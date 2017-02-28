import re
import requests
from sys import exit
from moviehub.console import *
from bs4 import BeautifulSoup
from collections import OrderedDict

def main():

	PROGRAM_NAME = 'OPEN MOVIE DATABASE'
	PROGRAM_WIDTH = 80 # Width of program
	API_URL = 'http://www.omdbapi.com/' # Open Movie Database API
	FULL_PLOT = False # Display full plot in basic information
	ROTTEN_TOMATOES = True # Display rotten tomatoes information
	EXTRA_INFO = True # Display extra information
	
	printDivider(PROGRAM_WIDTH)
	print()
	printTitle(PROGRAM_NAME, PROGRAM_WIDTH)
	print()
	print(centerAlign('~ Powered by OMDb API ~', PROGRAM_WIDTH))
	print(centerAlign(API_URL[7:-1], PROGRAM_WIDTH))

	while True:
		print()
		printHeader('Home Menu')
		options = ['Quick Hit', 'Search', 'About', 'Exit']
		choice = getChoice([0, 1, 2, 3], options)
		printDivider(PROGRAM_WIDTH)

		# Prepare request
		payload = {
			'type': 'movie',
			'tomatoes': 'true' if ROTTEN_TOMATOES else 'false', 
			'plot': 'full' if FULL_PLOT else 'short'
		}
		if choice == 0 or choice == 1:
			print()
			printHeader(options[choice], newLineBelow=False)
			query = getQuery()
			correctedQuery = autocorrect(query)
			# Suggest corrected query
			if query != correctedQuery:
				response = getYesOrNo('\nDid you mean %s? (Y/N) ' % correctedQuery.upper())
				if response == 'N':
					correctedQuery = query
			if choice == 0:
				searching = False
			else:
				searching = True
		elif choice == 2:
			# Display about information
			print()
			printHeader('About')
			print('Author: Marcus Mu')
			print('Email: chunkhang@gmail.com')
			print('Last Updated: 2017-02-25')
			printDivider(PROGRAM_WIDTH)
			continue
		else:
			exit(0)

		# Send request
		print('\nSending query to database...')
		res = sendRequest(correctedQuery, API_URL, payload, search=searching)
		printDivider(PROGRAM_WIDTH)

		# Parse response			
		if res['Response'] == 'True':	
			# Quick hit
			if not searching:
				# Display information
				displayInformation(res, PROGRAM_WIDTH, rottenTomatoes=ROTTEN_TOMATOES, extraInfo=EXTRA_INFO)
			# Search
			else:
				print()
				printHeader('Results for %s' % correctedQuery.upper())
				results = []
				ids = []
				for result in res['Search']:
					results.append('%s (%s)' % (result['Title'], result['Year']))
					ids.append(result['imdbID'])
				choice = getChoice(list(range(len(results))), results)
				# Send request
				print('\nRetrieving information from database...')
				res = sendRequest(str(ids[choice]), API_URL, payload, id=True)
				printDivider(PROGRAM_WIDTH)
				# Display information
				displayInformation(res, PROGRAM_WIDTH, rottenTomatoes=ROTTEN_TOMATOES, extraInfo=EXTRA_INFO)
		else:
			print()
			printHeader('Error')
			print(res['Error'])
			print()
		printDivider(PROGRAM_WIDTH, newLineAbove=False)

def sendRequest(query, api, payload, id=False, search=False):
	''' 
	Send HTTP request to OMDb API
	Return HTTP response parsed into JSON
	'''
	payload = payload.copy()
	assert type(query) == str, 'Query must be string.'
	if not search:
		if not id:
			payload['t'] = query
		else:
			payload['i'] = query
	else:
		assert id == False, 'Search by title only.'
		payload['s'] = query
	while True:
		try:
			r = requests.get(api, params=payload)
			if r.status_code == 200:
				return r.json()
			else:
				print('Something went wrong: Error %s.' % r.status_code)
				exit(1)
		except requests.exceptions.ConnectionError:
			print('Cannot establish connection to database.\n')
			hitEnter('retry')

def displayInformation(response, width, rottenTomatoes=True, extraInfo=True):
	''' Display movie information '''
	title = response['Title']
	year = response['Year']
	information = [
		# Basic information
		OrderedDict([
			('plot', response['Plot']),
			('director', response['Director']),
			('writer', response['Writer']),
			('actors', response['Actors'])
		])
	]
	if rottenTomatoes:
		information.append(
			# Rotten Tomatoes information
			OrderedDict([
				('consensus', response['tomatoConsensus']),
				('tomatometer', response['tomatoMeter'] + '%'),
				('average rating', response['tomatoRating'] + '/10'),
				('url', response['tomatoURL'])
			])
		)
	if extraInfo:
		information.append(
			# Extra information	
			OrderedDict([
				('genre', response['Genre']),	
				('rated', response['Rated']),
				('runtime', response['Runtime']),
				('release date', response['Released'])
			])
		)
	# Display information
	print()
	printHeader('%s (%s)' % (title, year))
	for info in information:
		for key in info.keys():
			print(key.upper() + '\n')
			detail = info[key]
			if 'N/A' in detail:
				detail = '-'
			print(leftPad(leftAlign(detail, width-3), 3))
			print()
		hitEnter()
		print()

def autocorrect(phrase):
	''' Return a string of suggested spelling for the phrase provided '''
	googleSearchURL = 'http://www.google.com/search'
	payload = {'q': phrase.strip()}
	try:
		r = requests.get(googleSearchURL, params=payload)
		if r.status_code != 200:
			return phrase
	except requests.exceptions.ConnectionError:
		return phrase
	soup = BeautifulSoup(r.text, 'html.parser')
	element = soup.find('a', attrs={'class': 'spell'})
	if element is not None:
		correctedPhrase = re.sub('<.*?>', '', str(element))
		return correctedPhrase
	else:
		return phrase

if __name__ == '__main__':
	main()