#-----------------------------------------------------------------------#
#
#    This program takes n-gram files and a word list    
#    and creates a file with lists of most similar words.
#    John Goldsmith and Wang Xiuli 2012.
#    Jackson Lee and Simon Jacobs 2014
#
#-----------------------------------------------------------------------#

from collections import (OrderedDict, defaultdict, Counter)
from itertools import combinations
from pathlib import Path

import json
import numpy as np
import scipy.spatial
import scipy.sparse
import networkx as nx

from linguistica.util import (double_sorted, SEP_NGRAM)



def hasGooglePOSTag(line, corpus):
    if corpus == 'google':
        for tag in ['_NUM', '_ADP', '_ADJ', '_VERB', '_NOUN',
                    '_PRON', '_ADV', '_CONJ', '_DET']:
            if tag in line:
                return True
        else:
            return False
    else:
        return False

def GetMyWords(infileWordsname):
    word_to_freq = json.load(infileWordsname.open())
    return [word for word, freq in
        double_sorted(word_to_freq.items(),
        key=lambda x: x[1], reverse=True)]







def counting_context_features(context_array):
    return np.dot(context_array, context_array.T) 








def compute_coordinates(NumberOfWordsForAnalysis, NumberOfEigenvectors, myeigenvectors):
    Coordinates = dict()
    for wordno in range(NumberOfWordsForAnalysis):
        Coordinates[wordno]= list() 
        for eigenno in range(NumberOfEigenvectors):
            Coordinates[wordno].append( myeigenvectors[ wordno, eigenno ] )
    return Coordinates











def compute_WordToSharedContextsOfNeighbors(analyzedwordlist, WordToContexts,
        WordToNeighbors, ContextToWords, mincontexts):

    WordToSharedContextsOfNeighbors = dict()

    for word in analyzedwordlist:
        WordToSharedContextsOfNeighbors[word] = dict()

        neighbors = WordToNeighbors[word] # list of neighbor indices

        for context in WordToContexts[word].keys():
            WordToSharedContextsOfNeighbors[word][context] = list()

            for neighbor in neighbors:
                if neighbor in ContextToWords[context]:
                    WordToSharedContextsOfNeighbors[word][context].append(neighbor)

            if len(WordToSharedContextsOfNeighbors[word][context]) < mincontexts:
                del WordToSharedContextsOfNeighbors[word][context]

    ImportantContextToWords = dict()
    for word in analyzedwordlist:
        for context in WordToSharedContextsOfNeighbors[word].keys():
            CountOfThisWordInThisContext = ContextToWords[context][word]
            if CountOfThisWordInThisContext >= mincontexts:
                if context not in ImportantContextToWords:
                    ImportantContextToWords[context] = dict()
                ImportantContextToWords[context][word] = CountOfThisWordInThisContext

    return (WordToSharedContextsOfNeighbors, ImportantContextToWords)


def output_WordToSharedContextsOfNeighbors(outfilenameSharedcontexts,
        WordToSharedContextsOfNeighbors, analyzedwordlist):

    with outfilenameSharedcontexts.open("w") as f:
        for i, word in enumerate(analyzedwordlist, 1):
            ContextToNeighbors = WordToSharedContextsOfNeighbors[word] # a dict
            if not ContextToNeighbors:
                continue

            # To ensure that the output is always the same, we need three
            # rounds of sorting here:
            #   1) sort alphabetically by the context str
            #   2) reverse sort for sizes of neighbor lists
            #   3) sort alphabetically for neighbor lists with the same size

            ContextToNeighbors = sorted(ContextToNeighbors.items())
            # ContextToNeighbors is now a list of tuples, not a dict anymore

            ContextToNeighbors = double_sorted(ContextToNeighbors,
                key=lambda x: len(x[1]), reverse=True, subkey=lambda x:x[1])

            print("{} {} ({})".format(i, word, len(ContextToNeighbors)), file=f)

            for context, neighbors in ContextToNeighbors:
                context = context.replace("\t", " ")
                neighbors = " ".join(neighbors)
                print("          {:20} | {}".format(context, neighbors), file=f)

            print(file=f)


