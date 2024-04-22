from usefulfunctions import int_to_little_endian , encode_varint , read_varint , sha256, little_endian_to_int , h160_to_p2pkh_address , h160_to_p2sh_address 
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

class Script:

    def __init__(self, cmds=None):
        if cmds is None:
            self.cmds = []
        else:
            self.cmds = cmds

    def parse(cls, s):
        length = read_varint(s)
        cmds = []
        count = 0
        while count < length:
            current = s.read(1)
            count += 1
            currbyte = current[0]
            if currbyte >= 1 and currbyte <= 75:
                n = currbyte
                cmds.append(s.read(n))
                count += n
            elif currbyte == 76:
                l = little_endian_to_int(s.read(1))
                cmds.append(s.read(l))
                count += l + 1
            elif currbyte == 77:
                l = little_endian_to_int(s.read(2))
                cmds.append(s.read(l))
                count += l + 2
            else:
                op_code = currbyte
                cmds.append(op_code)
        if count != length:
            raise SyntaxError('parsing script failed')
        return cls(cmds)


    def serialize(self):
        r = b''
        for cmd in self.cmds:
            if type(cmd) == int:
                r += int_to_little_endian(cmd, 1)
            else:
                length = len(cmd)
                if length < 75:
                    r += int_to_little_endian(length, 1)
                elif length > 75 and length < 0x100:
                    r += int_to_little_endian(76, 1)
                    r += int_to_little_endian(length, 1)
                elif length >= 0x100 and length <= 520:
                    r += int_to_little_endian(77, 1)
                    r += int_to_little_endian(length, 2)
                else:
                    raise ValueError('cmd is not correct file script.py serialization of script ')
                r += cmd    
            r = encode_varint(len(r)) + r  
        return r
    def evaluate(self, z, witness):
        cmds = self.cmds[:]
        stack = []
        altstack = []
        while len(cmds) > 0:
            cmd = cmds.pop(0)
            if type(cmd) == int:
                operation = OPCODEFUNCTIONS[cmd]
                if cmd in (99, 100):
                    if not operation(stack, cmds):
                        return False
                elif cmd in (107, 108):
                    if not operation(stack, altstack):
                        return False
                elif cmd in (172, 173, 174, 175):

                    if not operation(stack, z):
                        return False
                else:
                    if not operation(stack):
                        return False
            else:
                stack.append(cmd)
                if len(cmds) == 3 and cmds[0] == 0xa9 \
                    and type(cmds[1]) == bytes and len(cmds[1]) == 20 \
                    and cmds[2] == 0x87:
                    redeem_script = encode_varint(len(cmd)) + cmd
                    cmds.pop()
                    h160 = cmds.pop()
                    cmds.pop()
                    if not ophash160(stack):
                        return False
                    stack.append(h160)
                    if not opequal(stack):
                        return False
                    if not opverify(stack):
                        return False
                    redeem_script = encode_varint(len(cmd)) + cmd
                    stream = BytesIO(redeem_script)
                    cmds.extend(Script.parse(stream).cmds)
                if len(stack) == 2 and stack[0] == b'' and len(stack[1]) == 20: 
                    h160 = stack.pop()
                    stack.pop()
                    cmds.extend(witness)
                    cmds.extend(p2pkh_script(h160).cmds)
                if len(stack) == 2 and stack[0] == b'' and len(stack[1]) == 32:
                    s256 = stack.pop()  
                    stack.pop()  
                    cmds.extend(witness[:-1])
                    witness_script = witness[-1]  
                    if s256 != sha256(witness_script):
                        print('bad sha256 {} vs {}'.format
                            (s256.hex(), sha256(witness_script).hex()))
                        return False
                    stream = BytesIO(encode_varint(len(witness_script)) 
                        + witness_script)
                    witness_script_cmds = Script.parse(stream).cmds 
                    cmds.extend(witness_script_cmds)
        if len(stack) == 0:
            return False
        if stack.pop() == b'':
            return False
        return True
    # checking the what type of the script it is 
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

