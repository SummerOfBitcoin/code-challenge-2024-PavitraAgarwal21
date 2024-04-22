# making the intitial transaction object where we devide the transaction in the 
# Tx 
# TxIn 
# TxOut 
from usefulfunctions import int_to_little_endian , encode_varint 
    
class TxOut:
    #this is the basic frame of the
    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey
    
    def serialize(self):
        result = int_to_little_endian(self.amount, 8) # amount in the bitcoin is the 8 bytes 
        result += self.script_pubkey.serialize() # script pubkey is also been seraliaze 
        return result

     
# currently script is not implemented 
class TxIn : 
    def __init__(self, prev_tx, prev_index,sequence,prevout,witness = None ,script_sig = None):
        self.prev_tx = prev_tx
        self.prev_index = prev_index
        if script_sig is None: # if the witness is there then this is "" so i set it to the none 
            self.script_sig = Script() # to initialize it in the case of the 
        else:
            self.script_sig = script_sig 
        self.sequence = sequence
        self.witness = witness 
        self.prevout = prevout  # contain the vout info of the spend utxo this is of the type Txout
        
        def serialize(self):
            result = self.prev_tx[::-1] #little edian is the reverse 
            result += int_to_little_endian(self.prev_index, 4)
            result += self.script_sig.serialize() #script is also been serialize according to the rule 
            result += int_to_little_endian(self.sequence, 4)
            return result

         
class Tx:
    def __init__(self, version, tx_ins, tx_outs , locktime , segwit =None) :
        self.version = version
        self.tx_ins = tx_ins # this is may be the array of the TxIn
        self.tx_outs = tx_outs # this is may be the array of the aTxout
        self.locktime = locktime
        self.segwit = segwit # is this is segwit transaction or not 

# currently only serialixe the transaction using the 
    def serialize(self): 
        result = int_to_little_endian(self.version, 4) # version is in little edian
        result += encode_varint(len(self.tx_ins)) # no of inpout is variant so that it can represent in > 4byte representation 
        for tx_in in self.tx_ins:
            result += tx_in.serialize() # defining the serialization of the input 
        result += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs: 
            result += tx_out.serialize() # defining the serialization of the output 
        result += int_to_little_endian(self.locktime, 4)
        return result


        