from random import choice
from os.path import abspath, dirname

def read_file(file_name):
	with open(file_name) as f:
		return f.read()

def randfirst(gender='either'):
	file = dirname(__file__)
	male_first = read_file(abspath(file + '/../data/male_first_names.csv')).split(',')
	female_first = read_file(abspath(file + '/../data/female_first_names.csv')).split(',')
	if gender == 'male':
		return choice(male_first)
	elif gender == 'female':
		return choice(female_first)
	else:
		return choice(male_first + female_first)

def randlast():
	file = dirname(__file__)
	surnames = read_file(abspath(file + '/../data/surnames.csv')).split(',')
	return choice(surnames)

if __name__ == '__main__':
	print(randfirst())
	print(randfirst('male'))
	print(randfirst('female'))
	print(randlast())
