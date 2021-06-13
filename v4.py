# From mk4
import struct
import pickle
from Word import Word
import re
import binascii

_REFERENCES_ = {}
_INV_DEP_ = {}
_COST_ = {}
_DEPENDENCY_ = {}
prog = re.compile( r"^([\^\~\&\|])\((\w+),?(\w+)?\)$" )

def getDependencies(op):
    m= prog.search(op)
    ref1 = m.group(2)
    ref2 = m.group(3)
    dep=[]
    if( ref1!=None and ref1[0]=='r'):
            dep.append(ref1)
    if( ref2!=None and ref2[0]=='r'):
            dep.append(ref2)
    return dep

def getRef(val):
    global _COST_
    global _REFERENCES_
    global _DEPENDENCY_
    global _INV_DEP_
    if val not in _REFERENCES_:
        newRef = 'r'+str(len(_REFERENCES_))
        _REFERENCES_[ val ] = newRef
        depends = getDependencies( val )
        _DEPENDENCY_[newRef] = depends
        for r in depends:
            if( r not in _INV_DEP_): _INV_DEP_[r] = []
            _INV_DEP_[r].append(newRef)
        # _COST_[newRef] = reduce(max,map(lambda x: _COST_[x],depends),0)+1
        # print(f'! {depends}', _COST_)
        _COST_[newRef] = 1 if len(depends) == 0 else max([_COST_[x] for x in depends])+1
        return newRef
    else:
        return _REFERENCES_[ val ]

_k = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
      0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
      0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
      0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
      0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
      0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
      0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
      0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
      0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
      0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
      0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
      0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
      0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
      0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
      0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
      0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

_h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
      0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]

_h = [Word(list((bin(x)[2:].zfill(32).replace('0','f')).replace('1','t'))) for x in _h]
_k = [Word(list((bin(x)[2:].zfill(32).replace('0','f')).replace('1','t'))) for x in _k]

# XOR Returns ^(a,b) bits, and simplifies if possible.
def xor(a, b):
    if (a == 't' and b=='t') or (a == 'f' and b=='f'):
        return 'f'
    elif(a == 'f' and b=='t') or (a == 't' and b=='f'):
        return 't'
    elif(a == 'f'):
        return b
    elif(a == 't'):
        return getRef("~("+b+")")
    elif(b == 'f'):
        return a
    elif(b == 't'):
        return getRef("~("+a+")")
    return getRef("^("+a+","+b+")")

# AND Returns &(a,b) bits, and simplifies if possible.
def an(a, b):
    if( a =='f' or b=='f'):
        return 'f'
    elif( (a =='t' and b=='t') ):
        return 't'
    elif( a=='t'):
        return b
    elif( b=='t'):
        return a
    return getRef("&("+a+","+b+")")

# OR Returns |(a,b) bits, and simplifies if possible
def o(a, b):
    if( a == 't' or b=='t'):
        return 't'
    elif( (a =='f' or a=='t') and (b=='t' or b=='f') ):
        return 'f'
    elif( a=='f'):
        return b
    elif( b=='f'):
        return a
    return getRef("|("+a+","+b+")")

# NOT Returns ~(a), or the reverse of the bit if known
def flip(a):
    if( a == 't' ):
        return 'f'
    if( a == 'f' ):
        return 't'
    return getRef("~("+a+")")

# XOR 32 bits 
def xorWords( wordA, wordB ):
    res = [None]*32
    for i in range(32):
        res[i] = xor(wordA[i],wordB[i])
    return res

# AND 32 bits
def andWords( wordA, wordB ):
    res = [None] * 32
    for i in range(32):
        res[i] = an(wordA[i], wordB[i])
    return Word(res)

# OR 32 bits
def orWords( wordA, wordB ):
	res = [None] * 32
	for i in range(32):
		res[i] = o(wordA[i], wordB[i])
	return Word(res)

# NOT 32 bits
def flipWord( wordA ):
	res = [None] * 32
	for i in range(32):
		res[i] = flip(wordA[i])
	return Word(res)

# + 32 bits
def addWords(a, b, q=32):
    a=a[::-1]
    b=b[::-1]
    res = []
    for i in range(q):
        if(i == 0):
            res.append( xor( a[i] , b[i] ) )
        else:
            res.append( xor( xor( a[i] , b[i] ) , carry(a,b,i-1) ) )
    return Word(res[::-1])

# Carry a bit
def carry(a, b, at):
    if( at < 0):
        raise Exception("Do not need to carry on 1st")
        return '0'
    if (at != 0):
        return o( an(a[at], b[at]) , an(xor(a[at], b[at]),carry(a,b,at-1)) )
    return an(a[at], b[at])

