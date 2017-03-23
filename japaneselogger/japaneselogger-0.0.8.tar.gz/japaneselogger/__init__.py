# -*- coding: utf-8 -*-
'''
Created on 2017/03/17

@author: takasi

loggingについてのチュートリアル
https://docs.python.jp/3/howto/logging.html

必要パッケージ
・メール通知機能、インストールはubuntuの場合「sudo apt-get install postfix」
・デスクトップ通知機能、notify-sendコマンドが端末で使える事
'''
import logging
from logging.handlers import SMTPHandler,RotatingFileHandler
from logging import Handler
import smtplib
import subprocess


#最初に直接呼び出されて実行されたmainファイル名をログファイルの名前にする
import sys
from os.path import basename, splitext
try:
    LOGNAME = basename(splitext(sys.modules['__main__'].__file__)[0])
except AttributeError:
    LOGNAME = "japaneselogger"

#デバッグ以上のロガーの設定
logger = logging.getLogger(LOGNAME)
logger.setLevel(logging.DEBUG)

#ログの出力形式の設定
_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(lineno)s %(message)s',datefmt='%m/%d %H:%M:%S')

#デバッグ以上のハンドラの設定
#ストリームに出力
_ch = logging.StreamHandler()
_ch.setLevel(logging.DEBUG)
_ch.setFormatter(_formatter)
logger.addHandler(_ch)

#1ファイルにつき最大1Mバイトまで、最大5ファイルまで保管
_fhd = RotatingFileHandler("{}.debug.log".format(LOGNAME),
                        maxBytes=10**6,
                        backupCount=5)
_fhd.setLevel(logging.DEBUG)
_fhd.setFormatter(_formatter)
logger.addHandler(_fhd)

#エラー以上のハンドラの設定
#1ファイルにつき最大1Mバイトまで、最大5ファイルまで保管
_fhe = RotatingFileHandler("{}.error.log".format(LOGNAME),
                        maxBytes=10**6,
                        backupCount=5)
_fhe.setLevel(logging.ERROR)
_fhe.setFormatter(_formatter)
logger.addHandler(_fhe)

#関数を上書き
debug = logger.debug
info = logger.info
warn = logger.warn
error = logger.error
exception = logger.exception

#メール通知機能
def enableEMailNotification(
    #メール設定
    EMAIL_TO_ADDRESS = 'example@example.com',
    SMTP_HOST = 'localhost',
    SMTP_PORT = 25,
                            ):
    try:
        #SMTPサーバーが利用可能かの確認
        server = smtplib.SMTP()
        server.connect(SMTP_HOST, SMTP_PORT)
        server.close()
        
        sh = logging.handlers.SMTPHandler(mailhost=(SMTP_HOST, SMTP_PORT),
                                          fromaddr=LOGNAME,
                                          toaddrs=EMAIL_TO_ADDRESS,
                                          subject=LOGNAME)
        sh.setLevel(logging.ERROR)
        sh.setFormatter(_formatter)
        logger.addHandler(sh)
        logger.info("メール通知機能を使います、エラー以上は通知されます")
    except ConnectionRefusedError:
        logger.warning("SMTPサーバーが応答していないためメール通知機能が使えません")

#デスクトップ通知機能
def enableDesktopNotification(commandType="notifiy-send"):
    try:
        if(commandType=="notifiy-send"):
            output = subprocess.check_output(["notify-send","--version"])
            logger.info("デスクトップ通知機能のnotify-sendを使います、エラー以上は通知されます")
        elif(commandType=="zenity"):
            output = subprocess.check_output(["zenity","--help"])
            logger.info("デスクトップ通知機能のzenityを使います、エラー以上は通知されます")
        else:
            return
        class NotifyHandler(Handler):
            def emit(self,logRecord):
                if(commandType=="notifiy-send"):
                    command = ["notify-send", LOGNAME, logRecord.getMessage()]
                    subprocess.call(command)
                elif(commandType=="zenity"):
                    command = ["zenity", "--error", "--text={} : {}".format(LOGNAME,logRecord.getMessage())]
                    subprocess.call(command)
        nh = NotifyHandler()
        nh.setLevel(logging.ERROR)
        nh.setFormatter(_formatter)
        logger.addHandler(nh)
    except FileNotFoundError:
        logger.warning("デスクトップ通知機能が使えません")
