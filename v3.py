# From mk4
import struct
import pickle
from Word import Word
import re
_REFERENCES_ = {}
_INV_DEP_ = {}
_COST_ = {}
_DEPENDENCY_ = {}
prog = re.compile( r"^([\^\~\&\|])\((\w+),?(\w+)?\)$" )

def getDependencies( op ):
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
	if ( val not in _REFERENCES_ ):
		newRef = 'r'+str(len(_REFERENCES_))
		_REFERENCES_[ val ] = newRef
		depends = getDependencies( val )
		_DEPENDENCY_[newRef] = depends
		for r in depends:
			if( r not in _INV_DEP_): _INV_DEP_[r] = []
			_INV_DEP_[r].append(newRef)
		_COST_[newRef] = reduce(max,map(lambda x: _COST_[x],depends),0)+1
		return newRef
	else:
		return _REFERENCES_[ val ]

_k = [0x428a2f98L, 0x71374491L, 0xb5c0fbcfL, 0xe9b5dba5L,
	  0x3956c25bL, 0x59f111f1L, 0x923f82a4L, 0xab1c5ed5L,
	  0xd807aa98L, 0x12835b01L, 0x243185beL, 0x550c7dc3L,
	  0x72be5d74L, 0x80deb1feL, 0x9bdc06a7L, 0xc19bf174L,
	  0xe49b69c1L, 0xefbe4786L, 0x0fc19dc6L, 0x240ca1ccL,
	  0x2de92c6fL, 0x4a7484aaL, 0x5cb0a9dcL, 0x76f988daL,
	  0x983e5152L, 0xa831c66dL, 0xb00327c8L, 0xbf597fc7L,
	  0xc6e00bf3L, 0xd5a79147L, 0x06ca6351L, 0x14292967L,
	  0x27b70a85L, 0x2e1b2138L, 0x4d2c6dfcL, 0x53380d13L,
	  0x650a7354L, 0x766a0abbL, 0x81c2c92eL, 0x92722c85L,
	  0xa2bfe8a1L, 0xa81a664bL, 0xc24b8b70L, 0xc76c51a3L,
	  0xd192e819L, 0xd6990624L, 0xf40e3585L, 0x106aa070L,
	  0x19a4c116L, 0x1e376c08L, 0x2748774cL, 0x34b0bcb5L,
	  0x391c0cb3L, 0x4ed8aa4aL, 0x5b9cca4fL, 0x682e6ff3L,
	  0x748f82eeL, 0x78a5636fL, 0x84c87814L, 0x8cc70208L,
	  0x90befffaL, 0xa4506cebL, 0xbef9a3f7L, 0xc67178f2L]
_h = [0x6a09e667L, 0xbb67ae85L, 0x3c6ef372L, 0xa54ff53aL,
	  0x510e527fL, 0x9b05688cL, 0x1f83d9abL, 0x5be0cd19L]




_h = map( lambda x: Word(list((bin(x)[2:].zfill(32).replace('0','f')).replace('1','t'))) , _h)
_k = map( lambda x: Word(list((bin(x)[2:].zfill(32).replace('0','f')).replace('1','t'))) , _k)

def xor(a,b):
	if (a == 't' and b=='t') or (a == 'f' and b=='f'):
		return 'f'
	elif(a == 'f' and b=='t') or (a == 't' and b=='f'):
		return 't'
	
	return getRef("^("+a+","+b+")")

def an(a,b):
	if( a =='f' or b=='f'):
		return 'f'
	elif( (a =='t' and b=='t') ):
		return 't'
	elif( a=='t'):
		return b
	elif( b=='t'):
		return a
	return getRef("&("+a+","+b+")")

def o(a,b):
	if( a == 't' or b=='t'):
		return 't'
	elif( (a =='f' or a=='t') and (b=='t' or b=='f') ):
		return 'f'
	elif( a=='f'):
		return b
	elif( b=='f'):
		return a
	return getRef("|("+a+","+b+")")

def flip(a):
	if( a == 't' ):
		return 'f'
	if( a == 'f' ):
		return 't'
	return getRef("~("+a+")")

def xorWords( wordA, wordB ):
	res = [None]*32
	for i in range(32):
		res[i] = xor(wordA[i],wordB[i])
	return res

def andWords( wordA, wordB ):
	res = [None] * 32
	for i in range(32):
		res[i] = an(wordA[i], wordB[i])
	return Word(res)

def orWords( wordA, wordB ):
	res = [None] * 32
	for i in range(32):
		res[i] = o(wordA[i], wordB[i])
	return Word(res)

def flipWord( wordA ):
	res = [None] * 32
	for i in range(32):
		res[i] = flip(wordA[i])
	return Word(res)

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

def carry(a, b, at):
	if( at < 0):
		raise Exception("Do not need to carry on 1st")
		return '0'
	if (at != 0):
		return o( an(a[at], b[at]) , an(xor(a[at], b[at]),carry(a,b,at-1)) )
	return an(a[at], b[at])


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
		print i
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
		t1 = addWords(addWords(h , s1) , addWords(addWords(ch , _k[i]) , w[i]))
		
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
	
	fakeMessage = createBits("0100000081cd02ab7e569e8bcd9317e2fe99f2de44d49ab2b8851ba4a308000000000000e320b6c2fffc8d750423db8b1eb942ae710e951ed797f7affc8892b0f1fc122bc7f5d74df2b9441a")

	fakeMessage += map( lambda x : "b"+str(x), range(4 * 8) )
	size = len(fakeMessage) / 8
	

	mdi = size & 0x3F
	length = struct.pack('!Q', size<<3)
	padlen = 55-mdi if mdi < 56 else 119-mdi
	fakeMessage += createBits('80') + createBits('00'*padlen) + createBits(length.encode("hex"))
	print len(fakeMessage) ,"bits ", float(len(fakeMessage)/8.0), "bytes ", float(len(fakeMessage)/512),'blocks'
	
	while len(fakeMessage) >= 512:
		sha256(fakeMessage[:512])
		fakeMessage = fakeMessage[512:]
	
	fakeMessage = getResult()

	# Re HASH
	size = len(fakeMessage)
	mdi = size & 0x3F
	length = struct.pack('!Q', size<<3)
	padlen = 55-mdi if mdi < 56 else 119-mdi
	fakeMessage += createBits('80') + createBits('00'*padlen) + createBits(length.encode("hex"))
	print len(fakeMessage) ,"bits ", float(len(fakeMessage)/8.0), "bytes ", float(len(fakeMessage)/512),'blocks'
	
	while len(fakeMessage) >= 512:
		sha256(fakeMessage[:512])
		fakeMessage = fakeMessage[512:]

	
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

#print(_h)
print (len(_REFERENCES_))

# Export the data :
with open("sha_decoded.pp", "w") as file:
	pickle.dump( ( _h, _REFERENCES_, _DEPENDENCY_ ,_INV_DEP_, _COST_) , file )

