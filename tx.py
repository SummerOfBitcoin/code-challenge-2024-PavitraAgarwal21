# making the intitial transaction object where we devide the transaction in the 
# Tx 
# TxIn 
# TxOut
from io import BytesIO
from usefulfunctions import int_to_little_endian , encode_varint  , SIGHASH_ALL ,hash256
from script import p2pkh_script, Script
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
        self._hash_prevouts = None
        self._hash_sequence = None
        self._hash_outputs = None
        
    def serialize(self):
            result = self.prev_tx[::-1] #little edian is the reverse 
            result += int_to_little_endian(self.prev_index, 4)
            result += self.script_sig.serialize() #script is also been serialize according to the rule 
            result += int_to_little_endian(self.sequence, 4)
            return result
    def value(self):
            return self.prevout.amount 

    def script_pubkey(self):
            return self.prevout.script_pubkey


         
class Tx:
    def __init__(self, version, tx_ins, tx_outs , locktime , segwit =None) :
        self.version = version
        self.tx_ins = tx_ins # this is may be the array of the TxIn
        self.tx_outs = tx_outs # this is may be the array of the aTxout
        self.locktime = locktime
        self.segwit = segwit # is this is segwit transaction or not 
        self._hash_prevouts = None #prevout transacation 
        self._hash_sequence = None 
        self._hash_outputs = None # all the output serialized hash 

    def id(self):
        return self.hash().hex() # txid 
    
    def wtxid(self) : # used to find the wxtid 
        return (hash256(self.serialize_segwit())[::-1]).hex() # used in the formation of the witness commitment 

    # tag::source5[]
    def hash256for(self) :
        return hash256(self.serialize_legacy())
    
    def hash(self):
        return hash256(self.serialize_legacy())[::-1]
