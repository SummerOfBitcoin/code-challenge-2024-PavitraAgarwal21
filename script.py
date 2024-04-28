from usefulfunctions import int_to_little_endian , encode_varint , read_varint , decode_base58,sha256, little_endian_to_int , h160_to_p2pkh_address , h160_to_p2sh_address 
from op import opequal, ophash160, opverify, OPCODEFUNCTIONS, OPCODENAMES
from io import BytesIO
def p2pkh_script(h160): 
    return Script([0x76, 0xa9, h160, 0x88, 0xac])
def p2sh_script(h160):
    return Script([0xa9, h160, 0x87])
def p2wpkh_script(h160):
    return Script([0x00, h160]) 
def p2wsh_script(h256):
    return Script([0x00, h256]) 
def p2pkh_script(h160):
    return Script([0x76, 0xa9, h160, 0x88, 0xac])
def p2sh_script(h160):
    return Script([0xa9, h160, 0x87])
def p2wpkh_script(h160):
    return Script([0x00, h160])  # <1>
def p2wsh_script(h256):
    return Script([0x00, h256]) 




class Script:

    def __init__(self, cmds=None):
        if cmds is None:
            self.cmds = []
        else:
            self.cmds = cmds

    def __repr__(self):
        result = []
        for cmd in self.cmds:
            if type(cmd) == int:
                if OPCODENAMES.get(cmd):
                    name = OPCODENAMES.get(cmd)
                else:
                    name = 'OP[{}]'.format(cmd)
                result.append(name)
            else:
                result.append(cmd.hex())
        return ' '.join(result)

    def __add__(self, other):
        return Script(self.cmds + other.cmds)

    @classmethod
    def parse(cls, s):
        # get the length of the entire field
        length = read_varint(s)
        # initialize the cmds array
        cmds = []
        # initialize the number of bytes we've read to 0
        count = 0
        # loopuntil we've read length bytes
        while count < length:
            # get the current byte
            current = s.read(1)
            # increment the bytes we've read
            count += 1
            # convert the current byte to an integer
            current_byte = current[0]
            # if the current byte is between 1 and 75 inclusive
            if current_byte >= 1 and current_byte <= 75:
                # we have an cmd set n to be the current byte
                n = current_byte
                # add the next n bytes as an cmd
                cmds.append(s.read(n))
                count += n
            elif current_byte == 76:
                # oppushdata1
                data_length = little_endian_to_int(s.read(1))
                cmds.append(s.read(data_length))
                count += data_length + 1
            elif current_byte == 77:
                # oppushdata2
                data_length = little_endian_to_int(s.read(2))
                cmds.append(s.read(data_length))
                count += data_length + 2
            else:
                # we have an opode. set the current byte to opcode
                opcode = current_byte
                # add the opcode to the list of cmds
                cmds.append(opcode)
        if count != length:
            raise SyntaxError('parsing script failed')
        return cls(cmds)

    def raw_serialize(self):
        result = b''
        for cmd in self.cmds:
            if type(cmd) == int:
                result += int_to_little_endian(cmd, 1)
            else:
                length = len(cmd)
                if length < 75:
                    result += int_to_little_endian(length, 1)
                elif length > 75 and length < 0x100:
                    result += int_to_little_endian(76, 1)
                    result += int_to_little_endian(length, 1)
                elif length >= 0x100 and length <= 520:
                    result += int_to_little_endian(77, 1)
                    result += int_to_little_endian(length, 2)
                else:
                    raise ValueError('too long an cmd')
                result += cmd
        return result

    def serialize(self):
        # get the raw serialization (no prepended length)
        result = self.raw_serialize()
        # get the length of the whole thing
        total = len(result)
        # encode_varint the total length of the result and prepend
        return encode_varint(total) + result

    def evaluate(self, z, witness):
        # create a cop as we may need to add to this list if we have a
        # RedeemScript
        cmds = self.cmds[:]
        stack = []
        altstack = []
        while len(cmds) > 0:
            cmd = cmds.pop(0)
            if type(cmd) == int:
                # do what the opode says
                opration = OPCODEFUNCTIONS[cmd]
                if cmd in (99, 100):
                    # opif/opnotif require the cmds array
                    if not opration(stack, cmds):
                        return False
                elif cmd in (107, 108):
                    # optoaltstack/opfromaltstack require the altstack
                    if not opration(stack, altstack):
                        return False
                elif cmd in (172, 173, 174, 175):
                    # these are signing oprations, they need a sig_hash
                    # to check against
                    if not opration(stack, z):
                        return False
                else:
                    if not opration(stack):
                        return False
            else:
                # add the cmd to the stack
                stack.append(cmd)
                # p2sh rule. if the next three cmds are:
                # OPHASH160 <20 byte hash> OPEQUAL this is the RedeemScript
                # OPHASH160 == 0xa9 and OPEQUAL == 0x87
                if len(cmds) == 3 and cmds[0] == 0xa9 \
                    and type(cmds[1]) == bytes and len(cmds[1]) == 20 \
                    and cmds[2] == 0x87:
                    redeem_script = encode_varint(len(cmd)) + cmd
                    # we execute the next three opodes
                    cmds.pop()
                    h160 = cmds.pop()
                    cmds.pop()
                    if not ophash160(stack):
                        return False
                    stack.append(h160)
                    if not opequal(stack):
                        return False
                    # final result should be a 1
                    if not opverify(stack):
                        return False
                    # hashes match! now add the RedeemScript
                    redeem_script = encode_varint(len(cmd)) + cmd
                    stream = BytesIO(redeem_script)
                    cmds.extend(Script.parse(stream).cmds)
                # witness program version 0 rule. if stack cmds are:
                # 0 <20 byte hash> this is p2wpkh
                # tag::source3[]
                if len(stack) == 2 and stack[0] == b'' and len(stack[1]) == 20:  # <1>
                    h160 = stack.pop()
                    stack.pop()
                    cmds.extend(witness)
                    cmds.extend(p2pkh_script(h160).cmds)
                # end::source3[]
                # witness program version 0 rule. if stack cmds are:
                # 0 <32 byte hash> this is p2wsh
                # tag::source6[]
                if len(stack) == 2 and stack[0] == b'' and len(stack[1]) == 32:
                    s256 = stack.pop() 
                    stack.pop()
                    cmds.extend(witness[:-1])  # <3>
                    witness_script = witness[-1]  # <4>
                    if s256 != sha256(witness_script):  # <5>
                        print('bad sha256 {} vs {}'.format
                            (s256.hex(), sha256(witness_script).hex()))
                        return False
                    stream = BytesIO(encode_varint(len(witness_script)) 
                        + witness_script)
                    witness_script_cmds = Script.parse(stream).cmds  # <6>
                    cmds.extend(witness_script_cmds)
                # end::source6[]
        if len(stack) == 0:
            return False
        if stack.pop() == b'':
            return False
        return True

    def is_p2pkh_script_pubkey(self):

        return len(self.cmds) == 5 and self.cmds[0] == 0x76 \
            and self.cmds[1] == 0xa9 \
            and type(self.cmds[2]) == bytes and len(self.cmds[2]) == 20 \
            and self.cmds[3] == 0x88 and self.cmds[4] == 0xac

    def is_p2sh_script_pubkey(self):
        return len(self.cmds) == 3 and self.cmds[0] == 0xa9 \
            and type(self.cmds[1]) == bytes and len(self.cmds[1]) == 20 \
            and self.cmds[2] == 0x87

    def is_p2wpkh_script_pubkey(self): 
        return len(self.cmds) == 2 and self.cmds[0] == 0x00 \
            and type(self.cmds[1]) == bytes and len(self.cmds[1]) == 20

    def is_p2wsh_script_pubkey(self):
        return len(self.cmds) == 2 and self.cmds[0] == 0x00 \
            and type(self.cmds[1]) == bytes and len(self.cmds[1]) == 32

    def address(self, testnet=False):
        if self.is_p2pkh_script_pubkey():
            h160 = self.cmds[2]
            return h160_to_p2pkh_address(h160, testnet)
        elif self.is_p2sh_script_pubkey():
            h160 = self.cmds[1]
            return h160_to_p2sh_address(h160, testnet)
        raise ValueError('Unknown ScriptPubKey')
    