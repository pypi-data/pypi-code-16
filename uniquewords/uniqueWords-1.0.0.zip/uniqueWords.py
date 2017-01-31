from nltk.corpus import stopwords
from stemming.porter2 import stem
import enchant
import string
import os
def proper(path):
    proper_path = path[path.rindex('\\'):]
    return proper_path
def uniqueWords(initialName):
    list_of_stemmedwords = []
    list_of_non_duplicate_stemmedwords = []
    replacements = {'  ':' '}   #Define a dictionary with source and target values, this will later be used tto replace multiple spaces which will be formed after the certain removal of characters and punctuations from between
    remove = dict.fromkeys(map(ord, '\n' +string.punctuation)) #makes a list of all punctuations defined in Python
    remover2 = dict.fromkeys(map(ord, '\n' +string.digits)) #Makes a list of all digits
    allWords = enchant.Dict("en_US")
    list_of_stopwords = stopwords.words('english')
    try:
        name,ext = initialName.split('.') #The name and extention of the file name is stored in case it's required later
    except ValueError:
        pass
    str1 = "final"
    try:
        with open(initialName) as inFile:
            f = inFile.read().translate(remove) #removes all puntuations
    except FileNotFoundError:
        print("The given file doesn't exist")
    with open('sampleout.txt','w') as outFile:
        print(f,file = outFile) #writes to an intermediate file without punctuations
    with open('sampleout.txt') as midFile:
        f1 = midFile.read().translate(remover2) #removes all digits from the intermediate file and prepares for writing contents into final file
    finalName = str1 + "_" + initialName #The name of the final file is automatically decided based on the name of the input file
    stName = "stemmed" + "_" + finalName
    with open('stopped.txt','w') as stoppedFile:
        print(f1,file = stoppedFile) #Writes the file content without any digits or punctuations to a new file, this file however has multiple spaces and stopwords due to removal of characters and numbers from between
    with open('stopped.txt') as inf, open('meaningless.txt','w') as meanFile:
        for line in inf:
            for word in line.split():
                if word not in list_of_stopwords:
                    meanFile.write(word)
                    meanFile.write(' ')
    with open('meaningless.txt') as mFile, open('meaningfull.txt','w') as sf:
        for line in mFile:
            for word in line.split():
                if(allWords.check(word) == False):
                    line = line.replace(word,'')
            sf.write(line)
    with open('meaningfull.txt') as mft, open('spaceremover.txt','w') as spcf:
        for lines in mft:
            for src,tgt in replacements.items():
                lines = lines.replace(src,tgt)
            spcf.write(lines)
    with open('spaceremover.txt') as spcf, open(finalName,'w') as ff:
        for lines in spcf:
            ff.write(lines)
    with open(finalName,) as iff, open(stName,'w') as sfile:
        for line in iff:
            for word in line.split():
                list_of_stemmedwords.append(stem(word))
                list_of_non_duplicate_stemmedwords = set(list_of_stemmedwords)
        for i in list_of_non_duplicate_stemmedwords:
            sfile.write(i)
            sfile.write(' ')
    print('Done, please open: ', finalName)
    print("for stemmed words open: ", stName)
    os.remove('sampleout.txt') #Removes the intermediate file
    os.remove('stopped.txt') #Removes the stopped file
    os.remove('meaningless.txt') #Removes the meaningless file
    os.remove('meaningfull.txt') #removes meaningfull but spaced file
    os.remove('spaceremover.txt')#removes spaced file
