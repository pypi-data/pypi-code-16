import base64
import random

from django.conf import settings

def _pad(plaintext, block_size=16):
	padding = block_size - (len(plaintext) % block_size)
	return plaintext + '\0' + ''.join([chr(random.randint(ord('!'), ord('~'))) for x in range(padding - 1)])

def encrypt(plaintext, key=None, cipher='aes-256-cbc'):
	if not key:
		key = settings.SECRET_KEY
	try:
		from Crypto.Cipher import AES
		cipher = AES.new(key[:32])
		return 'AES$' + base64.b64encode(cipher.encrypt(_pad(plaintext)))
	except:
		import commands
		return commands.getoutput('printf "%s" | openssl %s -e -base64 -A -salt -k "%s"' % (plaintext, cipher, key))

def decrypt(ciphertext, key=None, cipher='aes-256-cbc'):
	if not key:
		key = settings.SECRET_KEY
	try:
		from Crypto.Cipher import AES
		cipher = AES.new(key[:32])
		return cipher.decrypt(base64.b64decode(ciphertext[4:])).split('\0')[0]
	except:
		import commands
		return commands.getoutput('printf "%s" | openssl %s -d -base64 -A -k "%s"' % (ciphertext, cipher, key))
