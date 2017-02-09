#!/usr/bin/env python
#
# Copyright 2016 Ville Rantanen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''CSV file pretty printer and curses based browser.'''

__author__ = "Ville Rantanen <ville.q.rantanen@gmail.com>"

__version__ = "0.15.0"

import sys,os,argparse
from argparse import ArgumentParser 
import unicodedata, re

class EndProgram( Exception ):
    ''' Nice way of exiting the program '''
    pass

class table_reader:
    """ Class for reading generic CSV files. """ 
    def __init__(self,filename,opts,keep):
        self.stdin=filename==sys.stdin
        if self.stdin or opts.transpose:
            self.keep=True
        else:
            self.keep=keep
        self.filename=filename
        self.reader=None
        self.numeric=False
        self.opts=opts
        self.rows=0
        self.sortcol=-1
        self.sortasc=True
        self.collength=[]
        self.data=[]
        self.control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
        self.control_char_re = re.compile('[%s]' % re.escape(self.control_chars))
        #self.comment_re = re.compile('^%s' % opts.comment )
        self.na_re = re.compile('^na$|^nan$|^$|^'+self.opts.nan+'$', re.IGNORECASE)
        self.gzip=opts.gzip
        
        self.read()
        if opts.transpose:
            self.transpose_table()
    
    def __iter__(self):
        if self.stdin:
            return iter(self.data)
        return self

    def open(self):
        ''' Opens the table for reading, not for stdIn '''
        if self.stdin:
            return
        if self.gzip: 
            import gzip
            self.reader=gzip.open(self.filename)
        else:
            self.reader=open(self.filename,'r')
        
    def next(self):
        ''' Row by row reader '''
        return self.split_row(self.reader.next())

    def read(self):
        ''' Read a table, return column  widths, and the whole table data if needed '''
        if self.gzip: import gzip,zlib
        if not self.stdin:
            # real file
            if self.gzip:
                self.reader=gzip.open(self.filename)
            else:
                self.reader=open(self.filename,'r')
        else:
            # stream input
            if self.gzip:
                d = zlib.decompressobj(16+zlib.MAX_WBITS)
                self.reader=d.decompress(self.filename.read()).split("\n")
            else:
                self.reader=self.filename
        self.collength=[]
        self.numeric=False
        self.sortcol=-1
        self.data=[]
        cols=0
        r=0
        for row in self.reader:
            if self.gzip and row=="": continue
            row=self.split_row(row)
            if not row:
                continue
            newcols=len(row)
            if newcols>cols:
                self.collength.extend([0]*(newcols-cols))
                cols=newcols
            for c in range(newcols):
                self.collength[c]=max(self.collength[c],len(row[c]))
            if self.keep:
                self.data.append(row)
            r=1+r
        self.reader.close()
        self.rows=r
        if r==0:
            # empty input
            return
        if self.opts.header:
            self.data.insert(0,[str(i+1) for i in range(len(self.collength))])
        else:
            # add header if missing
            if self.keep:
                while len(self.data[0])<len(self.collength):
                    self.data[0].append('-')
                for c in range(len(self.collength)):
                    if len(self.data[0][c])==0:
                        self.data[0][c]='-'    

    def split_row(self,row):
        ''' splits a row in to columns, and clean the content. returns a list '''

        if self.opts.comment and row.startswith(self.opts.comment):
            return False
        row=unicode(row, "utf-8")
        # When using Curses, rid of non-ascii. 
        if not (self.opts.statistics or self.opts.console):
            row=unicodedata.normalize('NFKD', row).encode('ascii','ignore')
        row=row.split(self.opts.indelimiter[0])
        for x in range(len(self.opts.indelimiter)-1):
            row=[c.split(self.opts.indelimiter[x+1]) for c in row]
            row=[c for sublist in row for c in sublist]

        row=[self.control_char_re.sub('', i) for i in row]
        row=[c.strip('\'" ') for c in row]
        row=[self.na_re.sub(self.opts.nan, i) for i in row]

        if self.opts.format:
            row=[self.number_format(s,self.opts.format,i) for i,s in enumerate(row)]
        return row
        
    def number_format(self,s,f,i=0):
        ''' Format a numeric string, or return the string if not numeric '''

        if len(f)==1:
            format=f[0]
        elif len(f)>=i+1:
            format=f[i]
        elif f[-1].endswith('*'): 
            format=f[-1]
        else:
            format="%s"
        try:
            out=format.rstrip('*')%float(s)
        except:
            out=s
        return out
    
    def find_numeric(self):
        ''' Find numerical columns '''
        self.numeric=[True]*len(self.collength)
        for row in self.data[1:]:
            for c in range(len(row)):
                if not self.numeric[c]:
                    continue
                if self.na_re.match(row[c]):
                    continue
                self.numeric[c]=is_number(row[c])
        return self.numeric

    def get_numeric(self):
        ''' Return list of booleans for numericality '''
        if not self.numeric:
            return self.find_numeric()
        return self.numeric

    def get_data(self):
        return self.data
        
    def get_dims(self):
        return [self.collength,self.rows]
    
    def get_sort_col(self):
        return self.sortcol

    def is_sort_ascending(self):
        return self.sortasc

    def sort_table(self,col):
        ''' data sort by a column '''
        if self.opts.freeze:
            col=col+1
        col=min(col,len(self.collength)-1)
        if col==self.sortcol:
            self.sortasc=not self.sortasc
        else:
            self.sortasc=True
        column_numeric=self.get_numeric()[col]
        na_value=float('inf') if self.sortasc else float('-inf')
        
        if column_numeric:
            convert = lambda text: float(text) if is_number(text,self.na_re) else na_value
            sort_key = lambda key: convert(key[col])
        else:
            number_re = re.compile('([0-9]+)')
            convert = lambda text: float(text) if is_number(text) else text.lower()
            sort_key = lambda key: [ convert(c) for c in number_re.split(key[col]) ]
        self.data[1:]=sorted(self.data[1:],key=sort_key,reverse=not self.sortasc)
        self.sortcol=col
    
    def transpose_table(self):
        if self.rows==1:
            self.data=[ [ x ] for x in self.data[0] ]
        else:
            self.data=map(None,*self.data)
            for r in range(len(self.data)):
                if None in self.data[r]:
                    self.data[r]=tuple(
                       "" if x==None else x for x in self.data[r]  
                    )
        self.collength=[]
        self.numeric=False
        self.sortcol=-1
        cols=0
        r=0
        for row in self.data:
            if not row:
                continue
            newcols=len(row)
            if newcols>cols:
                self.collength.extend([0]*(newcols-cols))
                cols=newcols
            for c in range(newcols):
                self.collength[c]=max(self.collength[c],len(row[c]))
            r=1+r
        self.rows=r

