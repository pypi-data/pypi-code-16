#!/usr/bin/env python3


import os
import argparse


path = os.path.dirname(__file__)


def dump(user, password):
  os.system(' '.join([
    'mysqldump',
    '--no-data',
    '--databases',
    '--user={}'.format(user),
    '--password={}'.format(password) if password is not None else '',
    'test_fangorn',
    '> {}/mysql_schema.sql'.format(path)
  ]))
  os.system(' '.join([
    'mysqldump',
    '--no-autocommit',
    '--no-create-info',
    '--skip-opt',
    '--skip-extended-insert',
    '--user={}'.format(user),
    '--password={}'.format(password) if password is not None else '',
    '| sed "s/set autocommit=0;/begin;/g"',
    '> {}/data.sql'.format(path)
  ]))

  os.system('sqlite3 {0}/sqlite.db .schema > {0}/sqlite_schema.sql'.format(path))

def restore(user, password):
  os.system(' '.join([
    'mysql',
    '--user={}'.format(user),
    '--password={}'.format(password) if password is not None else '',
    '< {}/mysql_schema.sql'.format(path)
  ]))
  os.system(' '.join([
    'mysql',
    '--user={}'.format(user),
    '--password={}'.format(password) if password is not None else '',
    'test_fangorn',
    '< {}/data.sql'.format(path)
  ]))

  os.system('rm -f {}/sqlite.db'.format(path))
  os.system('sqlite3 {0}/sqlite.db < {0}/sqlite_schema.sql'.format(path))
  os.system('sqlite3 {0}/sqlite.db < {0}/data.sql'.format(path))


def main():
  parser = argparse.ArgumentParser(description = 'Fangorn fixture manager')
  parser.add_argument('action', choices = ['dump', 'restore'],
    help = 'dump data to SQL files or restore MySQL and SQLite databases from dump')
  parser.add_argument('--user', help = 'MySQL user', default = 'root')
  parser.add_argument('--password', help = 'MySQL password')

  args = parser.parse_args()
  globals()[args.action](args.user, args.password)


if __name__ == '__main__':
  main()

