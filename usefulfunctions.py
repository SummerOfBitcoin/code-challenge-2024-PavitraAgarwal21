
def int_to_little_endian(n, length): # converting the int into the little edian format 
    return n.to_bytes(length, 'little') 

# encode  a variant which can represent the number over their bytes represntation 
def encode_varint(i):
    if i < 0xfd:
        return bytes([i])
    elif i < 0x10000:
        return b'\xfd' + int_to_little_endian(i, 2)
    elif i < 0x100000000:
        return b'\xfe' + int_to_little_endian(i, 4)
    elif i < 0x10000000000000000:
        return b'\xff' + int_to_little_endian(i, 8)