def reset_curses(stdscr):
    global curses
    curses.nocbreak()
    stdscr.keypad(0)
    curses.endwin()

def get_interactive_help_text():
    return '''  arrows,page up/down,home/P,end/G,<,>
     control the location.
  a/z move highlight cursor
  c   file statistics
  g : go to location
  f   toggle freezing
  n   toggle row numbers
  o   sort/reverse by column
  q   exit current file
  r   reload the file
  s / search (case insensitive)
  S   modify string formatting
  t   transpose table
  +/- change max width of columns
  ,/. shift column contents
  h   help'''

def setup_options():
    ''' Create command line options '''
    usage='''
NCSV (Nice CSV) either prints out a table padded with spaces,
or is an interactive table browser. 
If the file is omitted, stdin is used.
If the file is a folder, all the files within are used.
Project page: https://bitbucket.org/MoonQ/ncsv
 
interactive mode keymap:
'''+get_interactive_help_text()+'''

interactive mode indicators:
 column on the left is:
  +   sorted ascending
  -   sorted descending
  <   shifted
 cell indicator:
  >   contents do not fit view
'''
 
    parser=ArgumentParser(description=usage,
                          formatter_class=argparse.RawDescriptionHelpFormatter,
                          epilog="\n".join(["Version: "+__version__,__author__]))
    common_group=parser.add_argument_group('common', 'Common options')
    console_group=parser.add_argument_group('console', 'Console printing options')
    browser_group=parser.add_argument_group('browser', 'Curses browser options')
    
    common_group.add_argument("--comment",type=str,dest="comment",default=False,
                     help="Skip rows starting with given string ex. '#'. Default: No skipping")
    common_group.add_argument("-i",type=str,action="append",default=[],dest="indelimiter",
                     help="Input delimiter for the file. Supports multiple delimiters. default: [tab]")
    common_group.add_argument("--nan",action="store",type=str,dest="nan",default="nan",
                     help="String to use as not a number. Default: %(default)s")
    common_group.add_argument("--nh",action="store_true",dest="header",default=False,
                     help="File has no header row, add column number. Default: %(default)s")
    common_group.add_argument("-n",action="store_true",dest="numbers",default=False,
                     help="Show line numbers. Default: %(default)s")
    common_group.add_argument("-s",type=str,dest="format",default=False,
                     help="Format numeric values ex. '%%.03f'. Use comma separated formats for individual column formatting. If last character is * the formatting is used for the rest of the columns. Default: no formatting")
    common_group.add_argument("-v","--version",action="version",version=__version__)
    common_group.add_argument("-w",type=int,dest="colwidth",default=0,
                     help="Maximum width of a column. Default: %(default)s")
    common_group.add_argument("-W",type=int,dest="colminwidth",default=1,
                     help="Minimum width of a column. Default: %(default)s")
    common_group.add_argument("-t",action="store_true",dest="transpose",default=False,
                     help="Transpose table.")
    common_group.add_argument("-z",action="store_true",dest="gzip",default=False,
                     help="Read a gzip compressed file.")
                                          
    console_group.add_argument("-a",type=str,dest="align",default="left",choices=['left', 'l','right','r', 'center','c','auto','a'],
                     help="Align contents. Default: left. Auto implies keeping file in memory.")
    console_group.add_argument("-c",action="store_true",dest="console",default=False,
                     help="Use console instead of interactive curses based browser. If output is passed to a pipe, console output is automatically enabled. Default: %(default)s")
    console_group.add_argument("--cf",type=str,dest="console_format",default=False,
                               choices=['d', 'm', 'a', 'e', 'M', 'A','E'],
                     help="Format console output (if set, implies -c) Default: d. d=Delimited with -d, m=Markdown syntax, a=Ascii box, e=Extended Ascii box. M uses wider, more standard, format. A and E modes draw boxes for each table cell.")
    console_group.add_argument("-d",type=str,dest="delimiter",default="|",
                     help="Output delimiter for the table. Default: %(default)s")
    console_group.add_argument("--stat",action="store_true",dest="statistics",default=False,
                     help="Count statistics and print output as tab delimited table (change with -d)")
    
    browser_group.add_argument("--dc",action="store_true",dest="dark_colors",default=False,
                     help="Use dark colorscheme, better for white background terminals.")
    browser_group.add_argument("-f",action="store_true",dest="freeze",default=False,
                     help="Freeze the 1st column and row. Default: %(default)s")
    browser_group.add_argument("--nc",action="store_false",dest="colors",default=True,
                     help="Disable colors. Default: use colors")
    browser_group.add_argument("--search",type=str,dest="search_text",default='',
                     help="Highlight a regular expression match in the browser.")

    parser.add_argument("files",type=str, nargs='*',
                     help="Files/Paths to be opened")
    opts=parser.parse_args()
    if opts.console_format:
        opts.console=True
    else:
        opts.console_format="d"
    # boxchars:
    # [ "top left",       "top delimiter", "top right",  
    #   "left underline", "underline delimiter","right underline", 
    #   "bottom left",    "bottom delimiter",  "bottom right", 
    #   "line left",      "line delimiter"  ,  "line right",  
    #   "horizontal character"]
    opts.boxchars=[".","-",".",
                   "|","+","|",
                   "'","-","'",
                   "|","|","|",
                   "-" ]
    opts.boxchars[10]=opts.delimiter
    if opts.console_format in ("e","E"):
        opts.boxchars=["\xe2\x94\x8c","\xe2\x94\xac","\xe2\x94\x90",
                       "\xe2\x94\x9c","\xe2\x94\xbc","\xe2\x94\xa4",
                       "\xe2\x94\x94","\xe2\x94\xb4","\xe2\x94\x98",
                       "\xe2\x94\x82","\xe2\x94\x82","\xe2\x94\x82",
                       "\xe2\x94\x80" ]
    if opts.console_format=="m":
        opts.boxchars=["","","",
                       ""," ","",
                       "","","",
                       ""," ","",
                       "-" ]
    if opts.console_format=="M":
        opts.boxchars=["","","",
                       "","|","",
                       "","","",
                       ""," | ","",
                       "-" ]
    # Detect if we're being piped                 
    if (not sys.stdout.isatty()):
        opts.console=True
    if (len(opts.files)==0 and sys.stdin.isatty()):
        parser.print_usage()
        sys.exit(0)
    if len(opts.indelimiter)==0:
        opts.indelimiter=["\t"]
    opts.indelimiter=[s.decode('string_escape') for s in opts.indelimiter]
    if opts.console_format!="d":
        opts.delimiter=opts.boxchars[10]
    if opts.statistics:
        opts.console=True
        if opts.delimiter=="|":
            opts.delimiter="\t"
    if opts.format:
        opts.format=[s.strip() for s in opts.format.split(",")]
    return opts

