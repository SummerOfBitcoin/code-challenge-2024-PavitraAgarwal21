from usefulfunctions import int_to_little_endian , encode_varint , read_varint , little_endian_to_int , h160_to_p2pkh_address , h160_to_p2sh_address 


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

