import localmail
import os
import sys
import threading

import unittest

from simpletransfers import mail, TransferException

thread = None

def setUpModule():
	global thread
	thread = threading.Thread(
		target = localmail.run,
		args = ( 2142, 2143, ),
	)
	thread.start()

def tearDownModule():
	localmail.shutdown_thread( thread )


testfiles = { 'one.txt': 'wibble\n' }

class testMail( unittest.TestCase ):

	def test_getput( self ):
		smtp = mail(
			'a', 'b', # auth ignored for test
			'localhost',
			2142,
			'noreply@casual-tempest.net',
			'acustomer@casual-tempest.net',
		)
		imap = mail(
			'a', 'b',
			'localhost',
			2143,
			'acustomer@casual-tempest.net',
			processed = 'processed',
		)

		smtp.put( 'wibble', 'test.txt' )

		msgs = imap.get( r'.*\.txt' )
		self.assertEqual( len(msgs), 1 )
		self.assertEqual( msgs.keys(), [ 'test.txt', ] )
		self.assertEqual( msgs.values(), [ 'wibble', ] )

	def test_put_no_destination( self ):
		smtp = mail(
			'a', 'b', # auth ignored for test
			'localhost',
			2142,
			'noreply@casual-tempest.net',
		)
		with self.assertRaises( TransferException ):
			smtp.put( 'wibble', 'test.txt' )

	def test_put_incorrect_connection( self ):
		smtp = mail(
			'a', 'b', # auth ignored for test
			'localhost',
			666,
			'noreply@casual-tempest.net',
			'noreply@casual-tempest.net',
		)
		with self.assertRaises( TransferException ):
			smtp.put( 'wibble', 'test.txt' )

	def test_get_incorrect_connection( self ):
		imap = mail(
			'a', 'b', # auth ignored for test
			'localhost',
			666,
			'noreply@casual-tempest.net',
		)
		with self.assertRaises( TransferException ):
			imap.get()

if __name__ == '__main__':
	unittest.main()