def file_list(pathlist):
    ''' Returns an extended list of files, if any of the paths listed is a folder 
        [file1 dir1] -> [file1 dir1/file2 dir1/file3]
    '''
    returnlist=[]
    for p in pathlist:
        if not os.path.exists(p):
            sys.stderr.write("File not found: '"+p+"'\n")
            continue
        if os.path.isfile(p):
            returnlist.append(p)
        if os.path.isdir(p):
            returnlist_last=[]
            for filename in sorted(os.listdir(p)):
                if os.path.isfile(os.path.join(p,filename)):
                    if filename.startswith(".") or filename.startswith("_"):
                        returnlist_last.append(os.path.join(p, filename))
                    else:
                        returnlist.append(os.path.join(p, filename))
            returnlist.extend(returnlist_last)
    return returnlist

def go_to_location(stdscr,filerows, widths,offset,opts):
    ''' Go to a location in table '''
    if opts.freeze:
        offset=(offset[0]+1,offset[1]+1)
    maxsize=stdscr.getmaxyx()
    searchwin=curses.newwin(3,30,2,1)
    curses.curs_set(1)
    searchwin.border()
    searchwin.addstr(0,1,'Go to: (row,col)')
    textwin=curses.newwin(1,28,3,2)
    padarea=curses.textpad.Textbox(textwin,insert_mode=True)
    textwin.addstr(0,0,str(offset[0]-1)+","+str(offset[1]+1))
    textwin.move(0,0)
    searchwin.refresh()
    textwin.refresh()
    new=padarea.edit().split(",")
    if len(new)==1:
        new.append('1')
    curses.curs_set(0)
    try:
        offset=(int(new[0].strip())+1,int(new[1].strip())-1)
    except:
        pass
    if opts.freeze:
        offset=(offset[0]-1,offset[1]-1)
    offset=curses_in_display_range(offset,filerows,widths)
    return offset

def edit_formatting(stdscr,opts):
    ''' Edit the formatting of the table '''
    if not opts.format:
        opts.format=["%s"]
    edit_value=",".join(opts.format)
    maxsize=stdscr.getmaxyx()
    editwin=curses.newwin(5,50,2,1)
    curses.curs_set(1)
    editwin.border()
    editwin.addstr(1,1,'Formatting: single value or comma sep. list')
    editwin.addstr(2,1,'of %s,%d,%f,%.3f,%g.. * as last char. to repeat')
    textwin=curses.newwin(1,48,5,2)
    padarea=curses.textpad.Textbox(textwin,insert_mode=True)
    textwin.addstr(0,0,edit_value)
    #textwin.move(0,0)
    while True:
        editwin.refresh()
        textwin.refresh()
        new=padarea.edit().strip()
        if new=="":
            new="%s"
        
        try:
            for n in new.split(","):
                test_format=n % 0
            break
        except:
            pass
    opts.format=[s.strip() for s in new.split(",")]
    if len(opts.format)==1 and opts.format[0]=="%s":
        opts.format=False
    return opts

def search_table(stdscr,data,offset,opts):
    ''' Search a regexp in the table, return the location '''
    if opts.freeze:
        offset=(offset[0]+1,offset[1]+1)
    maxsize=stdscr.getmaxyx()
    searchwin=curses.newwin(3,maxsize[1]-4,2,1)
    curses.curs_set(1)
    searchwin.border()
    searchwin.addstr(0,1,'Search: (regex)')
    textwin=curses.newwin(1,maxsize[1]-6,3,2)
    padarea=curses.textpad.Textbox(textwin)
    textwin.addstr(0,0,opts.search_text)
    ## debug
    #searchwin.addstr(0,15,str(offset[0])+'x'+str(offset[1]))
    searchwin.refresh()
    textwin.refresh()
    opts.search_text=padarea.edit()
    curses.curs_set(0)
    opts.search_text=opts.search_text.strip().lower()
    if len(opts.search_text)==0:
        if opts.freeze:
            offset=(offset[0]-1,offset[1]-1)
        return offset
    try:
        foore=re.compile(opts.search_text)
    except:
        searchwin.addstr(0,1,'Expression not valid')
        searchwin.refresh()
        inkey=stdscr.getch()
        return offset
    searchwin.border()    
    searchwin.addstr(0,1,'Searching: ')
    searchwin.refresh()
    newoffset=searcher(data,opts.search_text,(offset[0], offset[1]+1))
    # If there are no matches, start from the upper left corner again.
    if newoffset==None:
        newoffset=searcher(data,opts.search_text,(1,0))
        if newoffset==None:
            searchwin.addstr(0,1,'No matches found')
            searchwin.refresh()
            inkey=stdscr.getch()
        else:
            offset=newoffset
    else:
        offset=newoffset
    if opts.freeze:
        offset=(offset[0]-1,offset[1]-1)
    
    return offset

def searcher(hay,needle,offset):
    ''' Search a table for substring.'''
    try:
        searchre=re.compile(needle)
    except:
        return None
    r=1
    for row in hay:
        rows=len(row)
        rowlower=[ i.lower() for i in row ]
        for c in range(rows):
            if (r*rows + c) < (offset[0]*rows + offset[1]):
                continue
            #if needle in rowlower[c]:
            if searchre.search(rowlower[c]):
                offset=(r,c)
                return offset
        r=r+1
    return None

