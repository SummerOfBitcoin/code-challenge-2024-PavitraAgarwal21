# making the intitial transaction object where we devide the transaction in the 
# Tx 
# TxIn 
# TxOut 

class TxOut:
    #this is the basic frame of the
    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey
     
 
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
         
class Tx:
    def __init__(self, version, tx_ins, tx_outs , locktime , segwit =None) :
        self.version = version
        self.tx_ins = tx_ins # this is may be the array of the TxIn
        self.tx_outs = tx_outs # this is may be the array of the aTxout
        self.locktime = locktime
        self.segwit = segwit # is this is segwit transaction or not 
        

        

        