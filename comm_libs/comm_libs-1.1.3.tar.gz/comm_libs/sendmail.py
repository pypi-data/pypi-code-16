#! /usr/bin/env python
#coding=utf8

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
#from email.mime.application import MIMEApplication
from email import Encoders

class MailSender:
    '''
    邮件发送客户端
    '''
    def __init__(self, mail_server, user, password, port=25):
        '''
        初始化
        '''
        self.mail_server = mail_server
        self.port = port
        self.user = user
        self.password = password
        self.mail = MIMEMultipart()
        self.sender = None
        self.receiver = None
    
    def add_content(self, content, encoding = "gbk"):
        '''
        增加邮件正文
        '''
        self.mail.attach(MIMEText(content, "html", encoding))
        #MIMEApplication
        #self.mail.attach(MIMEApplication(content, "excel", encoding))
        
    def add_attachment(self, filepath):
        '''
        增加附件
        '''
        import os
        fd = open(filepath, "rb")
        file_content = fd.read()
        fd.close()
        
        fn = os.path.basename(filepath)
        attachment = MIMEBase("application","octet-stream")
        attachment.set_payload(file_content)
        Encoders.encode_base64(attachment)
        attachment.add_header("Content-disposition", "attachment", filename=fn)
        
        self.mail.attach(attachment)
        
    def set_sender(self, sender):
        '''
        设置发件人
        '''
        self.sender = sender
        self.mail["From"] = sender
    
    def set_receiver(self, reveicer_list):
        '''
        设置收件人
        '''
        self.receiver = reveicer_list
        self.mail["To"] = ",".join(reveicer_list)
        
        
    def set_subject(self, subject):
        '''
        设置邮件主题
        '''
        self.mail["Subject"] = subject
    
    def sendmail(self):
        '''
        发送邮件
        '''
        smtp = smtplib.SMTP()
        
        #smtp.set_debuglevel(1)
        
        smtp.connect(self.mail_server, self.port)
        
        #smtp.ehlo_or_helo_if_needed()
        
        smtp.login(self.user, self.password)
        
        smtp.sendmail(self.sender, self.receiver, self.mail.as_string())
        
        smtp.quit()
        
        
    
if __name__ == '__main__':
    
    pass
    
        
