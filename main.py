import json
from tx import Tx , TxIn , TxOut  
from script import Script 
from usefulfunctions import  int_to_little_endian , hash256 , sha256 , merkle_root , read_varint , encode_varint
from io import BytesIO
import os

from block import Block  
import random
from block import Block 
import time;
ts = time.time()
difficulty_target_hex = "0000ffff00000000000000000000000000000000000000000000000000000000"
base_block = '0000000000000000000000000000000000000000000000000000000000000000'

def nonce():
    random_bytes = [random.randint(0, 255) for _ in range(4)]
    hex_string = ''.join(format(byte, '02x') for byte in random_bytes)
    
    return hex_string

def wxcommitment(hash,val) :
    return hash256(hash + val)



def scripttype(cmds) :
    x = bytes.fromhex(cmds)
    xx = encode_varint(len(x))+x 
    sc = Script() 
    scps = sc.parse(s=BytesIO(xx))
    return scps
def witnessbyte(wits) :
    ans =[]
    for wit in wits :
        ans.append(bytes.fromhex(wit))
    return ans   


def little_endian_to_big_endian_txid(hex_str):
    # Split the input string into pairs of characters
    byte_pairs = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)]
    
    # Reverse the order of byte pairs to switch endianness
    reversed_byte_pairs = byte_pairs[::-1]
    
    # Reconstruct the string from reversed byte pairs
    big_endian_hex_str = ''.join(reversed_byte_pairs)
    
    return bytes.fromhex(big_endian_hex_str)

def big_endian_to_little_endian_txid(hex_str):
    # Split the input string into pairs of characters
    byte_pairs = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)]
    
    # Reverse the order of byte pairs to switch endianness
    reversed_byte_pairs = byte_pairs[::-1]
    
    # Reconstruct the string from reversed byte pairs
    little_endian_hex_str = ''.join(reversed_byte_pairs)
    
    return bytes.fromhex(little_endian_hex_str)





def initializeTxn(txex , segwitness) :
  version  = txex['version'] 
  locktime = txex['locktime']
  tx_ins= [] 
  tx_outs = []
  tx = Tx(
    version=version ,
    tx_ins=tx_ins ,
    tx_outs= tx_outs ,
    locktime=locktime ,
    segwit=segwitness,
  )
  for txin in txex['vin'] :
      vin = TxIn (
      prev_tx=bytes.fromhex(txin['txid']),
      prev_index= txin['vout'],
      prevout=TxOut(
              script_pubkey=scripttype(txin['prevout']['scriptpubkey']),      
              amount= txin['prevout']['value'],
                ),
      script_sig= None if txin['scriptsig'] == "" else scripttype(txin['scriptsig']),
      sequence = txin['sequence'],
      witness = witnessbyte(txin['witness']) if tx.segwit else None ,
      )
      tx_ins.append(vin) 
  for txout in txex['vout'] :
      vout = TxOut (
          script_pubkey = scripttype(txout['scriptpubkey']),
          amount=txout['value']
      )
      tx_outs.append(vout)
  return tx

wxtidcons = "0000000000000000000000000000000000000000000000000000000000000000"
wxtid = []
wxtid.append(wxtidcons)
txids =[]

correct = 0
error = 0 
totalfees = 0 
totalwu =0 
bitsize =0

script_directory = os.path.dirname(os.path.abspath(__file__))
directory =  os.path.join(script_directory, "checkpool")
for filename in os.listdir(directory):
  if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r') as file:
            txex = json.load(file)
        # if this json file contain the witness of not           
        segwitness = False 
        for vin in txex['vin'] :
          if 'witness' in vin:
            segwitness = True 
            break 
        flag = 0
        for vin in txex['vin'] :
          if vin['prevout']['scriptpubkey_type'] == 'v0_p2wsh' or vin['prevout']['scriptpubkey_type'] == 'v1_p2tr' :
            flag =1 
        if flag == 1 : continue 
        try :
          tx = initializeTxn(txex=txex , segwitness=segwitness)
          if totalwu >= 4000000 :
            break 
          if tx.verify() :
            # print(tx.id())
            txids.append(tx.id())
            if tx.segwit : 
              # print(tx.wtxid())
              wxtid.append(tx.wtxid())
            else :
              wxtid.append(tx.id())
            totalwu += tx.weightunit()
            totalfees += tx.fee()
        except Exception as e:
            continue

hashes = [bytes.fromhex(h)[::-1] for h in wxtid]
wxc = wxcommitment(merkle_root(hashes),bytes.fromhex(wxtidcons)).hex()
witnesscomitmentpubkeyscript = "6a24aa21a9ed"+wxc
# so let now create the coinbase transaction 
txin = [TxIn (
  prev_tx=bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000000"),
  prev_index=4294967295 ,
  script_sig=scripttype("47304402201f6e9296e322013f90f89433926509a9ff686ce91452679c82c921cf18257c95022027497b1354b4dce14b3e15d2372c69d6323ecfad9cbc0c8bb20d8d8d088fc22001210224c6633127ca04e9b678ae7d106a9828ba2aed9a402eefae69f52fbe7a065699"),
  sequence=4294967295 ,
  witness= witnessbyte(["0000000000000000000000000000000000000000000000000000000000000000"]),
  prevout=None 
)]
txout = [
  TxOut(
    amount=1250006517,
    script_pubkey = scripttype("76a914edf10a7fac6b32e24daa5305c723f3de58db1bc888ac")
  )
  ,
  TxOut(
    amount=0, # this is the wtxid commitment value 
    script_pubkey = scripttype(witnesscomitmentpubkeyscript),
  )
]
ctx = Tx (
  version = 1,
  tx_ins=txin, 
  tx_outs=txout,
  locktime=0,
  segwit=True
)


CoinbaseTxnSerialize = ctx.serialize().hex()
# print(CoinbaseTxnSerialize)
CoinbaseTxnId = ctx.id()  # this is our coinbase transaction  
txids.insert(0,CoinbaseTxnId)
# print(totalfees)
# print(totalwu)
# print(txids)



txinlittle = [little_endian_to_big_endian_txid(tx) for tx in txids] 
merklebigedian = big_endian_to_little_endian_txid(merkle_root(txinlittle).hex())

# print(little_endian_to_big_endian_txid(txids[0]).hex())
# print(big_endian_to_little_endian_txid(little_endian_to_big_endian_txid(txids[0]).hex()).hex())



block = Block (
  version = 0x20000002,
  prev_block= bytes.fromhex(base_block),
  merkle_root= merklebigedian ,
  timestamp= int(ts),
  bits=bytes.fromhex('1f00ffff'),
  nonce= bytes.fromhex(nonce()), #nonce()) , #nonce should be of the bytes 
  tx_hashes = txids 
)

cout = 0
blockid = ""
while True :
  block.nonce = bytes.fromhex(nonce())
  if block.hash() < bytes.fromhex(difficulty_target_hex) :
    blockid = block.hash()
    break 
  cout +=1 

Coinbase_txn_serialize = ctx.serialize().hex()
Coinbase_txn_id = ctx.id() 
block_header = block.serialize().hex()


txcount = "FD"+int_to_little_endian(len(txids)+1,2).hex()


script_directory = os.path.dirname(os.path.abspath(__file__))
output_file_path = os.path.join(script_directory, "output.txt")
with open(output_file_path, "w") as output_file:
    output_file.write("{}\n".format(block_header))  
    output_file.write("{}\n".format(Coinbase_txn_serialize))
    output_file.write("{}\n".format(txcount))
    for tx in txids :
      output_file.write("{}\n".format(tx))

