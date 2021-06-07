import pickle
with open('sha_decoded_2.pp','rb') as file:
    d = pickle.load(file)
    _h = d[0]
    references = d[1]
    depencencies = d[2]
    inv_depencencies = d[3]

print(references )

