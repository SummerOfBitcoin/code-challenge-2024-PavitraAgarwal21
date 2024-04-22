# i am using the sample code where there is the op code mapping to reduce the workload and this is taken from the book 
from usefulfunctions import encode_num , decode_num , hash160 , hash256 , hashlib

from speck256k1 import S256Point , Signature

def op0(stack):
    stack.append(encode_num(0))
    return True


def op1negate(stack):
    stack.append(encode_num(-1))
    return True


def op1(stack):
    stack.append(encode_num(1))
    return True


def op2(stack):
    stack.append(encode_num(2))
    return True


def op3(stack):
    stack.append(encode_num(3))
    return True


def op4(stack):
    stack.append(encode_num(4))
    return True


def op5(stack):
    stack.append(encode_num(5))
    return True


def op6(stack):
    stack.append(encode_num(6))
    return True


def op7(stack):
    stack.append(encode_num(7))
    return True


def op8(stack):
    stack.append(encode_num(8))
    return True


def op9(stack):
    stack.append(encode_num(9))
    return True


def op10(stack):
    stack.append(encode_num(10))
    return True


def op11(stack):
    stack.append(encode_num(11))
    return True


def op12(stack):
    stack.append(encode_num(12))
    return True


def op13(stack):
    stack.append(encode_num(13))
    return True


def op14(stack):
    stack.append(encode_num(14))
    return True


def op15(stack):
    stack.append(encode_num(15))
    return True


def op16(stack):
    stack.append(encode_num(16))
    return True


def opnop(stack):
    return True


def opif(stack, items):
    if len(stack) < 1:
        return False
    good = []
    baad = []
    curarr = good
    found = False
    num_end_if_needed = 1
    while len(items) > 0:
        item = items.pop(0)
        if item in (99, 100):
            num_end_if_needed += 1
            curarr.append(item)
        elif num_end_if_needed == 1 and item == 103:
            curarr = baad
        elif item == 104:
            if num_end_if_needed == 1:
                found = True
                break
            else:
                num_end_if_needed -= 1
                curarr.append(item)
        else:
            curarr.append(item)
    if not found:
        return False
    element = stack.pop()
    if decode_num(element) == 0:
        items[:0] = baad
    else:
        items[:0] = good
    return True


def opnotif(stack, items):
    if len(stack) < 1:
        return False
    good = []
    baad = []
    curarr = good
    found = False
    num_end_if_needed = 1
    while len(items) > 0:
        item = items.pop(0)
        if item in (99, 100):
            num_end_if_needed += 1
            curarr.append(item)
        elif num_end_if_needed == 1 and item == 103:
            curarr = baad
        elif item == 104:
            if num_end_if_needed == 1:
                found = True
                break
            else:
                num_end_if_needed -= 1
                curarr.append(item)
        else:
            curarr.append(item)
    if not found:
        return False
    element = stack.pop()
    if decode_num(element) == 0:
        items[:0] = good
    else:
        items[:0] = baad
    return True


def opverify(stack):
    if len(stack) < 1:
        return False
    element = stack.pop()
    if decode_num(element) == 0:
        return False
    return True


def opreturn(stack):
    return False


def optoaltstack(stack, altstack):
    if len(stack) < 1:
        return False
    altstack.append(stack.pop())
    return True


def opfromaltstack(stack, altstack):
    if len(altstack) < 1:
        return False
    stack.append(altstack.pop())
    return True


def op2drop(stack):
    if len(stack) < 2:
        return False
    stack.pop()
    stack.pop()
    return True


def op2dup(stack):
    if len(stack) < 2:
        return False
    stack.extend(stack[-2:])
    return True


def op3dup(stack):
    if len(stack) < 3:
        return False
    stack.extend(stack[-3:])
    return True


def op2over(stack):
    if len(stack) < 4:
        return False
    stack.extend(stack[-4:-2])
    return True


def op2rot(stack):
    if len(stack) < 6:
        return False
    stack.extend(stack[-6:-4])
    return True


def op2swap(stack):
    if len(stack) < 4:
        return False
    stack[-4:] = stack[-2:] + stack[-4:-2]
    return True


def opifdup(stack):
    if len(stack) < 1:
        return False
    if decode_num(stack[-1]) != 0:
        stack.append(stack[-1])
    return True


def opdepth(stack):
    stack.append(encode_num(len(stack)))
    return True


def opdrop(stack):
    if len(stack) < 1:
        return False
    stack.pop()
    return True