def table_print(filename,opts):
    ''' Print a table on the console '''
    stdin=filename==sys.stdin
    keep_in_memory=True
    reader=table_reader(filename,opts,keep_in_memory)
    (collength,rows)=reader.get_dims()
    rowsstrlen=max(2,len(str(rows)))
    if len(collength)==0:
        return
    padder=pad
    if opts.align.startswith("l"):
        numeric=[False]*len(collength)
    if opts.align.startswith("r"):
        numeric=[True]*len(collength)
    if opts.align.startswith("c"):
        numeric=[True]*len(collength)
        padder=cpad
    if opts.align.startswith("a"):
        numeric=reader.get_numeric()
    if opts.colwidth==0 or opts.colwidth>max(collength):
        opts.colwidth=max(collength)
    collength=[min(opts.colwidth,i) for i in collength]
    collength=[max(opts.colminwidth,i) for i in collength]
    boxed=False
    topboxed=False
    linesboxed=False
    if opts.console_format in ("m","M"):
        collength=[i+1 for i in collength]
    if opts.console_format=="M":
        boxed=True
    if opts.console_format in ("a","e","A","E"):
        boxed=True
        topboxed=True
    if opts.console_format in ("A","E"):
        linesboxed=True
    line_end='\n'
    if boxed:
        line_end=opts.boxchars[11]+'\n'
    # If source is a file we can re-read the file, and not store it in memory
    #~ if not keep_in_memory:
    #~ reader.open()
    first_row=True
    row_number=0
    if topboxed:
        sys.stdout.write(opts.boxchars[0])
        if opts.numbers:
            sys.stdout.write(opts.boxchars[12]*rowsstrlen)
            sys.stdout.write(opts.boxchars[1])
        for c in range(len(collength)):
            sys.stdout.write(opts.boxchars[12]*collength[c])
            if c<len(collength)-1:
                sys.stdout.write(opts.boxchars[1])
        sys.stdout.write(opts.boxchars[2]+'\n')

    if opts.header and not stdin:
        if boxed:
            sys.stdout.write(opts.boxchars[9])
        if opts.numbers:
            sys.stdout.write(padder("#", rowsstrlen, False))
            sys.stdout.write(opts.delimiter)
        for c in range(len(collength)):
            sys.stdout.write(padder(str(c+1), collength[c], not numeric[c]))
            if c<len(collength)-1:
                sys.stdout.write(opts.boxchars[9])
        sys.stdout.write(line_end)
        first_row=False
        row_number+=1
        # underline for generared header
        if opts.console_format!="d":
            sys.stdout.write(opts.boxchars[3])
            for c in range(len(collength)):
                sys.stdout.write(opts.boxchars[12]*collength[c])
                if c<len(collength)-1:
                    sys.stdout.write(opts.boxchars[4])
            sys.stdout.write(opts.boxchars[5]+'\n')
    
    for row in reader.get_data():
    #for row in reader:
        if not row: continue
        if linesboxed and not first_row :
            sys.stdout.write(opts.boxchars[3])
            if opts.numbers:
                sys.stdout.write(opts.boxchars[12]*rowsstrlen)
                sys.stdout.write(opts.boxchars[4])
            for c in range(len(collength)):
                sys.stdout.write(opts.boxchars[12]*collength[c])
                if c<len(collength)-1:
                    sys.stdout.write(opts.boxchars[4])
            sys.stdout.write(opts.boxchars[5]+'\n')
        if boxed:
            sys.stdout.write(opts.boxchars[9])
        if opts.numbers:
            if first_row:
                sys.stdout.write(padder("#", rowsstrlen, False))
            else:
                sys.stdout.write(padder(str(row_number), rowsstrlen, False))
            sys.stdout.write(opts.boxchars[10])
            row_number+=1
        cols=len(row)
        for c in range(cols):
            sys.stdout.write(padder(row[c], collength[c], not numeric[c]).encode('utf-8'))
            if c<cols-1:
                sys.stdout.write(opts.boxchars[10])
        sys.stdout.write(line_end)
        if first_row:
            first_row=False
            if opts.console_format!="d":
                sys.stdout.write(opts.boxchars[3])
                if opts.numbers:
                    if opts.console_format=="M":
                        underline=markdown_align(opts.boxchars[12],rowsstrlen-1,c,opts.align,True)
                    else:
                        underline=opts.boxchars[12]*(rowsstrlen)
                    sys.stdout.write(underline)
                    sys.stdout.write(opts.boxchars[4])
                for c in range(len(collength)):
                    if opts.console_format=="M":
                        c_col=c+1 if opts.numbers else c
                        underline=markdown_align(opts.boxchars[12],collength[c],c_col,opts.align,numeric[c])
                    else:
                        underline=opts.boxchars[12]*(collength[c])
                    sys.stdout.write(underline)
                    
                    if c<len(collength)-1:
                        sys.stdout.write(opts.boxchars[4])
                sys.stdout.write(opts.boxchars[5]+'\n')
            
    if topboxed:
        sys.stdout.write(opts.boxchars[6])
        if opts.numbers:
            sys.stdout.write(opts.boxchars[12]*rowsstrlen)
            sys.stdout.write(opts.boxchars[7])
        for c in range(len(collength)):
            sys.stdout.write(opts.boxchars[12]*collength[c])
            if c<len(collength)-1:
                sys.stdout.write(opts.boxchars[7])
        sys.stdout.write(opts.boxchars[8]+'\n')

def str_array(array_in,header=True,options=""):
    ''' Use in a python session: Format a table and return as string.
    Get options with "ncsv -h"
    set header=True if your array has header names as first row.
    set header as list of strings to create a custom header
    
    y=[[-5,5,-5.03],[4,5,6],[7,8.43,3]]
    print(ncsv.str_array(y))
    y.insert(0,['one','two','three'])
    print(ncsv.str_array(y,True, '--cf m -a a'))
    '''
    if len(array_in)==0:
        return ""
    s=[None]*len(array_in)
    if not header:
        options="--nh "+options
    for i,r in enumerate(array_in):
        s[i]="\t".join([str(x) for x in r])
    if type(header) == list:
        s.insert(0,"\t".join(header))
    s="\n".join(s)
    
    return call_self(s,options)

def str_list_dict(dict_in,options=""):
    ''' Use in a python session: Format a table and return as string.
    Get options with "ncsv -h" 
        
        d=[{'foo':1, 'faa':2},
           {'foo':False, 'faa':8.234},
           {'boo':00, 'faa':118.234},]
        print(ncsv.str_list_dict(d))
    '''
    if len(dict_in)==0:
        return ""
    s=[None]*(len(dict_in)+1)
    header=[]
    for row in dict_in:
        for x in row:
            if x not in header:
                header.append(x)
    s[0]="\t".join(header)
    for i,r in enumerate(dict_in):
        row=[]
        for h in header:
            if h in r:
                row.append(str(r[h]))
            else:
                row.append("")
        s[i+1]="\t".join(row)
    s="\n".join(s)
    return call_self(s,options)

def str_dict_list(dict_in,options=""):
    ''' Use in a python session: Format a table and return as string.
        Get options with "ncsv -h" 
    
    dl={
        'foob': [1,2,3,4,5,6,7],
        'geez': [4,6,2,5,10.0001]
       }
    
    print(ncsv.str_dict_list(dl))        
    '''
    if len(dict_in)==0:
        return ""
    rows=max([len(dict_in[x]) for x in dict_in])
    header=dict_in.keys()
    s=[None]*(rows+1)
    s[0]="\t".join(header)
    for i in range(rows):
        row=[]
        for h in header:
            if len(dict_in[h])>i:
                row.append(str(dict_in[h][i]))
            else:
                row.append("")
        s[i+1]="\t".join(row)
    s="\n".join(s)
    return call_self(s,options)
    
