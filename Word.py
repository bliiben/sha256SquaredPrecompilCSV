class Word( ):
    def __init__(self, bits):
        if( len(bits) == 32 ):
            self.bits = bits
        else:
            raise Exception("Words need to be 32 bits long "+ str(len(bits)))

    def __str__(self):
        return "\n["+','.join(map(str,self.bits))+"]"

    def __repr__(self):
        return str(self)

    def __getitem__(self, item ):
        return self.bits[item]

    def rotateRight(self, value):
        return Word(self.bits[-value:] + self.bits[:-value])

    def shiftRight( self, value):
        prepend =[]
        for i in range(value):
            prepend.append('f')
        return Word(prepend + self.bits[:-value])

    def simplify( self ):
        for i in range(len(self.bits)):
            self.bits[i] = getRef(self.bits[i])