# currently only serialixe the transaction using the 
    def serialize(self):
        # now there are two techniques of the seriliaztion
        if self.segwit:
            return self.serialize_segwit() #containing witness 
        else:
            return self.serialize_legacy()

    def serialize_legacy(self):  # this is using the seriliazation whihc does not containt the legacy 
        result = int_to_little_endian(self.version, 4) 
        result += encode_varint(len(self.tx_ins))
        for tx_in in self.tx_ins:
            result += tx_in.serialize()
        result += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            result += tx_out.serialize()
        result += int_to_little_endian(self.locktime, 4)
        return result
    
    def serialize_segwit(self):
        result = int_to_little_endian(self.version, 4)
        result += b'\x00\x01' # maker  flag 
        result += encode_varint(len(self.tx_ins))
        for tx_in in self.tx_ins:
            result += tx_in.serialize()
        result += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            result += tx_out.serialize()
        for tx_in in self.tx_ins:  
            result += int_to_little_endian(len(tx_in.witness), 1)
            for item in tx_in.witness: #witness transaction is added at the end 
                if type(item) == int:
                    result += int_to_little_endian(item, 1) 
                else:
                    result += encode_varint(len(item)) + (item)
        result += int_to_little_endian(self.locktime, 4)
        return result 
    
    def weightunit(self) : # here we find the wu from which we find the 
        if self.segwit :  
            # finding for the segwit transaction 
            result = len(int_to_little_endian(self.version, 4))*4
            result += len(b'\x00\x01')*1 # this is the segwit data 
            result += len(encode_varint(len(self.tx_ins)))*4 # non segwit data is * 4 times
            for tx_in in self.tx_ins:
                result += len(tx_in.serialize())*4
            result += len(encode_varint(len(self.tx_outs)))*4
            for tx_out in self.tx_outs:
                result += len(tx_out.serialize())*4
            for tx_in in self.tx_ins: 
                result += len(int_to_little_endian(len(tx_in.witness), 1))*1 # segwit data in 1 times
                for item in tx_in.witness:
                    if type(item) == int:
                        result += len(int_to_little_endian(item, 1))*1
                    else:
                        result += len(encode_varint(len(item)) + (item))*1
            result += len(int_to_little_endian(self.locktime, 4))*4
            return result 
        else :
            # finding for the legacy transaction 
            result = int_to_little_endian(self.version, 4)
            result += encode_varint(len(self.tx_ins))
            for tx_in in self.tx_ins:
                result += tx_in.serialize()
            result += encode_varint(len(self.tx_outs))
            for tx_out in self.tx_outs:
                result += tx_out.serialize()
            result += int_to_little_endian(self.locktime, 4)
            return len(result)*4
    
    def fee(self): # calculating the fees 
        ini, out = 0, 0 
        for tx_in in self.tx_ins:
            ini += tx_in.value()
        for tx_out in self.tx_outs:
            out += tx_out.amount
        return ini - out

    def sig_hash(self, input_index, redeem_script=None): # creating the sighash for each of the index 
        s = int_to_little_endian(self.version, 4)
        s += encode_varint(len(self.tx_ins))
        for i, tx_in in enumerate(self.tx_ins):
            if i == input_index:
                if redeem_script:
                    script_sig = redeem_script
                else:
                    script_sig = tx_in.script_pubkey()
            else:
                script_sig = None
            s += TxIn(
                prev_tx=tx_in.prev_tx,
                prev_index=tx_in.prev_index,
                script_sig=script_sig,
                sequence=tx_in.sequence,
                prevout=None , #as prevout information is not stored on the 
                witness=None, # witness is also not signed 
            ).serialize() # serilaize it 
        s += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            s += tx_out.serialize()
        s += int_to_little_endian(self.locktime, 4)
        s += int_to_little_endian(SIGHASH_ALL, 4)
        h256 = hash256(s) # 2 round of the sha256
        return int.from_bytes(h256, 'big') # this is able to create the message 
    
    
    
    def hash_prevouts(self):
        if self._hash_prevouts is None:
            allprevouts = b''
            allsequence = b''
            for tx_in in self.tx_ins:
                allprevouts += tx_in.prev_tx[::-1] + int_to_little_endian(tx_in.prev_index, 4)
                allsequence += int_to_little_endian(tx_in.sequence, 4)
            self._hash_prevouts = hash256(allprevouts)
            self._hash_sequence = hash256(allsequence)
        return self._hash_prevouts

    def hash_sequence(self):
        if self._hash_sequence is None:
            self.hash_prevouts()  
        return self._hash_sequence

    def hash_outputs(self): # output hash is finding out 
        if self._hash_outputs is None:
            all_outputs = b''
            for tx_out in self.tx_outs: # first creating and concate the all serialize txout 
                all_outputs += tx_out.serialize() #all the txn output is serialize
            self._hash_outputs = hash256(all_outputs) # then we hash the output hash only 
        return self._hash_outputs # return the hashpoutput 
    
    def segwit_hash(self, input_index, redeem_script=None, witness_script=None): #creating the message hash for the segwit transaction 
        tx_in = self.tx_ins[input_index]
        s = int_to_little_endian(self.version, 4)
        s += self.hash_prevouts() + self.hash_sequence()
        s += tx_in.prev_tx[::-1] + int_to_little_endian(tx_in.prev_index, 4)
        if witness_script:
            script_code = witness_script.serialize()
        elif redeem_script: # if reedem script is there means 
            script_code = p2pkh_script(redeem_script.cmds[1]).serialize()
        else:
            script_code = p2pkh_script(tx_in.script_pubkey().cmds[1]).serialize()
        s += script_code
        s += int_to_little_endian(tx_in.value(), 8)
        s += int_to_little_endian(tx_in.sequence, 4)
        s += self.hash_outputs() # output hash is calulcated
        s += int_to_little_endian(self.locktime, 4)
        s += int_to_little_endian(SIGHASH_ALL, 4) # assuming that all is signed 
        return int.from_bytes(hash256(s), 'big')
    
    def verify_input(self, input_index): # verify the transaction input signature by using the signature techniques 
        
        tx_in = self.tx_ins[input_index]
        script_pubkey = tx_in.script_pubkey() # this script_pubkey calls return prevout.script_pubkey 
        
        if script_pubkey.is_p2sh_script_pubkey():
            cmd = tx_in.script_sig.cmds[-1]
            raw_redeem = int_to_little_endian(len(cmd), 1) + cmd
            redeem_script = Script.parse(BytesIO(raw_redeem))
            if redeem_script.is_p2wpkh_script_pubkey():
                z = self.segwit_hash(input_index, redeem_script)
                witness = tx_in.witness
            elif redeem_script.is_p2wsh_script_pubkey():
                cmd = tx_in.witness[-1]
                raw_witness = encode_varint(len(cmd)) + cmd
                witness_script = Script.parse(BytesIO(raw_witness))
                z = self.segwit_hash(input_index, witness_script=witness_script)
                witness = tx_in.witness
            else:
                z = self.sig_hash(input_index, redeem_script)
                witness = None
        else:
            
            if script_pubkey.is_p2wpkh_script_pubkey():
                z = self.segwit_hash(input_index)
                witness = tx_in.witness
            elif script_pubkey.is_p2wsh_script_pubkey():
                cmd = tx_in.witness[-1]
                raw_witness = encode_varint(len(cmd)) + cmd
                witness_script = Script.parse(BytesIO(raw_witness))
                z = self.segwit_hash(input_index, witness_script=witness_script)
                witness = tx_in.witness
            else:
                z = self.sig_hash(input_index)
                witness = None
        combined = tx_in.script_sig + script_pubkey
        return combined.evaluate(z, witness)
    

    def verify(self): # verify each of the script_sig in the each input vin 
        for i in range(len(self.tx_ins)):
            if not self.verify_input(i):
                return False
        return True
        