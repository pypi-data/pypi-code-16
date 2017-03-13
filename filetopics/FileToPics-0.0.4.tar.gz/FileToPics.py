import sys
import os
import json    
import subprocess


class FileToPics:
    def __init__(self, **kwargs) :
        self.filePath = kwargs.get('filePath', '')
        self.picPath  = kwargs.get('picPath', '')
        self.fileName = os.path.basename(self.filePath)
        self.fileExt  = kwargs.get('fileExt', '')
        self.picExt  = kwargs.get('picExt', 'webp')
        self.info     = dict()

    def checkParams(self):
        if not (self.filePath and self.picPath and self.picExt and self.fileExt):
            res = {'Code': 400, 'Message': 'the necessary params is not given'}
        else:
            res = {'Code': 0, 'Message': 'check params success'}
        return res

    def checkPath(self, filePath):
        check = os.path.exists(filePath)
        if not check:
            res = {'Code': 400, 'Message': 'the file: '+filePath+' is not found'}
        else:
            res = {'Code': 0, 'Message': 'success'}

        return res


    def fileToPicture(self):
        checkParams = self.checkParams()
        checkPath   = self.checkPath(self.filePath)

        if checkParams['Code'] != 0:
            return checkParams

        if checkPath['Code'] != 0:
            return checkPath

        if self.fileExt == 'pptx' or self.fileExt == 'ppt' or self.fileExt == 'doc':
            pdfRes = self.fileToPdf(self.filePath, self.picPath)
            if pdfRes['PdfCode'] == 0:
                picRes = self.pdfToPictures(pdfRes['PdfPath'], self.picPath, self.picExt)
            else:
                return json.dumps(pdfRes)   
        else:
            picRes = self.pdfToPictures(self.filePath, self.picPath, self.picExt)


        if picRes != 0:
            res = {'Code': 500, 'Message': 'the file to pics failed'}
        else:
            res = {'Code': 0, 'Message': 'the file to pics success'}
            return json.dumps(res)

    def fileToPdf(self, filePath, pdfPath):
        fullFilename = self.fileName
        fileName     = fullFilename.split('.')[0]
        cmd          = 'libreoffice --invisible --headless --convert-to pdf:writer_pdf_Export '+filePath+' --outdir '+ pdfPath
        proc         = subprocess.run(cmd, stdin = subprocess.PIPE, input = None, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True, timeout = None)
        
        outStr   = proc.stdout
        #errStr   = proc.stderr
        pdfCode  = proc.returncode
        return dict(PdfCode = pdfCode, PdfPath = pdfPath + fileName + '.pdf')
    
    def pdfToPictures(self, pdfPath, picPath, ext='png'):
        check = os.path.exists(pdfPath)
        if not check:
            return {'Code': 500, 'Message': 'pdf file is not found, '+pdf_path}
        fullFilename = self.fileName
        fileName    = fullFilename.split('.')[0]

        imgDir = picPath + fileName + '/'
        check = self.checkPath(imgDir)
        if check['Code'] != 0:
            os.makedirs(imgDir, 0o777)

        imgCmd = 'convert ' + pdfPath + ' ' + imgDir + fileName + '-%d.' + ext
        imgCode = os.system(imgCmd)
        return imgCode


if __name__ == '__main__':

    #file2pics = FileToPics(picpath = '/home/caomingzhu/ppttopic/jiaoben/', filetype = 'pdf')
    file2pics = FileToPics(filePath = '/data/web/2007-2010.pptx', picPath = '/data/web/', fileExt = 'ppt', picExt = 'png')
    res = file2pics.fileToPicture()
    print(json.dumps(res))
   
