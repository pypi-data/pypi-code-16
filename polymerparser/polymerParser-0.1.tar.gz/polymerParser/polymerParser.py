# Guillermo Carrera Trasobares 2017

import os, sys, fnmatch, argparse, json
from pathlib import Path
from bs4 import BeautifulSoup

parser= argparse.ArgumentParser()
parser.add_argument('-u','--url',help="Introduce the URL you want to start parsing")
parser.add_argument('-o','--output',help="Introduce the desired output: txt, json.....")
parser.add_argument('-s','--sorted',help="Sorts the output",action='store_true')
parser.add_argument('-l','--listFiles',help="Lists all files inside the selected directory and sub-directories",action='store_true')
args = parser.parse_args()

#if len(sys.argv) < 2:
#   cwd = os.getcwd() + '/index.html'
#   print  ("Error!! Introducir directorio a analizar como primer argumento")
#  print (" Se utilizara el directorio actual: " + cwd + "\n\n")
#else:
#    cwd = sys.argv[1]

def removeDups(inputfile, outputfile):
    lines=open(inputfile, 'r').readlines()
    lines_set = set(lines)
    out=open(outputfile, 'w')
    for line in lines_set:
        out.write(line)
        
def listAllFiles(dirrel):
    count=1
    for subdir, dirs, files in os.walk(dirrel):
        for file in files:
            print(str(count) + ': '+ os.path.join(subdir, file))
            count=count+1

def createJson(inputfile):
    count=1
    lines=open(inputfile, 'r').readlines()
    with open("imports.json",'w') as outfile:
        outfile.write("[")
        for line in lines[:-1]:
            #Eliminate the last \n while parsing the json
            json.dump({'url:':line[:-1], 'number:':count},outfile, indent=3)
            outfile.write(",")
            count=count+1
        for line in lines[-1:]:
            json.dump({'url:':line[:-1], 'number:':count},outfile, indent=3)
            outfile.write("]")

def funcionRecursiva(dirrel):
    dirajust = dirrel
    fileopen = open(dirajust)
    soup2 = BeautifulSoup(fileopen, "html.parser")
    with open("totalImports.txt", "a") as myfile:
        for link in soup2.find_all(rel="import"):
            #print('Import number:' + dirajust)
            if link.get('href') == '':
                break
            else:
                auxi = str(link.get('href'))
                if auxi.startswith("./"):
                    #print("Empieza con ./:   "+auxi + '\n')
                    #print("El resultado de removerPuntoPunto es: " + removerPuntoPunto(auxi))
                    auxi = str(Path(dirajust).parent) + auxi[1:]
                    myfile.write(auxi+'\n')
                    funcionRecursiva(auxi)
                if auxi.startswith("../../"):
                    auxi2 = str(Path(dirajust).parent.parent.parent)
                    auxi = auxi2 + auxi[5:]
                    #print("Empieza con ../../:  "+auxi+'\n')
                    myfile.write(auxi+'\n')
                    funcionRecursiva(auxi)
                if auxi.startswith("../"):
                    auxi2 = str(Path(dirajust).parent.parent)
                    auxi = auxi2 + auxi[2:]
                    #print("Empieza con ../:  "+auxi+'\n')
                    myfile.write(auxi+'\n')
                    funcionRecursiva(auxi)
                elif auxi.startswith("/"):
                    #print("Empieza con /:   "+auxi + '\n')
                    funcionRecursiva(auxi)
                else:
                    #print("Import a tratar:  " + auxi + '\n')
                    auxi = str(Path(dirajust).parent) + '/' + auxi
                    myfile.write(auxi+'\n')
                    funcionRecursiva(auxi)


if args.listFiles:
    if args.url:
        listAllFiles(args.url)
        sys.exit()
    else:
        print ("No directory selected, using current one\n\n")
        listAllFiles(os.getcwd())
        sys.exit()

if args.url:
    print (args.url)
    funcionRecursiva(args.url)
    if args.output and args.sorted:
        if args.output == "json":
            removeDups('totalImports.txt', 'sortedImports.txt')
            createJson('sortedImports.txt')
            sys.exit()
        else:
            print ("generating default .txt output")
            removeDups('totalImports.txt', 'sortedImports.txt')
            sys.exit()
    else:
        if args.output:
            if args.output == "json":
                createJson('totalImports.txt')
                sys.exit()
    if args.sorted:
        removeDups('totalImports.txt', 'sortedImports.txt')
                
            
                



