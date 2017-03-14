#coding:utf-8
import os
import thread
from datetime import date
from multiprocessing.dummy import Pool as ThreadPool
import struct,zipfile,re
import os

__author__ = 'creeper'

class DotableDict(dict):
    def __init__(self,*args,**kwargs):
        dict.__init__(self,*args,**kwargs)
        self.__dict__ = self


class unzipSource(object):
    def __init__(self,source_zip_file,source_path,dst_path,performance_path,mUtil,process_num = 1):
        self.mUtil = mUtil
        self.source_zip_file = source_zip_file
        self.source_path = source_path
        self.dst_path = dst_path
        self.performance_path = performance_path
        self.PROCESS_NUM = process_num
        self.createPath(dst_path)
        self.createPath(performance_path)
        self.pattern = re.compile(r"\d*.jpg")
        self.zipfile = {'num':0,'comment':"Total compressed file provided by the platform",'device':'-'}
        self.valid_zipfile = {'num':0,'comment':"Effective compressed files number,\nUnvalid compressed files don't have any content in it",'device':''}
        self.resultzip = {'num':0,'comment':"Number of effective compressed files where\n we can find Result.zip in it",'device':''}
        self.valid_resultzip = {'num':0,'comment':"Total effective result.zip in all Result.zip devices",'device':''}
        self.task_id = ''
        self.pool = ThreadPool(8)
        self.mylock = thread.allocate_lock()

    def unzip_process(self,mfile):
        if mfile.endswith(".zip"):
            file_name = self.getDeviceName(mfile)
            self.zipfile['num'] += 1
            self.mylock.acquire()
            self.zipitem.extract(mfile,self.source_path)
            self.mylock.release()
            if self.mUtil.isZipFile(os.path.join(self.source_path,mfile)):
                self.valid_zipfile['num'] += 1
                tmp_zipfile_object = zipfile.ZipFile(os.path.join(self.source_path,mfile))
                if len(tmp_zipfile_object.namelist()) == 0:
                    #创建目录
                    os.mkdir(os.path.join(self.dst_path,file_name))
                else:
                    tmp_zipfile_object.extractall(os.path.join(self.dst_path,file_name))

                if "Result.zip" in os.listdir(os.path.join(self.dst_path,file_name)):
                    self.resultzip['num'] += 1
                    if self.mUtil.isZipFile(os.path.join(self.dst_path,file_name,"Result.zip")):
                        self.valid_resultzip['num'] += 1
                        resultzipfile = zipfile.ZipFile(os.path.join(self.dst_path,file_name,"Result.zip"))
                        for item in resultzipfile.namelist():
                            if re.search(r"Kat_Performance.csv$",item):
                                try:
                                    resultzipfile.extract(item,os.path.join(self.performance_path))
                                    os.rename(os.path.join(self.performance_path,"Result","Kat_Performance.csv"),os.path.join(self.performance_path, "Result",file_name+"_Kat_Performance.csv"))
                                except:
                                    pass
                    else:
                        self.valid_resultzip['device'] += self.getDeviceName(mfile)+'\n'

                else:
                    self.resultzip['device'] += self.getDeviceName(mfile)+'\n'

            else:
                self.valid_zipfile['device'] += file_name +'\n'


    def unzip(self):
        self.task_id = os.path.basename(self.source_zip_file).split(".")[0]
        # 首先删除source_path 和 dst_path
        self.mUtil.delete_file_folder(self.source_path)
        self.mUtil.delete_file_folder(self.dst_path)
        self.mUtil.delete_file_folder(self.performance_path)

        self.zipitem = zipfile.ZipFile(self.source_zip_file)
        zipfiles = self.zipitem.namelist()
        try:
            self.pool.map(self.unzip_process, zipfiles)
            self.pool.close()
            self.pool.join()
        except:
            pass

    def createPath(self,path):
        if os.path.exists(path):
            self.mUtil.delete_file_folder(path)
        os.mkdir(path)

    def getDeviceName(self,filename):
        year = "_" + str(date.today().year)
        return filename.split(year)[0].split("/")[-1]

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

    def contentNumOfDir(self,rdirname):
        if os.path.exists(rdirname):
            return len(os.listdir(rdirname))
        else:
            return 0


if __name__ == "__main__":
    mUtil = Util()
    process = unzipSource(source_zip_file = r"C:\Users\SJKP\Desktop\3339.zip",\
            source_path = r"d:\source", dst_path = r"d:\dst_path", performance_path = r"d:\performance_path",mUtil= mUtil)
    import time
    start = time.time()
    process.unzip()
    end = time.time()
    print 'end-start:', end-start