def call_self(str_in, options):
    ''' Use in a python session: Call self as executable, and return output string '''
    # Cheap trick, just call us in a shell:
    import shlex,subprocess
    command=['python',os.path.realpath(__file__)]
    command.extend(shlex.split(options))
    proc=subprocess.Popen(command,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE)
    proc.stdin.write(str_in)
    proc.stdin.close()
    result = proc.stdout.read()
    exit_code=proc.wait()
    if exit_code>0:
        raise RuntimeError("Error in running ncsv")
    return result


def markdown_align(s,length,coln,align,numeric=False):
    if coln==0:
        length-=1
    if align.startswith("l"):
        underline=":"+s*(length+1)
    if align.startswith("r"):
        underline=s*(length+1)+":"
    if align.startswith("c"):
        underline=":"+s*(length)+":"
    if align.startswith("a"):
        if numeric:
            underline=s*(length+1)+":"
        else:
            underline=":"+s*(length+1)
    
    return underline
        

def pad(s, max_length, right=True):
    ''' Returns a padded string '''
    if right:
        return s[:max_length].ljust(max_length)
    else:
        return s[:max_length].rjust(max_length)

def cpad(s, max_length, foo=True):
    ''' Returns a center padded string '''
    return s[:max_length].center(max_length)

def console_print(opts,filename):
    ''' Main function for table printing '''
    try:
        table_print(filename,opts)
    except IOError:
        pass
    except KeyboardInterrupt:
        pass    

def curses_print(reader,stdscr,collength,opts,offset,scrsize,coloffset):
    ''' Print a table in curses '''
    if opts.freeze:
        offset=(offset[0]+1,offset[1]+1)
    rowsstrlen=len(str(len(reader.get_data())))
    collength=[min(opts.colwidth,i) for i in collength]
    collength=[max(opts.colminwidth,i) for i in collength]
    numeric=reader.get_numeric()
    sortcol=reader.get_sort_col()
    searchre=False
    if len(opts.search_text)>0:
        try:
            searchre=re.compile(opts.search_text)
        except:
            pass
    y=0
    x=0
    endX=0
    r=1
    # Clear end of rows for remaining characters.. 
    for y_end in range(scrsize[0]-1):
        try:
            stdscr.addch(y_end,scrsize[1]-1,ord(" "))
        except:
            pass
    # Print header
    if offset[0]==1 or opts.freeze:
        x=0
        if opts.numbers:
            x=rowsstrlen+1
            stdscr.addstr(y,0,pad('#', rowsstrlen, False),opts.style_head)
            stdscr.addch(y,rowsstrlen,curses.ACS_VLINE,opts.style_del_head)
        header=reader.get_data()[0]
        cols=len(header)
        for c in range(cols):
            if c<offset[1]:
                if c==0 and opts.freeze:
                    pass
                else:
                    continue
            delchar=curses.ACS_VLINE
            pad_col=cpad(header[c], collength[c])
            if opts.numbers and not opts.header:
                col_n_str='#'+str(c+1)
                pad_col=pad_col[:-len(col_n_str)]+col_n_str
            if x+3>scrsize[1]:
                break
            if x+collength[c] >= scrsize[1]:
                endlen=min(scrsize[1]-x-1,len(pad_col))
                pad_col=cpad(header[c], endlen)
            else:
                endlen=min(len(pad_col),collength[c])
            if sortcol==c:
                if reader.is_sort_ascending():
                    delchar=ord('+')
                else:
                    delchar=ord('-')
            if coloffset[c]>0:
                delchar=ord('<')
            if endlen>=0:
                stdscr.addstr(y,x,
                              pad_col[0:(endlen)],
                              opts.style_head)
                x=x+collength[c]
                if (c<cols) and (x+1 < scrsize[1]):
                    stdscr.addch(y,x,delchar,opts.style_del_head)
                    x+=1
            endX=x
        # fill the rest of columns with blanks
        if x<scrsize[1]:
            stdscr.addstr(y,x," "*(scrsize[1]-x-1),opts.style_str)
        y+=1

    # Print data columns
    if opts.freeze or y==0:
        r=offset[0]-1
    else:
        r=offset[0]
    for row in reader.get_data()[r:]:
        r=r+1
        x=0
        # break the for loop before y-axis is used up
        if y>=scrsize[0]:
            break
        if opts.numbers:
            x=rowsstrlen+1
            delchar=curses.ACS_VLINE
            delstyle=opts.style_del
            if opts.cursor==y+1:
                delchar=curses.ACS_DIAMOND
                delstyle=opts.style_del_high
            stdscr.addstr(y,0,pad(str(r-1), rowsstrlen, False),opts.style_num)
            stdscr.addch(y,rowsstrlen,delchar,delstyle)
        cols=len(row)
        for c in range(cols):
            if c<offset[1]:
                if c==0 and opts.freeze:
                    pass
                else:
                    continue
            if coloffset[c]==0:
                offset_col=row[c]
            else:
                if numeric[c]:
                    last_char=len(row[c])-coloffset[c]
                    last_char=max(1,last_char)
                    offset_col=row[c][:last_char]
                else:
                    offset_col=row[c][coloffset[c]:]
            pad_col=pad(offset_col, collength[c], not numeric[c])
            if x+3>scrsize[1]:
                break
            if x+collength[c] >= scrsize[1]:
                endlen=min(scrsize[1]-x-1,len(pad_col))
            else:
                endlen=min(len(pad_col),collength[c])
            fontattr=opts.style_col[c]
            if (c==offset[1]):
                fontattr=curses.A_BOLD+fontattr
            delchar=curses.ACS_VLINE
            delstyle=opts.style_del
            if opts.cursor==y+1:
                delchar=curses.ACS_DIAMOND
                delstyle=opts.style_del_high
            if (opts.freeze and c==0):
                fontattr=opts.style_col_freeze
            if searchre:
                if searchre.search(row[c].lower()):
                    fontattr=opts.style_high
            if endlen>=0:
                stdscr.addstr(y,x,
                              pad_col[0:(endlen)],
                              fontattr)
                x=x+endlen
                if endlen<len(offset_col):
                    delchar=ord('>')
                    if x<scrsize[1] and x+2>scrsize[1]:
                        stdscr.addch(y,x-1,delchar,delstyle)
                if x+1 < scrsize[1]:
                    stdscr.addch(y,x,delchar,delstyle)
                    x=x+1
            endX=x
        # fill the rest of columns with blanks
        
        if x<scrsize[1]:
            stdscr.addstr(y,x," "*(scrsize[1]-x-1), opts.style_str)

        y+=1
    # fill the rest of rows with blanks
    if y<scrsize[0]:
        for r in range(scrsize[0]-y):
            stdscr.addstr(y+r,0," "*(scrsize[1]-1))
        # Draw the bottom line
        for x in range(endX-1):
            try:
                if x-1<scrsize[1]:
                    stdscr.addch(y,x,curses.ACS_HLINE, opts.style_del)
            except:
                pass
        if endX<scrsize[1]:
            stdscr.addstr(y,endX," "*(scrsize[1]-endX-1), opts.style_str)
        x=0
        if opts.numbers:
            x=rowsstrlen
            stdscr.addch(y,x,curses.ACS_BTEE,opts.style_del)
            x+=1
        for c in range(cols):
            if c<offset[1]:
                if c==0 and opts.freeze:
                    pass
                else:
                    continue
            x=x+collength[c]
            delchar=curses.ACS_BTEE
            if c==cols-1:
                delchar=curses.ACS_LRCORNER
            if x+1 < scrsize[1]:
                stdscr.addch(y,x,delchar,opts.style_del)
                x=x+1
    return

