#!/usr/bin/env python
#
# Copyright 2016 Ville Rantanen
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

'''Large CSV curses based printer.'''

__author__ = "Ville Rantanen <ville.q.rantanen@gmail.com>"

__version__ = "0.1.3"

import sys,os,argparse
from argparse import ArgumentParser 
import unicodedata, re

class EndProgram( Exception ):
    ''' Nice way of exiting the program '''
    pass

class table_reader:
    """ Class for reading generic CSV files. """ 
    def __init__(self,filename,opts):
        self.filename=filename
        self.reader=False
        self.opts=opts
        self.collength=[]
        self.data=[]
        self.control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
        self.control_char_re = re.compile('[%s]' % re.escape(self.control_chars))
        self.na_re = re.compile('^na$|^nan$|^$', re.IGNORECASE)
        self.header=[]
        self.open()

    def open(self):
        ''' Opens the table for reading '''
        if self.filename==sys.stdin:
            self.reader=sys.stdin
        else:
            self.reader=open(self.filename,'r')
        while True:
            self.header=self.split_row(self.reader.readline())
            if self.header:
                break

    def get_header(self):
        return self.header
    
    def read(self,lines):
        ''' Read a table from current position, return N lines and column lengths '''
        self.collength=[]
        self.data=[]
        cols=0
        r=0
        while True:
            row=self.reader.readline()
            if not row:
                break
            row=self.split_row(row)
            if not row:
                continue
            newcols=len(row)
            if newcols>cols:
                self.collength.extend([0]*(newcols-cols))
                cols=newcols
            for c in range(newcols):
                self.collength[c]=max(self.collength[c],len(row[c]))
            self.data.append(row)
            r=1+r
            if r==lines:
                break
        if len(self.header)>=len(self.collength):
            self.collength=[max(self.collength[c],len(self.header[c])) for c in range(len(self.collength))]
        return (self.data, self.collength)


    def split_row(self,row):
        ''' splits a row in to columns, and clean the content. returns a list '''
        
        if self.opts.comment and row.startswith(self.opts.comment):
            return False
        row=unicode(row, "utf-8")
        row=row.split(self.opts.indelimiter[0])
        for x in range(len(self.opts.indelimiter)-1):
            row=[c.split(self.opts.indelimiter[x+1]) for c in row]
            row=[c for sublist in row for c in sublist]

        row=[self.control_char_re.sub('', i) for i in row]
        row=[c.strip('" ') for c in row]
        row=[self.na_re.sub('nan', i) for i in row]

        if self.opts.format:
            row=[self.number_format(i,self.opts.format) for i in row]
        return row
        
    def number_format(self,s,f):
        ''' Format a numeric string, or return the string if not numeric '''
        try:
            out=f%float(s)
        except:
            out=s
        return out
    
    def find_numeric(self):
        ''' Find numerical columns '''
        self.numeric=[True]*len(self.collength)
        for row in self.data:
            for c in range(len(row)):
                if not self.numeric[c]:
                    continue
                self.numeric[c]=is_number(row[c])
        return self.numeric

    def get_numeric(self):
        ''' Return list of booleans for numericality '''
        return self.find_numeric()