# SHA 256
def sha256( c ):
    global _h,_k
    # Creating 32bits (4bytes) words with the bytes
    w=[None]*64
    i=0
    while len(c) >= 32 :
        w[i] = Word(c[:32])
        c=c[32:]
        i+=1

    for i in range(16,64):
        print(i)
        s0 = xorWords(xorWords( w[i-15].rotateRight(7) , w[i-15].rotateRight(18) ) , w[i-15].shiftRight(3))
        s1 = xorWords(xorWords( w[i-2].rotateRight(17) , w[i-2].rotateRight(19) ) , w[i-2].shiftRight(10))
        w[i] = addWords( addWords(s0,w[i-16]) , addWords(w[i-7] ,s1) )
        #w[i].simplify()

    a,b,c,d,e,f,g,h = _h

    for i in range(64):
        #s0 = self._rotr(a, 2) ^ self._rotr(a, 13) ^ self._rotr(a, 22)
        s0 = xorWords(xorWords( a.rotateRight(2) , a.rotateRight(13) ) , a.rotateRight(22))
        #maj = (a & b) ^ (a & c) ^ (b & c)
        maj = xorWords(xorWords(andWords(a,b) , andWords(a,c)) , andWords(b,c))
        #t2 = s0 + maj
        t2 = addWords(s0,maj)
        #s1 = self._rotr(e, 6) ^ self._rotr(e, 11) ^ self._rotr(e, 25)
        s1 = xorWords(xorWords(e.rotateRight(6),e.rotateRight(11)), e.rotateRight(25))
        #ch = (e & f) ^ ((~e) & g)
        ch = xorWords(andWords(e,f) , andWords( flipWord(e) , g))
        #t1 = h + s1 + ch + self._k[i] + w[i]
        #t1 = addWords(addWords(h , s1) , addWords(addWords(ch , _k[i]) , w[i]))
        print(_k[i])
        yy = addWords(ch , _k[i])
        xx = addWords(yy , w[i])
        t1 = addWords(addWords(h , s1) , xx)

        h = g
        g = f
        f = e
        e = addWords(d , t1)
        d = c
        c = b
        b = a
        a = addWords(t1 , t2)

    _h = [addWords(x,y) for x,y in zip(_h, [a,b,c,d,e,f,g,h])]


def getResult ():
    total = []
    for i in _h:
        for b in i:
            total.append(b)
    return total

def preprocess( ):
    size = 40
    # Taking a file
    input_file = '/tmp/my_file.txt'
    # Prepending 8 bits that can be modified at will. This acts as our NONCE
    fakeMessage = [ f'b{i}' for i in range(1 * 8)]
    # Loading a random text file
    with open(input_file, 'rb') as file:
        file_bits = str(binascii.hexlify(file.read()),'ascii')
        fakeMessage += createBits(file_bits)

    print ( fakeMessage )
    size = int(len(fakeMessage) / 8)
    mdi = size & 0x3F
    length = struct.pack('!Q', size<<3)
    padlen = 55-mdi if mdi < 56 else 119-mdi
    # length big endian 16 bits
    fakeMessage += createBits('80') + createBits('00'*padlen) + createBits(str(binascii.hexlify(length),'ascii'))
    print (len(fakeMessage) ,"bits ", float(len(fakeMessage)/8.0), "bytes ", float(len(fakeMessage)/512),'blocks')
    while len(fakeMessage) >= 512:
            sha256(fakeMessage[:512])
            fakeMessage = fakeMessage[512:]

    fakeMessage = getResult()
    print(fakeMessage)

    # Re HASH
    # size = len(fakeMessage)
    # mdi = size & 0x3F
    # length = struct.pack('!Q', size<<3)
    # padlen = 55-mdi if mdi < 56 else 119-mdi

    # fakeMessage += createBits('80')
    # fakeMessage += createBits('00'*padlen)
    # fakeMessage += createBits(str(binascii.hexlify(length),'ascii'))
    # print (len(fakeMessage) ,"bits ", float(len(fakeMessage)/8.0), "bytes ", float(len(fakeMessage)/512),'blocks')
    # while len(fakeMessage) >= 512:
    #     sha256(fakeMessage[:512])
    #     fakeMessage = fakeMessage[512:]

def createBits(hexdump):
    value = ""
    for a in hexdump:
        r= bin(int(a,16))[2:]
        r='0'*(4-len(r))+r
        value += r

    endRes = []
    for v in value:
        endRes.append('t' if v=='1' else 'f')

    return endRes

preprocess()

print(_h)
print (len(_REFERENCES_))
# Export the data :
with open("sha_decoded_2.pp", "wb") as file:
    pickle.dump( ( _h, _REFERENCES_, _DEPENDENCY_ ,_INV_DEP_, _COST_) , file )