def curses_print_help(stdscr,opts):
    ''' Create a window with help message '''
    helptext=get_interactive_help_text().split('\n')
    helpwin=curses.newwin(2+len(helptext),40,1,1)
    helpwin.border()
    y=1
    helpwin.addstr(0,2,'Keyboard commands:')
    for row in helptext:
        helpwin.addstr(y,1,row)
        y=y+1
    #helpwin.addstr(y+2,2,'Current file: '+opts.fileid)
    helpwin.refresh()
    while 1:
        inkey=stdscr.getch()
        break

def curses_stats_browser(stdscr,scrsize,data,filename):
    
    statwin=curses.newwin(5,20,1,1)
    statwin.border()
    statwin.addstr(0,1,'Info:')
    statwin.addstr(3,1,'Calculating ...')
    statwin.refresh()
    #try:
    stats=column_stats(data)
    #except:
    #    stats=False
    heads=len(data[0])
    line=0
    while 1:
        if line<0:
            line=0
        if line>(heads-scrsize[0]+6):
            line=heads-scrsize[0]+6
        if scrsize[0]>heads+6:
            line=0
        if stats:
            curses_print_stats(stdscr,data,filename,stats,line)
        else:
            curses_print_stats_nonumeric(stdscr,data,filename,line)
        while 1:
            inkey=stdscr.getch()
            if inkey==curses.KEY_DOWN or inkey==ord('B'):
                line+=1
            if inkey==curses.KEY_UP or inkey==ord('A'):
                line-=1
            if inkey==54: # PGDN
                line+=15
            if inkey==53: # PGUP
                line-=15
            if inkey in [ord('c'),ord('q')]:
                return
            break
    return

def curses_print_stats(stdscr,data,filename,stats,line):
    ''' Create a window with file stats '''
    
    # Note: many of the arbitrary looking numbers derive from the string
    #       lengths below.
    head=[i.strip() for i in data[0]]
    cols=len(head)
    rows=len(data)-1
    lengths=[len(i.strip()) for i in head]
    if filename==sys.stdin:
        fullfilename='stdin'
    else:
        fullfilename=os.path.abspath(filename)[-60:]
    headmax=max(lengths)
    lengthsmax=max(headmax,15)+2
    headmax=max([lengthsmax+73,len(fullfilename)+12])
    statwin=curses.newwin(5+cols,headmax,1,1)
    statwin.border()
    statwin.addstr(0,1,'Info:')
    statwin.addstr(1,1,'File name: '+fullfilename)
    statwin.addstr(2,1,'Cols,Rows: '+str(cols)+','+str(rows))
    statwin.addstr(3,1,'Column names:')
    statwin.addstr(3,lengthsmax,'Mean:     Max:      Min:      Sum:      StDev:    NAs:  Uniq:')
    [means,maxs,mins,sums,varis,nans,uniqs]=stats
    y=4
    w=10
    for c in range(len(head)-line):
        statwin.addstr(y,1,head[c+line])
        statwin.addstr(y,(0*w)+lengthsmax,means[c+line])
        statwin.addstr(y,(1*w)+lengthsmax,maxs[c+line])
        statwin.addstr(y,(2*w)+lengthsmax,mins[c+line])
        statwin.addstr(y,(3*w)+lengthsmax,sums[c+line])
        statwin.addstr(y,(4*w)+lengthsmax,varis[c+line])
        statwin.addstr(y,(5*w)+lengthsmax,nans[c+line])
        statwin.addstr(y,(5*w)+6+lengthsmax,uniqs[c+line])
        y=y+1
    statwin.refresh()
    
def curses_print_stats_nonumeric(stdscr,data,filename,line):
    ''' Create a window with file stats, without numeric values '''
    
    # Note: many of the arbitrary looking numbers derive from the string
    #       lengths below.
    head=data[0]
    cols=len(head)
    rows=len(data)-1
    lengths=[len(i.strip()) for i in head]
    fullfilename=os.path.abspath(filename)[-60:]
    headmax=max(lengths)
    lengthsmax=max(headmax,15)+2
    headmax=max([lengthsmax+73,len(fullfilename)+12])
    statwin=curses.newwin(5+cols,headmax,1,1)
    statwin.border()
    statwin.addstr(0,1,'Info:')
    statwin.addstr(1,1,'File name: '+fullfilename)
    statwin.addstr(2,1,'Cols,Rows: '+str(cols)+','+str(rows))
    statwin.addstr(3,1,'Column names:')
    y=4
    for c in range(len(head)-line):
        statwin.addstr(y,1,head[c+line])
        y=y+1
    statwin.refresh()

def curses_in_display_range(offset,filerows,widths):
    ''' Change the display position of curses table '''
    offsety=min(filerows,offset[0])
    offsety=max(1,offsety)
    offsetx=min(len(widths)-1,offset[1])
    offsetx=max(0,offsetx)
    return (offsety, offsetx)

def is_number(s,na_re=False):
    ''' Check if string is float '''
    # na_re:  re object, If matches, returns False
    
    if na_re:
        is_na=na_re.match(s)
        if is_na: # Matches to NA search
            return False
    try:
        converted=float(s)
        return True # converts to float
    except:
        return False # Does not convert, does not match to NA search

