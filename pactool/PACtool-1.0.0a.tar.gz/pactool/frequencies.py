import timeit

start = timeit.default_timer()

def frequencies(snp):

    splitted = snp.split()
    
    code = splitted[0]

    i = 5
    triplets = []

    while i < len(splitted):
        triplet = splitted[i:i+3]
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
        
cases_freq = freqsfile('gwas.cases.gen')
controls_freq = freqsfile('gwas.controls.gen')

result = []

for i in controls_freq:
    for j in cases_freq:
        if i[0] == j[0]:
            i.append(j[1])
            i.append(j[2])
            result.append(i)
            
for r in result:
    ref_freq_total = round((r[1]+r[3])/2, 4)
    alt_freq_total = round((r[2]+r[4])/2, 4)
    r.append(ref_freq_total)
    r.append(alt_freq_total)
    
with open('output.txt', 'w') as output:
    output.write("snp_code" + " " + "ref_freq_control" + " " + "alt_freq_control" + " " + "ref_freq_cases" \
                 + " " + "alt_freq_cases" + " " + "ref_freq_total" + " " + "alt_freq_total" + "\n")
    for r in result:   
        output.write(str(r[0]) + " " + str(r[1]) + " " + str(r[2]) + " " + str(r[3]) + " " +\
                         str(r[4]) + " " + str(r[5]) + " " + str(r[6]) + " " + "\n")
        
end = timeit.default_timer()
runtime = end - start

print(runtime)