def opdup(stack):
    if len(stack) < 1:
        return False
    stack.append(stack[-1])
    return True


def opnip(stack):
    if len(stack) < 2:
        return False
    stack[-2:] = stack[-1:]
    return True


def opover(stack):
    if len(stack) < 2:
        return False
    stack.append(stack[-2])
    return True


def oppick(stack):
    if len(stack) < 1:
        return False
    n = decode_num(stack.pop())
    if len(stack) < n + 1:
        return False
    stack.append(stack[-n - 1])
    return True


def oproll(stack):
    if len(stack) < 1:
        return False
    n = decode_num(stack.pop())
    if len(stack) < n + 1:
        return False
    if n == 0:
        return True
    stack.append(stack.pop(-n - 1))
    return True


def oprot(stack):
    if len(stack) < 3:
        return False
    stack.append(stack.pop(-3))
    return True


def opswap(stack):
    if len(stack) < 2:
        return False
    stack.append(stack.pop(-2))
    return True


def optuck(stack):
    if len(stack) < 2:
        return False
    stack.insert(-2, stack[-1])
    return True


def opsize(stack):
    if len(stack) < 1:
        return False
    stack.append(encode_num(len(stack[-1])))
    return True


def opequal(stack):
    if len(stack) < 2:
        return False
    element1 = stack.pop()
    element2 = stack.pop()
    if element1 == element2:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True


def opequalverify(stack):
    return opequal(stack) and opverify(stack)


def op1add(stack):
    if len(stack) < 1:
        return False
    element = decode_num(stack.pop())
    stack.append(encode_num(element + 1))
    return True


def op1sub(stack):
    if len(stack) < 1:
        return False
    element = decode_num(stack.pop())
    stack.append(encode_num(element - 1))
    return True


def opnegate(stack):
    if len(stack) < 1:
        return False
    element = decode_num(stack.pop())
    stack.append(encode_num(-element))
    return True


def opabs(stack):
    if len(stack) < 1:
        return False
    element = decode_num(stack.pop())
    if element < 0:
        stack.append(encode_num(-element))
    else:
        stack.append(encode_num(element))
    return True


def opnot(stack):
    if len(stack) < 1:
        return False
    element = stack.pop()
    if decode_num(element) == 0:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True


def op0notequal(stack):
    if len(stack) < 1:
        return False
    element = stack.pop()
    if decode_num(element) == 0:
        stack.append(encode_num(0))
    else:
        stack.append(encode_num(1))
    return True


def opadd(stack):
    if len(stack) < 2:
        return False
    element1 = decode_num(stack.pop())
    element2 = decode_num(stack.pop())
    stack.append(encode_num(element1 + element2))
    return True


def opsub(stack):
    if len(stack) < 2:
        return False
    element1 = decode_num(stack.pop())
    element2 = decode_num(stack.pop())
    stack.append(encode_num(element2 - element1))
    return True


def opbooland(stack):
    if len(stack) < 2:
        return False
    element1 = decode_num(stack.pop())
    element2 = decode_num(stack.pop())
    if element1 and element2:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True


def opboolor(stack):
    if len(stack) < 2:
        return False
    element1 = decode_num(stack.pop())
    element2 = decode_num(stack.pop())
    if element1 or element2:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True


def opnumequal(stack):
    if len(stack) < 2:
        return False
    element1 = decode_num(stack.pop())
    element2 = decode_num(stack.pop())
    if element1 == element2:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True


def opnumequalverify(stack):
    return opnumequal(stack) and opverify(stack)


def opnumnotequal(stack):
    if len(stack) < 2:
        return False
    element1 = decode_num(stack.pop())
    element2 = decode_num(stack.pop())
    if element1 == element2:
        stack.append(encode_num(0))
    else:
        stack.append(encode_num(1))
    return True


def oplessthan(stack):
    if len(stack) < 2:
        return False
    element1 = decode_num(stack.pop())
    element2 = decode_num(stack.pop())
    if element2 < element1:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True


def opgreaterthan(stack):
    if len(stack) < 2:
        return False
    element1 = decode_num(stack.pop())
    element2 = decode_num(stack.pop())
    if element2 > element1:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True


def oplessthanorequal(stack):
    if len(stack) < 2:
        return False
    element1 = decode_num(stack.pop())
    element2 = decode_num(stack.pop())
    if element2 <= element1:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True


def opgreaterthanorequal(stack):
    if len(stack) < 2:
        return False
    element1 = decode_num(stack.pop())
    element2 = decode_num(stack.pop())
    if element2 >= element1:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True