def column_stats(data):
    ''' Count statistics of each column in the data '''
    from math import sqrt,isnan
    column_sum=[0]*len(data[0])
    column_sumsq=[0]*len(data[0])
    column_numeric=[True]*len(data[0])
    column_nas=[0]*len(data[0])
    column_max=[float('-inf')]*len(data[0])
    column_min=[float('inf')]*len(data[0])
    
    for row in data[1:]:
        for col in range(len(row)):
            if row[col].strip()=='nan':
                column_nas[col]+=1
                continue
            if column_numeric[col]:
                try:
                    value=float(row[col])
                    column_sum[col]+=value
                    column_sumsq[col]+=value*value
                    column_max[col]=max(column_max[col],value)
                    column_min[col]=min(column_min[col],value)
                except:
                    column_numeric[col]=False
    column_uniqs=[0]*len(data[0])
    for col in range(len(data[0])):
        column_uniqs[col]=len(set( [row[col] for row in data[1:] if len(row)>col] ))
       
    column_means=[]
    column_sds=[]
    for x,csum in enumerate(column_sum):
        try:
            column_means.append(csum/(len(data)-1-column_nas[x]))
        except:
            column_means.append(float('nan'))
        try:
            column_sds.append(sqrt((column_sumsq[x] - column_sum[x]*column_means[x])/(len(data)-1-column_nas[x])))
        except:
            column_sds.append(float('nan'))
    
    stats=format_stats([column_means,column_max,column_min,column_sum,column_sds,column_nas,column_uniqs],column_numeric)
    return stats

def format_stats(stats,numeric):
    ''' Returns a formatted string version of a numerical table '''
    for f,feature in enumerate(stats):
        epxf=['%1.2e'%i for i in feature]
        genf=['%.4g'%i for i in feature]
        for x,isnum in enumerate(numeric):
            if (not isnum) and (f < 5):
                stats[f][x]=''
                continue
            if len(epxf[x])<len(genf[x]):
                # Return the exponential form if it is shorter notation
                stats[f][x]=epxf[x]
            else:
                stats[f][x]=genf[x]
            
    return stats

def maxcol_change(opts,collength,scrmax,dval):
    ''' Change the value of maximum column width '''
    if opts.colwidth+dval<1:
        return opts
    if opts.colwidth+dval>scrmax-2:#max(collength):
        return opts
    if opts.colwidth+dval>max(collength):
        return opts
    opts.colwidth=opts.colwidth+dval
    return opts
    
def widthoffset_change(opts,offset,widths,widthoffset,dval):
    ''' Change the value of current width-wise offset '''
    if opts.freeze:
        offset=(offset[0]+1,offset[1]+1)
    newval=widthoffset[offset[1]]+dval
    if newval<0:
        newval=0
    if newval>widths[offset[1]]-1:
        newval=widths[offset[1]]-1
    widthoffset[offset[1]]=newval
    return widthoffset
    
def curses_freezer(opts,offset):
    ''' toggle curses first column and row freezing '''
    if opts.freeze:
        if offset[1]>1:
            offset=(offset[0]+1, offset[1]+1)
        else:
            offset=(offset[0]+1, offset[1])
    else:
        offset=(offset[0]-1, offset[1]-1,)
    opts.freeze=not opts.freeze
    return (opts,offset)

