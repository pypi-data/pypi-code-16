#coding:utf-8
import struct,zipfile,re

__author__ = 'creeper'
import os
class Util(object):
    def __init__(self):
        pass

    def getSuffixList(self,path,regex):
        # os.chdir(path)
        # return glob.glob(regex)
        pass

    def isZipFile(self,filename):
        return zipfile.is_zipfile(filename)

    def hasFileInZip(self,path_of_zipfile,filename):
        zf = zipfile.ZipFile('python.zip', 'r')
        return filename in zf

    def _typeList(self):
        return {
        "52617221": "RAR",
        "504B0304": "ZIP",
        "FFD8FF":'JPG',
        }

    def _bytes2hex(self,bytes):
        num = len(bytes)
        hexstr = u""
        for i in range(num):
            t = u"%x" % bytes[i]
            if len(t) % 2:
                hexstr += u"0"
            hexstr += t
        return hexstr.upper()

    def filetype(self,filename):
        binfile = open(filename, 'rb') # 必需二制字读取
        tl = self._typeList()
        ftype = 'unknown'
        for hcode in tl.keys():
            numOfBytes = len(hcode) / 2 # 需要读多少字节
            binfile.seek(0) # 每次读取都要回到文件头，不然会一直往后读取
            hbytes = struct.unpack_from("B"*numOfBytes, binfile.read(numOfBytes)) # 一个 "B"表示一个字节
            f_hcode = self._bytes2hex(hbytes)
            if f_hcode == hcode:
                ftype = tl[hcode]
                break
        binfile.close()
        return ftype

    def delete_file_folder(self,src):
        '''delete files and folders'''
        if os.path.isfile(src):
            try:
                os.remove(src)
            except:
                pass
        elif os.path.isdir(src):
            for item in os.listdir(src):
                itemsrc=os.path.join(src,item)
                self.delete_file_folder(itemsrc)
            try:
                os.rmdir(src)
            except:
                pass

    def hasDirectory(self,rootDir,rfoldername):
        pattern = re.compile("^"+rfoldername+"$")
        def _recursive(rootDir):
            for lists in os.listdir(rootDir):
                path = os.path.join(rootDir, lists)

                if os.path.isdir(path):
                    if pattern.search(os.path.basename(path)):
                        return True
                    elif _recursive(path):
                        return True
        return _recursive(rootDir)

    def hasDirectory_cur(self,rootDir,foldername):
        for lists in os.listdir(rootDir):
            path = os.path.join(rootDir, lists)
            if os.path.isdir(path) and foldername == os.path.basename(path):
                return True
        return False

    def hasFile(self,rootDir,rfilename):
        pattern = re.compile("^"+rfilename+"$")
        def _recursive(rootDir):
            for lists in os.listdir(rootDir):
                path = os.path.join(rootDir, lists)
                if os.path.isfile(path):
                    if pattern.search(os.path.basename(path)) and os.path.getsize(path) != 0L:
                        return True
                if os.path.isdir(path):
                    if _recursive(path):
                        return True
        return _recursive(rootDir)

    def getAbsoluteFilePath(self,rootDir,rfilename):
        pattern = re.compile("^" + rfilename + "$")

        def _recursive(rootDir):
            for lists in os.listdir(rootDir):
                path = os.path.join(rootDir, lists)
                if os.path.isfile(path):
                    if pattern.search(os.path.basename(path)) and os.path.getsize(path) != 0L:
                        absolute_path = os.path.abspath(path)
                        return absolute_path
                if os.path.isdir(path):
                    _recursive(path)
            return ''

        return _recursive(rootDir)

    def getAbsolutePath(self, rootDir, rname):
        pattern = re.compile("^" + rname + "$")

        def _recursive(rootDir):
            for lists in os.listdir(rootDir):
                path = os.path.join(rootDir, lists)
                if os.path.isfile(path):
                    if pattern.search(os.path.basename(path)) and os.path.getsize(path) != 0L:
                        absolute_path = os.path.abspath(path)
                        return absolute_path
                if os.path.isdir(path):
                    if pattern.search(os.path.basename(path)):
                        return os.path.abspath(path)
                    else:
                        _recursive(path)
            return ''

        return _recursive(rootDir)


    def contentNumOfDir(self,rdirname):
        if os.path.exists(rdirname):
            return len(os.listdir(rdirname))
        else:
            return 0

class AbsPath(object):

    def __init__(self,pattern):
        self.filepath = ""
        self.objectpath = ""
        self.pattern = pattern

    def hasFile(self,rootDir):
        for lists in os.listdir(rootDir):
            path = os.path.join(rootDir,lists)
            if os.path.isfile(path):
                self.filepath = path
                if self.pattern.search(os.path.basename(path)) and os.path.getsize(path) != 0L:
                    return True
            elif os.path.isdir(path):
                if self.hasFile(path):
                    return True
        return False
    def getAbsoluteFilePath(self):
        return self.filepath

    def hasObject(self,rootDir):
        for lists in os.listdir(rootDir):
            path = os.path.join(rootDir,lists)
            self.objectpath = path
            if os.path.isfile(path):
                if self.pattern.search(os.path.basename(path)) and os.path.getsize(path) != 0L:
                    return True
            if os.path.isdir(path):
                if self.pattern.search(os.path.basename(path)):
                    return True
                elif self.hasObject(path):
                    return True
        return False

    def getAbsolutePath(self):
        return self.objectpath


if __name__ == "__main__":
    util = Util()
    print util.filetype(r"C:\Users\creeper\Desktop\source\2530\1_Samsung_GT-N7100_1280x720_2015-09-29-17-05-04_tencentmobileassistant_6.0.0.8979_android_r95513_20150929094000_with_plugins.zip")




