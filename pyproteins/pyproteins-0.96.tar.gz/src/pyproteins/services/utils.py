import sys
import os
import errno
import StringIO
import re
import os.path
from types import ModuleType
import stat
import tarfile



def stringToSlice(mystring):
    return slice(*map(lambda x: int(x.strip()) if x.strip() else None, mystring.split(':')))

def nonblank_lines(f):
    for l in f:
        line = l.rstrip()
        if line:
            yield line

'''
Container w/ loading/dumping capabilities for tsv formated text-file
'''
class Tsv(object):
    def __init__(self, stream, ofs='\t', Nskip=0, dataParser=None, headerParser=None):
        self.ofs = ofs
        self.keymap = []
        self.data = []
        self.Nskip = Nskip
        self.dataParser = dataParser
        self.headerParser = headerParser


        if hasattr(stream, 'read'):
            self._loadStream(stream)
        elif isinstance(stream, basestring):
            if os.path.isfile(stream):
                self._loadFile(stream)
            else :
                self._loadString(stream)
        elif isinstance(stream, list):
            self._loadList(stream)
        else:
            raise TypeError('Cant parse/load ' + str(stream) )

    def _loadStream(self, stream):
        for i in range(self.Nskip):
            stream.readline()
        if self.headerParser:
            self.keymap = self.headerParser(stream.readline().replace("\n", ""))
        else:
            self.keymap = stream.readline().replace("\n", "").split(self.ofs)

        if self.dataParser:
            self.data = [ self.dataParser(l) for l in nonblank_lines(stream) ]
        else:
            self.data = [ self._push(l) for l in nonblank_lines(stream) ]



    def _loadList(self, inputList):

        if self.headerParser:
            self.keymap = self.headerParser( inputList[self.Nskip].replace("\n", "") )
        else :
            self.keymap = inputList[self.Nskip].replace("\n", "").split(self.ofs)

        if self.dataParser:
            self.data = [ self.dataParser(l) for l in nonblank_lines(inputList[ (self.Nskip+1): ])]
        else :
            self.data = [ self._push(l) for l in nonblank_lines(inputList[ (self.Nskip+1): ])]


    def _loadFile(self, fPath):
        with open(fPath, 'r') as stream:
            self._loadStream(stream)

    def _loadString(self, inputRaw):
        l = inputRaw.split('\n')
        self._loadList(l)


    def __len__(self):
        return len(self.data)

    def _push(self, inputRaw):
        #print ">" + self.ofs+ "<"
        #print inputRaw
        d = { self.keymap[i] : val for i, val in enumerate( inputRaw.split(self.ofs) ) }
        return d

    def __iter__(self):
        for d in self.data:
            yield d

    def __str__(self):
        asString= ''
        for i,value in enumerate(self.data):
            asString += '# Element n_' + str(i) + '\n'
            for k in self.keymap:
                if k not in value:
                    continue
                asString += '\'' + k + '\' : ' + value[ k ] + '\n'
        return asString

    def write(self):
        asString= '\t'.join(self.keymap) + '\n'
        for d in self :
            buf = [ d[ k ] for k in self.keymap ]
            asString += '\t'.join(buf) + '\n'
        return asString

def bruteDecode(input):
    codecs=["ascii","utf_8","utf_8_sig","big5","big5hkscs","cp037","cp424","cp437","cp500","cp720","cp737","cp775","cp850","cp852","cp855","cp856","cp857","cp858","cp860","cp861","cp862","cp863","cp864","cp865","cp866","cp869","cp874","cp875","cp932","cp949","cp950","cp1006","cp1026","cp1140","cp1250","cp1251","cp1252","cp1253","cp1254","cp1255","cp1256","cp1257","cp1258","euc_jp","euc_jis_2004","euc_jisx0213","euc_kr","gb2312","gbk","gb18030","hz","iso2022_jp","iso2022_jp_1","iso2022_jp_2","iso2022_jp_2004","iso2022_jp_3","iso2022_jp_ext","iso2022_kr","latin_1","iso8859_2","iso8859_3","iso8859_4","iso8859_5","iso8859_6","iso8859_7","iso8859_8","iso8859_9","iso8859_10","iso8859_11","iso8859_13","iso8859_14","iso8859_15","iso8859_16","johab","koi8_r","koi8_u","mac_cyrillic","mac_greek","mac_iceland","mac_latin2","mac_roman","mac_turkish","ptcp154","shift_jis","shift_jis_2004","shift_jisx0213","utf_32","utf_32_be","utf_32_le","utf_16","utf_16_be","utf_16_le","utf_7"]
    for codec in codecs:
        string = self.value.decode(codec)


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def getAvailableTagFile(fPath, nLim=100):
    if os.path.isfile(fPath):
        backUpFileRoot = fPath + '.old'
        backUpFile = backUpFileRoot
        if os.path.isfile(backUpFile):
            for i in range(1, nLim):
                if os.path.isfile(backUpFileRoot + '_' + str(i)):
                    continue
                else:
                    backUpFile = backUpFileRoot + '_' + str(i)
                    break
                raise ValueError, 'Tag number limit exceeded for ' + fPath

        print 'moving previous ' + fPath + ' to ' + backUpFile
        os.rename(fPath, backUpFile)
    return fPath



# inject carriage returns in long string to obtain mutliline fixed width lines
def lFormat(string, nCol=60):
    return ''.join([x+'\n' if (i+1)%nCol == 0 else x for i,x in enumerate(string) ])


# from http://stackoverflow.com/questions/12791997/how-do-you-do-a-simple-chmod-x-from-within-python
def chmodX(filePath):
    st = os.stat(filePath)
    os.chmod(filePath, st.st_mode | stat.S_IEXEC)

def checkEnv(keyList):
    for key in keyList:
        if not os.environ.get(key):
            raise ValueError("Environment variable " + key + " not defined")
    return True


# emulates find unix command
def find(sType='file', **kwargs):

    patt = kwargs['name'].replace("*", ".*")
    if 'path' not in kwargs and 'name' not in kwargs:
        raise ValueError
    if sType == 'file':
        result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(kwargs['path']) for f in filenames if re.match(patt, f)]

    if sType == 'dir':
        result = [os.path.join(dp, d) for dp, dn, filenames in os.walk(kwargs['path']) for d in dn if re.match(patt, d)]

    return result


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def toInStream(inputData):
    if hasattr(inputData, 'read'):
        return inputData
    if os.path.isfile(inputData):
        f = open(inputData, 'r')
        return f

    return StringIO.StringIO(inputData)

def hasMethod(obj, askedMethod):
    l = [method for method in dir(obj) if callable(getattr(obj, method))]
    if askedMethod in l:
        return True
    return False

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise





def rreload(module):
    """Recursively reload modules."""
    reload(module)
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)
        if type(attribute) is ModuleType:
            rreload(attribute)

'''
    parse a tsv file into a list of dictionary, dictionary keys are extracted from the first line (aka column headers)
'''

def tsvToDictList(fileName):
    buffer = tabularFileToList(fileName, separator = "\t")
    print len(buffer)
    keymap = buffer.pop(0)
    print len(buffer)
    data = []
    for d in buffer:
        data.append({})
        for i,x in enumerate(d):
            data[-1][keymap[i]] = x

    return {'keymap' : keymap, 'data' : data}

def tabularFileToList(fileName, separator = ","):

    with open (fileName, "r") as f:
        data = [line.strip('\n').split(separator) for line in f]

    return data