def setup_options():
    ''' Create command line options '''
    usage='''
fast-ncsv is a table pretty printer. 
Project page: https://bitbucket.org/MoonQ/ncsv

'''
 
    parser=ArgumentParser(description=usage,
                          formatter_class=argparse.RawDescriptionHelpFormatter,
                          epilog="\n".join(["Version: "+__version__,__author__]))
    parser.add_argument("-a",type=str,dest="align",default="left",choices=['left', 'right', 'auto', 'center'],
                     help="Align contents. Default: left. Auto implies keeping file in memory.")
    parser.add_argument("--comment",type=str,dest="comment",default=False,
                     help="Skip rows starting with given string ex. '#'. Default: No skipping")
    parser.add_argument("-d",type=str,dest="delimiter",default="|",
                     help="Output delimiter for the table. Default: %(default)s")
    parser.add_argument("-i",type=str,action="append",default=[],dest="indelimiter",
                     help="Input delimiter for the file. Supports multiple delimiters. default: [tab]")
    parser.add_argument("-n",action="store_false",dest="numbers",default=True,
                     help="Disable line numbers.")
    parser.add_argument("-r",type=int,dest="repeat",default=0,
                     help="Repeat header every N line. If 0, then use screen size. Default: %(default)s")                 
    parser.add_argument("-s",type=str,dest="format",default=False,
                     help="Format numeric values ex. '%%.03f'. Default: no formatting")
    parser.add_argument("-v","--version",action="version",version=__version__)
    parser.add_argument("-w",type=int,dest="colwidth",default=0,
                     help="Maximum width of a column. Default: %(default)s")
    parser.add_argument("-W",type=int,dest="colminwidth",default=1,
                     help="Minimum width of a column. Default: %(default)s")
                     
    parser.add_argument("file",type=str, nargs='*',
                     help="File(s) to be opened. stdin autodetected")
    opts=parser.parse_args()

    if len(opts.indelimiter)==0:
        opts.indelimiter=["\t"]
    opts.indelimiter=[s.decode('string_escape') for s in opts.indelimiter]
    if opts.repeat==0:
        try:
            opts.repeat, columns = [int(x)-1 for x in os.popen('stty size', 'r').read().split()]
        except:
            opts.repeat=25
    return opts

def is_number(s):
    ''' Check if string is float '''
    try:
        out=float(s)
        return True
    except:
        return False

def pad(s, max_length, right=True):
    ''' Returns a padded string '''
    if right:
        return s[:max_length].ljust(max_length)
    else:
        return s[:max_length].rjust(max_length)

def cpad(s, max_length, foo=True):
    ''' Returns a center padded string '''
    return s[:max_length].center(max_length)

def table_print(filename,opts):
    ''' Print a table on the console '''
    reader=table_reader(filename,opts)
    padder=pad
    header=reader.get_header()
    header_len=len(header)
    line_end='\n'
    (data,collength)=reader.read(opts.repeat-1)
    r=1
    while len(data)>0:
        rowsstrlen=len(str(r+opts.repeat-2))
        if opts.colwidth==0:
            opts.colwidth=max(collength)
        collength=[min(opts.colwidth,i) for i in collength]
        collength=[max(opts.colminwidth,i) for i in collength]
        if opts.align=="left":
            numeric=[False]*len(collength)
        if opts.align=="right":
            numeric=[True]*len(collength)
        if opts.align=="center":
            numeric=[True]*len(collength)
            padder=cpad
        if opts.align=="auto":
            numeric=reader.get_numeric()
        if opts.numbers:
            sys.stdout.write(padder("#", rowsstrlen, False))
            sys.stdout.write(opts.delimiter)
        for c in range(header_len):
            sys.stdout.write(cpad(header[c], collength[c], True).encode('utf-8'))
            if c<header_len-1:
                sys.stdout.write(opts.delimiter)
        sys.stdout.write(line_end)
        for row in data:
            if opts.numbers:
                sys.stdout.write(padder(str(r), rowsstrlen, False))
                sys.stdout.write(opts.delimiter)
            cols=len(row)
            for c in range(cols):
                sys.stdout.write(padder(row[c], collength[c], not numeric[c]).encode('utf-8'))
                if c<cols-1:
                    sys.stdout.write(opts.delimiter)
            sys.stdout.write(line_end)
            r+=1
        (data,collength)=reader.read(opts.repeat-1)
    if r==1:
        # no data, just a header
        for c in range(header_len):
            sys.stdout.write(cpad(header[c], len(header[c]), True).encode('utf-8'))
            if c<header_len-1:
                sys.stdout.write(opts.delimiter)
        sys.stdout.write(line_end)
def main():
    opts=setup_options()
    try:
        if (not sys.stdin.isatty()):
            table_print(sys.stdin, opts)
        for fi in opts.file:
            table_print(fi, opts)
    except IOError as (n,e):
        if  n==32:
            pass
        else:
            import traceback
            print traceback.format_exc()

if __name__ == "__main__":
    main()
