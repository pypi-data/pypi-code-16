#!/usr/bin/env python
# coding: utf-8
import pexpect
from configobj import ConfigObj
from socket import socket, SOCK_DGRAM, AF_INET

SMIT_PROPS = "../../install_files/linux-worker/smit-celery.ini"
LOGIN = 'admin'
PASSWORD = 'admin6tem'
EMAIL = 'admin@starxpert.fr'

child = pexpect.spawn('python manage.py migrate')
child.expect('Would you like to create one now.*')
child.sendline('yes')
child.expect('Username.*')
child.sendline(LOGIN)
child.expect('E-mail.*')
child.sendline(EMAIL)
child.expect('Password.*')
child.sendline(PASSWORD)
child.expect('Password.*')
child.sendline(PASSWORD)

child.expect(pexpect.EOF, timeout=None)
#modification du celeryconfig.py linux
s = socket(AF_INET, SOCK_DGRAM)
s.connect(('google.fr', 0))
s.getsockname()
IP_SERVER=s.getsockname()[0]
print "Adresse ip de ce serveur : %s"%IP_SERVER
print "Copie de l'adresse ip dans le fichier de config..."

globalConfig = ConfigObj()
globalConfig.filename = SMIT_PROPS

smit={
      'ip':'%s'%IP_SERVER,
      'webAdminLogin':'%s'%LOGIN,
      'webAdminPassword':'%s'%PASSWORD,
      'webAdminEmail':'%s'%EMAIL
      }

globalConfig['smit'] = smit
globalConfig.write()

print "fichier de config utilisé : %s "%SMIT_PROPS
