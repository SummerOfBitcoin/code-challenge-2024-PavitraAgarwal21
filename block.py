from usefulfunctions import int_to_little_endian , hash256 , little_endian_to_int
class Block:

    def __init__(self, version, prev_block, merkle_root,
                 timestamp, bits, nonce, tx_hashes=None):
        self.version = version
        self.prev_block = prev_block
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = nonce
        self.tx_hashes = tx_hashes
        
    @classmethod  
    def parse(cls, s):
        '''Takes a byte stream and parses a block. Returns a Block object'''
        # s.read(n) will read n bytes from the stream
        # version - 4 bytes, little endian, interpret as int
        version = little_endian_to_int(s.read(4))
        # prev_block - 32 bytes, little endian (use [::-1] to reverse)
        prev_block = s.read(32)[::-1]
        # merkle_root - 32 bytes, little endian (use [::-1] to reverse)
        merkle_root = s.read(32)[::-1]
        # timestamp - 4 bytes, little endian, interpret as int
        timestamp = little_endian_to_int(s.read(4))
        # bits - 4 bytes
        bits = s.read(4)
        # nonce - 4 bytes
        nonce = s.read(4)
        # initialize class
        return cls(version, prev_block, merkle_root, timestamp, bits, nonce)


    def serialize(self):
        result = int_to_little_endian(self.version, 4)
        result += self.prev_block[::-1]
        result += self.merkle_root
        result += int_to_little_endian(self.timestamp, 4)
        result += self.bits[::-1]
        result += self.nonce[::-1]
        return result
    
    def hash(self):
        '''Returns the hash256 interpreted little endian of the block'''
        # serialize
        s = self.serialize()
        # hash256
        h256 = hash256(s)
        # reverse
        return h256[::-1]