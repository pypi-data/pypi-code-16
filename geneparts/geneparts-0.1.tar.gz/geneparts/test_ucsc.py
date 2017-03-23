import requests
from urllib2 import urlopen
import MySQLdb

url = 'http://genome.ucsc.edu/cgi-bin/hgTables?hgsid=201790284_dkwVYFu7V6ISmTzFGlXzo23aUhXk'    
url1 = 'http://genome.ucsc.edu/cgi-bin/hgTables?hgsid=585151717_84kunrH0bKFnKv9O6uwq5N6S7wD8&boolshad.hgSeq.promoter=0&hgSeq.promoterSize=1000&hgSeq.utrExon5=on&boolshad.hgSeq.utrExon5=0&hgSeq.cdsExon=on&boolshad.hgSeq.cdsExon=0&hgSeq.utrExon3=on&boolshad.hgSeq.utrExon3=0&hgSeq.intron=on&boolshad.hgSeq.intron=0&boolshad.hgSeq.downstream=0&hgSeq.downstreamSize=1000&hgSeq.granularity=gene&hgSeq.padding5=0&hgSeq.padding3=0&boolshad.hgSeq.splitCDSUTR=0&hgSeq.casing=exon&boolshad.hgSeq.maskRepeats=0&hgSeq.repMasking=lower&hgta_doGenomicDna=get+sequence'

#session = requests.Session()
session = requests.Session()

## Learn these parameters by viewing the web page source. Look for id
params = {
    'hgsid': '201790284_dkwVYFu7V6ISmTzFGlXzo23aUhXk',
    'jsh_pageVertPos': '0',
    'clade': 'mammal',
    'org': 'Human',
    'db': 'hg19',
    'hgta_group': 'genes',
    'hgta_track': 'refGene',
    'hgta_table': 'refFlat',
    'hgta_regionType': 'range',
    'position': 'chr9:21802635-21865969',
    #j'hgta_outputType': 'gff',
    'hgta_outputType': 'sequence',
    'boolshad.sendToGalaxy': '0',
    'boolshad.sendToGreat': '0',
    'boolshad.sendToGenomeSpace': '0',
    'hgta_outFileName': 'test.fa',
    'hgta_compressType': 'none',
    'hgta_doTopSubmit': 'get output'
}

#response = session.post(url, data=params)
response = urlopen(url1)
print response.read()

'''
##  access UCSC MySQL database. How to pass the -A parameter?
conn = MySQLdb.connect(user='genome', host='genome-mysql.cse.ucsc.edu', database='hg19')
cur = conn.cursor()
query = 'show tables'

cur.execute(query)

for t in cur:
    print(t)

conn.close()
'''
