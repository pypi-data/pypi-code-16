from django.conf import settings
from django.db import connection

"""
http://dev.mysql.com/doc/refman/5.0/en/lock-tables-and-transactions.html
In mysql locks cannot be used with transactions, do not use this 

Use this as a last resort.  Use select_for_update or just update if possible first.
This does not play well with the transaction Django sets up with it's middleware and with testing.
NOTE: This function needs something to effectively end the current transaction and then start a new one to deal with the Transaction middleware. See transaction middleware for ideas.
"""

# Generate a lock decorator using a list of models to read lock and a list to write lock
def lock_models(read_lock_models, write_lock_models):
	"""Lock tables based on a list of models to read or write lock.

	Read locks mean that no one including the current session can write to the table.
	Write locks mean that no one except the current session can write to the table, but anyone can read.
	Pass the arguments a lists or None e.g. lock_models((mymodel1,mymodel2), (mymodel3,)) or lock_models(None, (mymodel3,))
	"""
	def lock_decorator(func):
		def lock_fun(*args, **kwargs):
		
			if settings.DATABASES['default']['ENGINE'].find('mysql') != -1:
				if read_lock_models:
					read_lock_str = ", ".join(map(lambda model:"%s READ" % (model._meta.db_table,), read_lock_models))
				else:
					read_lock_str = None
				if write_lock_models:
					write_lock_str = ", ".join(map(lambda model:"%s WRITE" % (model._meta.db_table,), write_lock_models))
				else:
					write_lock_str = None
					
				if read_lock_str and write_lock_str:
					lock_str = ", ".join((read_lock_str, write_lock_str))
				elif read_lock_str:
					lock_str = read_lock_str
				elif write_lock_str:
					lock_str = write_lock_str
				else:
					return func(*args, **kwargs)
				
				cursor = connection.cursor()
				# Lock
				cursor.execute("SET autocommit=0;")
				cursor.execute("LOCK TABLES %s;" % (lock_str,))
				# Work
				try:
					result = func(*args, **kwargs)
				except Exception as e:
					cursor.execute("ROLLBACK;UNLOCK TABLES;")
					raise e
				# Unlock
				cursor.execute("COMMIT;UNLOCK TABLES;")
				return result
				
			elif settings.DATABASES['default']['ENGINE'].find('postgres') != -1:
				if not read_lock_models and not write_lock_models:
					return func(*args, **kwargs)
				cursor = connection.cursor()
				# Lock
				cursor.execute("BEGIN;")
				if read_lock_models:
					cursor.execute("LOCK TABLE %s IN ACCESS SHARE;" % (",".join(map(lambda model:model._meta.db_table, read_lock_models)),))
				if write_lock_models:
					cursor.execute("LOCK TABLE %s IN EXCLUSIVE;" % (",".join(map(lambda model:model._meta.db_table, write_lock_models)),))
				# Work
				try:
					result = func(*args, **kwargs)
				except Exception as e:
					cursor.execute("ROLLBACK;")
					raise e
				# Unlock
				cursor.execute("COMMIT;")
				
			else:
				return func(*args, **kwargs)
			
		return lock_fun
	return lock_decorator