def opmin(stack):
    if len(stack) < 2:
        return False
    element1 = decode_num(stack.pop())
    element2 = decode_num(stack.pop())
    if element1 < element2:
        stack.append(encode_num(element1))
    else:
        stack.append(encode_num(element2))
    return True


def opmax(stack):
    if len(stack) < 2:
        return False
    element1 = decode_num(stack.pop())
    element2 = decode_num(stack.pop())
    if element1 > element2:
        stack.append(encode_num(element1))
    else:
        stack.append(encode_num(element2))
    return True


def opwithin(stack):
    if len(stack) < 3:
        return False
    maximum = decode_num(stack.pop())
    minimum = decode_num(stack.pop())
    element = decode_num(stack.pop())
    if element >= minimum and element < maximum:
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True


def opripemd160(stack):
    if len(stack) < 1:
        return False
    element = stack.pop()
    stack.append(hashlib.new('ripemd160', element).digest())
    return True


def opsha1(stack):
    if len(stack) < 1:
        return False
    element = stack.pop()
    stack.append(hashlib.sha1(element).digest())
    return True


def opsha256(stack):
    if len(stack) < 1:
        return False
    element = stack.pop()
    stack.append(hashlib.sha256(element).digest())
    return True


def ophash160(stack):
    if len(stack) < 1:
        return False
    element = stack.pop()
    h160 = hash160(element)
    stack.append(h160)
    return True


def ophash256(stack):
    if len(stack) < 1:
        return False
    element = stack.pop()
    stack.append(hash256(element))
    return True


def opchecksig(stack, z):
    if len(stack) < 2:
        return False
    secpubkey = stack.pop()
    dersignature = stack.pop()[:-1]
    try:
        point = S256Point.parse(secpubkey)
        sig = Signature.parse(dersignature)
    except (ValueError, SyntaxError) as e:
        return False
    if point.verify(z, sig):
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    return True


def opchecksigverify(stack, z):
    return opchecksig(stack, z) and opverify(stack)


def opcheckmultisig(stack, z):
    if len(stack) < 1:
        return False
    n = decode_num(stack.pop())
    if len(stack) < n + 1:
        return False
    sec_pub_keys = []
    for _ in range(n):
        sec_pub_keys.append(stack.pop())
    m = decode_num(stack.pop())
    if len(stack) < m + 1:
        return False
    der_sig = []
    for _ in range(m):
        # signature is assumed to be using SIGHASHALL
        der_sig.append(stack.pop()[:-1])
    stack.pop()
    try:
        points = [S256Point.parse(sec) for sec in sec_pub_keys]
        sigs = [Signature.parse(der) for der in der_sig]
        for sig in sigs:
            if len(points) == 0:
                return False
            while points:
                point = points.pop(0)
                if point.verify(z, sig):
                    break
        stack.append(encode_num(1))
    except (ValueError, SyntaxError):
        return False
    return True


def opcheckmultisigverify(stack, z):
    return opcheckmultisig(stack, z) and opverify(stack)


def opchecklocktimeverify(stack, locktime, sequence):
    if sequence == 0xffffffff:
        return False
    if len(stack) < 1:
        return False
    element = decode_num(stack[-1])
    if element < 0:
        return False
    if element < 500000000 and locktime > 500000000:
        return False
    if locktime < element:
        return False
    return True


def opchecksequenceverify(stack, version, sequence):
    if sequence & (1 << 31) == (1 << 31):
        return False
    if len(stack) < 1:
        return False
    element = decode_num(stack[-1])
    if element < 0:
        return False
    if element & (1 << 31) == (1 << 31):
        if version < 2:
            return False
        elif sequence & (1 << 31) == (1 << 31):
            return False
        elif element & (1 << 22) != sequence & (1 << 22):
            return False
        elif element & 0xffff > sequence & 0xffff:
            return False
    return True


