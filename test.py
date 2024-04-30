txid = [
    "f2078834eef50608d4ffac7dc27525e7152c1f42d447ff108ffa8beea8863995",
    "c215ec630ea97b31bb2eee817f1541191aa1b1473b586399c0e8695077d82e68"
]
from usefulfunctions import merkle_root
def little_endian_to_big_endian_txid(hex_str):
    # Split the input string into pairs of characters
    byte_pairs = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)]
    
    # Reverse the order of byte pairs to switch endianness
    reversed_byte_pairs = byte_pairs[::-1]
    
    # Reconstruct the string from reversed byte pairs
    big_endian_hex_str = ''.join(reversed_byte_pairs)
    
    return bytes.fromhex(big_endian_hex_str)

def big_endian_to_little_endia_txid(hex_str):
    # Split the input string into pairs of characters
    byte_pairs = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)]
    
    # Reverse the order of byte pairs to switch endianness
    reversed_byte_pairs = byte_pairs[::-1]
    
    # Reconstruct the string from reversed byte pairs
    little_endian_hex_str = ''.join(reversed_byte_pairs)
    
    return bytes.fromhex(little_endian_hex_str)




txinlittle = [little_endian_to_big_endian_txid(tx) for tx in txid] 
print((merkle_root(txinlittle).hex()))

# print(little_endian_to_big_endian_txid(txid[0]).hex())
# print(big_endian_to_little_endia_txid(little_endian_to_big_endian_txid(txid[0]).hex()).hex())
