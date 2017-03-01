# console is a module that provides common console operations

# PROMPTS
def getChoice(numbers, choices, prompt='\nEnter choice: ', error='Invalid choice.'):
	'''
	Prompt user for choice
	Return an integer of valid choice
	'''
	assert len(numbers) == len(choices), 'Length of list of numbers and list of choices must be the same.'
	assert all(type(number) == int for number in numbers), 'Numbers must be integer.'
	assert all(type(choice) == str for choice in choices), 'Choices must be string.'
	for i in range(len(numbers)):
		print('(%s) %s' % (numbers[i], choices[i]))
	while True:
		choice = input(prompt)
		try:
			choice = int(choice)
			if choice in numbers:
				return choice
			else:
				raise ValueError()
		except ValueError:
			print(error)

def getQuery(prompt='\nEnter query: ', error='Invalid query.'):
	''' 
	Prompt user for query
	Return a string of valid query 
	'''
	while True:
		query = input(prompt)
		if query != '':
			return query
		else:
			print(error)

def getYesOrNo(prompt='\nEnter response (Y/N) ', error='Invalid response.'):
	'''
	Prompt user for yes or no
	Return a string of either 'Y' or 'N'
	'''
	while True:
		response = getQuery(prompt, error)
		if response.upper() in 'Y N'.split():
			return response.upper()
		else:
			print(error)

def hitEnter(action='continue'):
	''' Prompt user to hit enter '''
	input('[Hit enter to %s]' % action)

# STRING ADJUSTMENT
def leftAlign(text, width):
	''' Return a string left-aligned within the given width '''
	words = text.split()
	# Check longest word against width
	longestWord = ''
	for word in words:
		if len(word) > len(longestWord):
			longestWord = word
	assert len(longestWord) <= width, 'Longest word cannot exceed width.'
	# Left-align text
	string = ''
	line = ''
	firstWord = True
	for word in words:
		lineLength = len(line)
		wordLength = len(word) + 1
		if firstWord:
			line += word
			firstWord = False
			continue
		if lineLength + wordLength > width:
			line += ('\n')
			string += line
			line = word
		else:
			line += (' ' + word)
	string += line
	return string

def centerAlign(text, width):
	''' Return a string centered-aligned within the given width '''
	leftAlignedText = leftAlign(text, width)
	lines = leftAlignedText.split('\n')
	centeredLines = list(map(lambda line: line.center(width), lines))
	return '\n'.join(centeredLines)

def leftPad(text, padding):
	''' Return a string left-padded with the given padding '''
	lines = text.split('\n')
	paddedLines = (map(lambda line: ' '*padding + line, lines))
	return '\n'.join(paddedLines)

# STRUCTURING
def printTitle(title, width, character='*', padding=1):
	''' Print a decorated title '''
	assert type(title) == str and title != '', 'Title must be non-empty string.'
	assert type(width) == int and width >= len(title), 'Width must be at integer that is at least length of title.'
	assert type(character) == str and len(character) == 1, 'Character must be string of length 1.'
	assert type(padding) == int and padding >= 1, 'Padding must be integer that is at least 1.'
	length = len(title)
	string = centerAlign(character*(length + padding*4), width)
	string += '\n'
	titleString = centerAlign('%s%s%s' % (' '*(padding*2 - 1), title, ' '*(padding*2 - 1)), width)
	firstIndex = 0
	for char in titleString:
		if char != ' ':
			firstIndex = titleString.index(char) - padding*2
			break
	lastIndex = firstIndex + length + padding*4
	titleString = titleString[:firstIndex] + character + titleString[firstIndex+1:lastIndex-1] + character + titleString[lastIndex:]
	string += titleString
	string += '\n'
	string += centerAlign(character*(length + padding*4), width)
	print(string)

def printHeader(header, character='=', padding=1, newLineBelow=True):
	''' Print a decorated header '''
	assert type(character) == str and len(character) == 1, 'Character must be string of length 1.'
	print(' '*padding + header)
	print(character*(len(header)+ padding*2))
	if newLineBelow:
		print()

def printDivider(length, character='-', newLineAbove=True):
	''' Print a horizontal divider '''
	assert type(character) == str and len(character) == 1, 'Character must be string of length 1.'
	divider = character*length
	if newLineAbove:
		divider = '\n' + divider
	print(divider)	