OPCODEFUNCTIONS = {
    0: op0,
    79: op1negate,
    81: op1,
    82: op2,
    83: op3,
    84: op4,
    85: op5,
    86: op6,
    87: op7,
    88: op8,
    89: op9,
    90: op10,
    91: op11,
    92: op12,
    93: op13,
    94: op14,
    95: op15,
    96: op16,
    97: opnop,
    99: opif,
    100: opnotif,
    105: opverify,
    106: opreturn,
    107: optoaltstack,
    108: opfromaltstack,
    109: op2drop,
    110: op2dup,
    111: op3dup,
    112: op2over,
    113: op2rot,
    114: op2swap,
    115: opifdup,
    116: opdepth,
    117: opdrop,
    118: opdup,
    119: opnip,
    120: opover,
    121: oppick,
    122: oproll,
    123: oprot,
    124: opswap,
    125: optuck,
    130: opsize,
    135: opequal,
    136: opequalverify,
    139: op1add,
    140: op1sub,
    143: opnegate,
    144: opabs,
    145: opnot,
    146: op0notequal,
    147: opadd,
    148: opsub,
    154: opbooland,
    155: opboolor,
    156: opnumequal,
    157: opnumequalverify,
    158: opnumnotequal,
    159: oplessthan,
    160: opgreaterthan,
    161: oplessthanorequal,
    162: opgreaterthanorequal,
    163: opmin,
    164: opmax,
    165: opwithin,
    166: opripemd160,
    167: opsha1,
    168: opsha256,
    169: ophash160,
    170: ophash256,
    172: opchecksig,
    173: opchecksigverify,
    174: opcheckmultisig,
    175: opcheckmultisigverify,
    176: opnop,
    177: opchecklocktimeverify,
    178: opchecksequenceverify,
    179: opnop,
    180: opnop,
    181: opnop,
    182: opnop,
    183: opnop,
    184: opnop,
    185: opnop,
}

OPCODENAMES = {
    0: 'OP0',
    76: 'OPPUSHDATA1',
    77: 'OPPUSHDATA2',
    78: 'OPPUSHDATA4',
    79: 'OP1NEGATE',
    81: 'OP1',
    82: 'OP2',
    83: 'OP3',
    84: 'OP4',
    85: 'OP5',
    86: 'OP6',
    87: 'OP7',
    88: 'OP8',
    89: 'OP9',
    90: 'OP10',
    91: 'OP11',
    92: 'OP12',
    93: 'OP13',
    94: 'OP14',
    95: 'OP15',
    96: 'OP16',
    97: 'OPNOP',
    99: 'OPIF',
    100: 'OPNOTIF',
    103: 'OPELSE',
    104: 'OPENDIF',
    105: 'OPVERIFY',
    106: 'OPRETURN',
    107: 'OPTOALTSTACK',
    108: 'OPFROMALTSTACK',
    109: 'OP2DROP',
    110: 'OP2DUP',
    111: 'OP3DUP',
    112: 'OP2OVER',
    113: 'OP2ROT',
    114: 'OP2SWAP',
    115: 'OPIFDUP',
    116: 'OPDEPTH',
    117: 'OPDROP',
    118: 'OPDUP',
    119: 'OPNIP',
    120: 'OPOVER',
    121: 'OPPICK',
    122: 'OPROLL',
    123: 'OPROT',
    124: 'OPSWAP',
    125: 'OPTUCK',
    130: 'OPSIZE',
    135: 'OPEQUAL',
    136: 'OPEQUALVERIFY',
    139: 'OP1ADD',
    140: 'OP1SUB',
    143: 'OPNEGATE',
    144: 'OPABS',
    145: 'OPNOT',
    146: 'OP0NOTEQUAL',
    147: 'OPADD',
    148: 'OPSUB',
    154: 'OPBOOLAND',
    155: 'OPBOOLOR',
    156: 'OPNUMEQUAL',
    157: 'OPNUMEQUALVERIFY',
    158: 'OPNUMNOTEQUAL',
    159: 'OPLESSTHAN',
    160: 'OPGREATERTHAN',
    161: 'OPLESSTHANOREQUAL',
    162: 'OPGREATERTHANOREQUAL',
    163: 'OPMIN',
    164: 'OPMAX',
    165: 'OPWITHIN',
    166: 'OPRIPEMD160',
    167: 'OPSHA1',
    168: 'OPSHA256',
    169: 'OPHASH160',
    170: 'OPHASH256',
    171: 'OPCODESEPARATOR',
    172: 'OPCHECKSIG',
    173: 'OPCHECKSIGVERIFY',
    174: 'OPCHECKMULTISIG',
    175: 'OPCHECKMULTISIGVERIFY',
    176: 'OPNOP1',
    177: 'OPCHECKLOCKTIMEVERIFY',
    178: 'OPCHECKSEQUENCEVERIFY',
    179: 'OPNOP4',
    180: 'OPNOP5',
    181: 'OPNOP6',
    182: 'OPNOP7',
    183: 'OPNOP8',
    184: 'OPNOP9',
    185: 'OPNOP10',
}
