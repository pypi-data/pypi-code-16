import timeit

start = timeit.default_timer()

def frequencies(snp):

    code = snp[0]

    i = 5
    triplets = []

    while i < len(snp):
        triplet = snp[i:i+3]
        triplets.append(str(triplet[0]) + str(triplet[1]) + str(triplet[2]))
        i = i + 3
    
    string = ""
    
    for triplet in triplets:
        if triplet == '100':
            string += '('
        elif triplet == '010':
            string += '.'
        elif triplet == '001':
            string += ')'
        else:
            print("There is some error in the columns of the input")
    
    ref_freq = round(string.count('(')/len(string) + (string.count('.')/len(string))/2, 4)
    alt_freq = round(string.count(')')/len(string) + (string.count('.')/len(string))/2, 4)
    final = [code, ref_freq, alt_freq]
    return final
    
def freqsfile(file):
    i = []
    final = []
    with open(file, 'r') as controls:
        for line in controls.readlines():
            i.append(line.strip())

    for line in i[:10]:
        final.append(frequencies(line))
    return final
