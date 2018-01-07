import pickle
import operator
import re
prog = re.compile( r"^([\^\~\&\|])\((\w+),?(\w+)?\)$" )
def getElements( op ):
	m= prog.search(op)
	ref1 = m.group(2)
	ref2 = m.group(3)
	return (ref1,ref2)


with open("sha_decoded.pp", "r") as file:
	_h, _REFERENCES_, _DEPENDENCY_ ,_INV_DEP_, _COST_ = pickle.load( file )
inv_refs = {v: k for k, v in _REFERENCES_.iteritems()}
#sorted_COST = sorted(_COST_.items(), key=operator.itemgetter(1))

opsByDiv = {}
# CONSTRAINTS = {}
# for i in range(2):
# 	for j in _h[i]:
# 		CONSTRAINTS[ _h[i][j] ] = 0

def toCell(n,c):
	crs = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	if( c >= 26):
		letter = crs[ (c // 26) -1] + crs[ c % 26 ]
	else:
		letter = crs[c]
	return letter+str(n)

for i in _COST_.items():
	if( i[1] not in opsByDiv ):
		opsByDiv[i[1]]=[]
	opsByDiv[i[1]].append(i[0])

csv = open("sha2562hash.csv","w")

csv.write("\n"*10)
opsResultCell = {}
for n in opsByDiv:
	line = []
	c = 0
	for opRef in (opsByDiv[n]):
		opsResultCell[opRef] = toCell(n+10,c)
		op = inv_refs[opRef]
		a,b = getElements( op )
		if(a[0]=='r'):
			cella = opsResultCell[a]
		elif( a[0] == 't'):
			cella = '1'
		elif( a[0] == 'f' ):
			cella = '0'
		elif( a[0]=='b'):
			cella = toCell(1,int(a[1:]))
		else:
			cella = a

		if( b!= None and b[0]=='r' ):
			cellb = opsResultCell[b]
		elif( b!= None and b[0] == 't'):
			cellb = '1'
		elif( b!= None and b[0] == 'f' ):
			cellb = '0'
		elif( b!= None and b[0]=='b'):
			cellb = toCell(1,int(b[1:]))
		else:
			cellb = b

		if(op[0]=='^'):
			line.append("=XOR("+cella+";"+cellb+")")
		elif(op[0]=='|'):
			line.append("=OR("+cella+";"+cellb+")")
		elif(op[0]=='&'):
			line.append("=AND("+cella+";"+cellb+")")
		elif(op[0]=='~'):
			line.append("=NOT("+cella+")")


		c+=1

	csv.write('\t'.join(line)+"\n")

csv.close()