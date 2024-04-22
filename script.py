from usefulfunctions import int_to_little_endian , encode_varint , read_varint , little_endian_to_int

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