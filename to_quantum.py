import pickle
with open('sha_decoded_2.pp','rb') as file:
    d = pickle.load(file)
    _h = d[0]
    references = d[1]
    dependencies = d[2]
    inv_dependencies = d[3]

inv_ref = {}
# Create the inverse reference
for key, value in references.items():
    inv_ref[value] = key

# Let's start to see if we can get a result

hash_list=[]
for i in range(len(_h)):
    hash_list +=_h[i]
_h = hash_list

# Find the function to generate each bit from the dependencies

def getValuesAndOperation(something):
    if something[0] == '~':
        return '~', something[2:len(something)-1], None
    return something[0], something[2:something.index(',')], something[something.index(',')+1:len(something)-1]

def replaceWithValue(bit):
    sign, value1, value2 = getValuesAndOperation(inv_ref[bit])
    if value1[0] == 'r':
        value1 = replaceWithValue(value1)

    if value2 is not None and value2[0] == 'r':
        value2 = replaceWithValue(value2)
        return f'({value1}{sign}{value2})'
    else:
        return f'({sign}{value1})'

for _h_bit in _h:
    print(replaceWithValue(_h_bit))
    break




