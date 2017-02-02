import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.audio import MIMEAudio
from email import encoders
from email.mime.text import MIMEText
import mimetypes
import os

class sendMailError(Exception):
    pass

def sendMail(fromAddress, toAddress, mSubject, mBody, mBodyHTML, mAttachment = [], serverLogin = True, serverServer = None, serverPort = None, serverTSL = True, serverUser = None, serverPass = None):
  msg = MIMEMultipart('alternative')

  msg['From'] = fromAddress
  msg['To'] = toAddress
  msg['Subject'] = mSubject

  body = mBody
  bodyHTML = mBodyHTML
  partText = MIMEText(body, 'plain')
  partHTML = MIMEText(bodyHTML, 'html')
  msg.attach(partText)
  msg.attach(partHTML)

  if mAttachment:
    for i in mAttachment:
      fp = open(i, 'rb')
      ctype, encoding = mimetypes.guess_type(i)
      if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
      maintype, subtype = ctype.split('/', 1)
      if maintype == 'text':
        attachment = MIMEText(fp.read(), _subtype=subtype)
      elif maintype == 'image':
        attachment = MIMEImage(fp.read(), _subtype=subtype)
      elif maintype == 'audio':
        attachment = MIMEAudio(fp.read(), _subtype=subtype)
      else:
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        encoders.encode_base64(msg)
      fp.close()
      msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(i))
      msg.attach(i)
  
  s = smtplib.SMTP(serverServer,serverPort)

  if serverLogin:
    if serverTSL:
      s.starttls()
    s.login(serverUser, serverPass)
  
  text = msg.as_string()
  send = s.sendmail(fromAddress, toAddress, text)
  s.quit()

  if send == {}:
    print ("Sending successful")
  else:
    raise sendMailError(send)