def output_ImportantContextToWords(outfilename, ImportantContextToWords):

    ImportantContextToWords_sorted = double_sorted(
        ImportantContextToWords.items(), key=lambda x: len(x[1]), reverse=True)

    context_list = [context.replace("\t", " ")
                        for context, v in ImportantContextToWords_sorted]
    max_key_length = max([len(x) for x in context_list])

    WordToCount_list = [WordToCount for _, WordToCount in ImportantContextToWords_sorted]

    with outfilename.open("w") as f:
        for context, WordToCount in zip(context_list, WordToCount_list):
            print("{} {}".format(context.ljust(max_key_length), 
                len(WordToCount)), file=f)
        print(file=f)

        for context, WordToCount in zip(context_list, WordToCount_list):
            if not WordToCount:
                continue

            print("\n===============================================\n", file=f)
            print("{} {}".format(context.ljust(max_key_length),
                len(WordToCount)), file=f)
            print(file=f)

            WordToCount_sorted = double_sorted(WordToCount.items(),
                key=lambda x :x[1], reverse=True)

            # don't use "count" as a variable (it's the name of a function in python)
            max_word_length = max([len(word)
                for word, c in WordToCount_sorted])

            for word, c in WordToCount_sorted:
                print("        {} {}".format(
                    word.ljust(max_word_length), c), file=f)


    ### BEGIN work in progress ### J Lee, 2015-12-24
    eigenvector_outdict = dict()

    for eigen_no in range(len(myeigenvalues)):

        ## BUG? Why is len(myeigenvalues) NOT equal to nEigenvectors?
        coordinate_word_pairs = list()

        for word_no in range(nWordsForAnalysis):
            coordinate = myeigenvectors[word_no, eigen_no]
            word = analyzedwordlist[word_no]
            coordinate_word_pairs.append((coordinate, word))

        coordinate_word_pairs.sort()
        eigenvector_outdict[eigen_no] = (myeigenvalues[eigen_no],
                                         coordinate_word_pairs)

    with Path(outfolder, corpusName + '_eigenvectors.json').open('w') as f:
        json_dump(eigenvector_outdict, f)

    # Data structure of the output json file:
    #
    # { eigen_number : [ eigenvalue, eigenvector_as_an_array ] }
    #
    # eigen_number starts from 0 to k-1, for k eigenvectors
    # (note: I don't understand why the current code only outputs 6 eigenvectors, while our default parameter has set the number of eigenvectors to be 11... bug to fix soon?)
    #
    # eigenvector_as_an_array is an array of pairs, where each pair is (coordinate, word). The pairs in eigenvector_as_an_array are sorted in ascending order by the coordinates.

    ### END work in progress ### J Lee, 2015-12-24


#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
# TODO: bring latex output back


#def LatexAndEigenvectorOutput(LatexFlag, PrintEigenvectorsFlag, infileWordsname, outfileLatex, outfileEigenvectors, NumberOfEigenvectors, myeigenvalues, NumberOfWordsForAnalysis):
#    if LatexFlag:
#            #Latex output
#            print("% ",  infileWordsname, file=outfileLatex)
#            print("\\documentclass{article}", file=outfileLatex) 
#            print("\\usepackage{booktabs}" , file=outfileLatex)
#            print("\\begin{document}" , file=outfileLatex)

#    data = dict() # key is eigennumber, value is list of triples: (index, word, eigen^{th} coordinate) sorted by increasing coordinate
#    print("9. Printing contexts to latex file.")
#    formatstr = '%20s   %15s %10.3f'
#    headerformatstr = '%20s  %15s %10.3f %10s'
#    NumberOfWordsToDisplayForEachEigenvector = 20
#            

#            
#                     
#    if PrintEigenvectorsFlag:

#            for eigenno in range(NumberOfEigenvectors):
#                    print >>outfileEigenvectors
#                    print >>outfileEigenvectors,headerformatstr %("Eigenvector number", eigenno, myeigenvalues[eigenno], "word" )
#                    print >>outfileEigenvectors,"_"*50 

#                    eigenlist=list()        
#                    for wordno in range (NumberOfWordsForAnalysis):         
#                            eigenlist.append( (wordno,myeigenvectors[wordno, eigenno]) )            
#                    eigenlist.sort(key=lambda x:x[1])            

#                    for wordno in range(NumberOfWordsForAnalysis):    
#                            word = analyzedwordlist[eigenlist[wordno][0]]
#                            coord =  eigenlist[wordno][1]        
#                            print >>outfileEigenvectors, formatstr %(eigenno, word, eigenlist[wordno][1])


#     

#    if LatexFlag:
#            for eigenno in range(NumberOfEigenvectors):
#                    eigenlist=list()    
#                    data = list()
#                    for wordno in range (NumberOfWordsForAnalysis):         
#                            eigenlist.append( (wordno,myeigenvectors[wordno, eigenno]) )            
#                    eigenlist.sort(key=lambda x:x[1])            
#                    print >>outfileLatex             
#                    print >>outfileLatex, "Eigenvector number", eigenno, "\n" 
#                    print >>outfileLatex, "\\begin{tabular}{lll}\\toprule"
#                    print >>outfileLatex, " & word & coordinate \\\\ \\midrule "

#                    for i in range(NumberOfWordsForAnalysis):             
#                            word = analyzedwordlist[eigenlist[i][0]]
#                            coord =  eigenlist[i][1]
#                            if i < NumberOfWordsToDisplayForEachEigenvector or i > NumberOfWordsForAnalysis - NumberOfWordsToDisplayForEachEigenvector:
#                                    data.append((i, word , coord ))
#                    for (i, word, coord) in data:
#                            if word == "&":
#                                    word = "\&" 
#                            print >>outfileLatex,  "%5d & %10s &  %10.3f \\\\" % (i, word, coord) 

#                    print >>outfileLatex, "\\bottomrule \n \\end{tabular}", "\n\n"
#                    print >>outfileLatex, "\\newpage" 
#            print >>outfileLatex, "\\end{document}" 