def curses_browser(opts,filename):
    ''' Main function for curses printing '''
    global curses
    import curses
    import curses.textpad
    global re
    import re
    import traceback
    stdscr=curses.initscr()
    if opts.colors:
        curses.start_color()
        curses.use_default_colors()
        if opts.dark_colors:
            curses.init_pair(2, curses.COLOR_BLUE, -1)
            curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_YELLOW)
            curses.init_pair(4, curses.COLOR_RED, -1)
            curses.init_pair(5, -1, -1)
            curses.init_pair(6, curses.COLOR_MAGENTA, -1)
        else:
            curses.init_pair(2, curses.COLOR_GREEN, -1)
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) 
            curses.init_pair(4, curses.COLOR_CYAN, -1)
            curses.init_pair(5, curses.COLOR_WHITE, -1)
            curses.init_pair(6, curses.COLOR_RED, -1)
        
    if opts.colors:
        opts.style_head=curses.color_pair(3)+curses.A_BOLD
        opts.style_col_freeze=curses.color_pair(3)+curses.A_BOLD
        opts.style_del=curses.color_pair(2)
        opts.style_del_head=opts.style_del
        opts.style_del_high=curses.color_pair(2)+curses.A_BOLD
        opts.style_num=curses.color_pair(4)
        opts.style_str=curses.color_pair(5)
        opts.style_high=curses.color_pair(6)+curses.A_UNDERLINE+curses.A_BOLD
    else:
        opts.style_head=curses.A_BOLD
        opts.style_col_freeze=curses.A_BOLD
        opts.style_del=curses.A_DIM
        opts.style_del_head=opts.style_del
        opts.style_del_high=curses.A_BOLD
        opts.style_num=curses.A_DIM
        opts.style_str=curses.A_DIM
        opts.style_high=curses.A_BOLD+curses.A_UNDERLINE
    if not opts.colors or curses.termname().startswith('putty'):
        # disable fancy vertical line 
        curses.ACS_VLINE='|'
        curses.ACS_HLINE='-'
        curses.ACS_BTEE='+'
        curses.ACS_LLCORNER="'"
        curses.ACS_LRCORNER="'"
        curses.ACS_DIAMOND="*"
    curses.curs_set(0)
    curses.noecho()

    opts.cursor=0
    offset=(1,0)
    try:
        reader=table_reader(filename,opts,True)
        (widths,filerows)=reader.get_dims()
        if len(widths)==0:
            return stdscr
        if opts.colwidth==0 or opts.colwidth>max(widths):
            opts.colwidth=min( max(widths), stdscr.getmaxyx()[1]-2)
        widthoffset=[0 for i in widths]
        opts.colshow=[True for i in widths]
        opts.style_col=[opts.style_str]*len(widths)
        numeric=reader.get_numeric()
        for is_n in range(len(numeric)):
            if numeric[is_n]:
                opts.style_col[is_n]=opts.style_num
    except:
        curses.nocbreak()
        stdscr.keypad(0)
        curses.endwin()
        print("Error in reading the file:")
        traceback.print_exc()
        sys.exit(1)
    try:
        if filename==sys.stdin:
            ftty=open("/dev/tty")
            os.dup2(ftty.fileno(), 0)
        status_text=None
        while 1:
            curses_print(reader,stdscr,widths,opts,offset,stdscr.getmaxyx(),widthoffset)
            if status_text:
                try:
                    stdscr.addstr(0,stdscr.getmaxyx()[1]-len(status_text)-1,status_text, opts.style_high)
                except:
                    pass
                status_text=None
            while 1:
                inkey=stdscr.getch()                
                if inkey==curses.KEY_DOWN or inkey==ord('B'):
                    offset=curses_in_display_range((offset[0]+1, offset[1]), filerows, widths)
                if inkey==curses.KEY_UP or inkey==ord('A'):
                    offset=curses_in_display_range((offset[0]-1, offset[1]), filerows, widths)
                if inkey==curses.KEY_RIGHT or inkey==ord('C'):
                    offset=curses_in_display_range((offset[0], offset[1]+1), filerows, widths)
                if inkey==curses.KEY_LEFT or inkey==ord('D'):
                    offset=curses_in_display_range((offset[0], offset[1]-1), filerows, widths)
                if inkey==54 or inkey==32: # PGDN or space
                    page_shift=stdscr.getmaxyx()[0]-opts.freeze
                    offset=curses_in_display_range((offset[0]+page_shift, offset[1]), filerows, widths)
                if inkey==53: # PGUP
                    page_shift=stdscr.getmaxyx()[0]-opts.freeze
                    offset=curses_in_display_range((offset[0]-page_shift, offset[1]), filerows, widths)
                if inkey in (curses.KEY_HOME,72,49,ord('P')): # HOME
                    offset=(1, offset[1])
                if inkey in (curses.KEY_END,70,52,ord('G')): # END
                    offset=curses_in_display_range((filerows-stdscr.getmaxyx()[0]+1, offset[1]), filerows, widths)
                if inkey==ord('a'):
                    opts.cursor=max(0,opts.cursor-1)
                    status_text='HL '+str(opts.cursor)
                if inkey==ord('z'):
                    opts.cursor=min(stdscr.getmaxyx()[0],opts.cursor+1)
                    status_text='HL '+str(opts.cursor)
                if inkey==ord('c'):
                    curses_stats_browser(stdscr,stdscr.getmaxyx(),reader.get_data(),filename)
                if inkey==ord('f'):
                    (opts,offset)=curses_freezer(opts,offset)
                    offset=curses_in_display_range(offset, filerows, widths)
                if inkey in [ord('g'), ord(':')]:
                    offset=go_to_location(stdscr,filerows, widths,offset,opts)
                if inkey==ord('h'):
                    curses_print_help(stdscr,opts)
                if inkey==ord('n'):
                    opts.numbers=not opts.numbers
                if inkey==ord('o'):
                    reader.sort_table(offset[1])
                if inkey==ord('q'):
                    return stdscr
                if inkey==ord('S'):
                    if filename!=sys.stdin:
                        opts=edit_formatting(stdscr,opts)
                    else:
                        status_text='Can not reformat with stdin input'
                        break
                if inkey in (ord('r'),ord('S')):
                    if filename==sys.stdin:
                       status_text='Can not reload with stdin input'
                       break 
                    try:
                        reader.read()
                        (widths,filerows)=reader.get_dims()
                        widthoffset=[0 for i in widths]
                        opts.colshow=[True for i in widths]
                        opts.style_col=[opts.style_str]*len(widths)
                        numeric=reader.get_numeric()
                        for is_n in range(len(numeric)):
                            if numeric[is_n]:
                                opts.style_col[is_n]=opts.style_num
                        offset=curses_in_display_range(offset, filerows, widths)
                        status_text='Reread file'
                    except:
                        status_text='Error reading file'
                if inkey in (ord('s'), ord('/')):
                    offset=search_table(stdscr,reader.get_data(),offset,opts)
                if inkey==ord('t'):
                    reader.transpose_table()
                    (widths,filerows)=reader.get_dims()
                    if opts.colwidth==0 or opts.colwidth>max(widths):
                        opts.colwidth=max(widths)
                    widthoffset=[0 for i in widths]
                    opts.colshow=[True for i in widths]
                    opts.style_col=[curses.A_DIM]*len(widths)
                    numeric=reader.get_numeric()
                    for is_n in range(len(numeric)):
                        if numeric[is_n]:
                            opts.style_col[is_n]=opts.style_num
                    offset=curses_in_display_range(offset, filerows, widths)
                if inkey==ord('-'):
                    opts=maxcol_change(opts,widths,stdscr.getmaxyx()[1],-1)
                    status_text="Max width "+str(opts.colwidth)
                if inkey in (ord('+'),ord('=')):
                    opts=maxcol_change(opts,widths,stdscr.getmaxyx()[1],1)
                    status_text="Max width "+str(opts.colwidth)
                if inkey==ord(','):
                    widthoffset=widthoffset_change(opts,offset,widths,widthoffset,1)
                    status_text="Shift "+str(widthoffset[offset[1]])
                if inkey==ord('.'):
                    widthoffset=widthoffset_change(opts,offset,widths,widthoffset,-1)
                    status_text="Shift "+str(widthoffset[offset[1]])
                if inkey==ord('>'):
                    offset=curses_in_display_range((offset[0], len(widths)), filerows, widths)
                if inkey==ord('<'):
                    offset=curses_in_display_range((offset[0], 0), filerows, widths)
                break
            stdscr.refresh()    
            
        
    except IOError:
        pass
    except KeyboardInterrupt:
        reset_curses(stdscr)
        sys.exit(0)
    except EndProgram:
        pass
    except:
        reset_curses(stdscr)
        print("Unexpected error:")
        print(traceback.format_exc())
        sys.exit(1)
    return stdscr

def stats_from_file(opts,filename):
    """ Print out another CSV, with statistics of the current table  """
    
    reader=table_reader(filename,opts,True)
    dims=reader.get_dims()
    if len(dims[0])==0:
        # no data present
        return
    stats=column_stats(reader.get_data())
    header=[x.encode('utf_8') for x in list(reader.get_data()[0])]
    header.insert(0,'Statistic')
    rows=["Mean","Max","Min","Sum","StDev","NAs","Unique"]
    print(opts.delimiter.join(header))
    for i,stat in enumerate(stats):
        stat.insert(0,rows[i])
        print(opts.delimiter.join(stat))

def main_stdin(opts):
    """ Run things with stdin """
    opts.fileid='<stdin>'
    if opts.statistics:
        stats_from_file(opts,sys.stdin)
        return None
    if opts.console:
        console_print(opts,sys.stdin)
        return None

    stdscr=curses_browser(opts,sys.stdin)
    return stdscr    
    
def main_args(opts,stdscr):
    """ Run things with command line args """
    filelist=file_list([opts.files[fi] for fi in range(len(opts.files))])
    files=len(filelist)
    for fi in range(files):
        opts.fileid=os.path.basename(filelist[fi])
        if opts.statistics:
            stats_from_file(opts,filelist[fi])
            continue
        if opts.console:
            console_print(opts,filelist[fi])
        else:
            stdscr=curses_browser(opts,filelist[fi])
    if stdscr!=None:
        reset_curses(stdscr)

def main():
    opts=setup_options()
    stdscr=None
    # First read stdin
    if (not sys.stdin.isatty()):
        stdscr=main_stdin(opts)
    # Then handle arguments
    main_args(opts,stdscr)

if __name__ == "__main__":
    main()
