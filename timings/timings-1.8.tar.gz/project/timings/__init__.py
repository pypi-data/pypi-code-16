
''' Python Module to convert time units. '''

def to_mins( seconds ):
	
	''' Converts seconds to minutes. '''
	
	mins = seconds/60
	sec = seconds%60
	
	print mins, 'minutes and', sec, 'seconds.'
	

def to_hours( seconds ):

	''' Converts seconds to the form hh:mm:ss. '''
	
	if seconds/3600 == 0:
		mins = seconds/60
		sec = seconds%60
		print mins, 'minutes', sec, 'seconds.'
	
	else:
		hrs = seconds/3600
		leftOvers = seconds%3600
		mins = leftOvers/60
		sec = leftOvers%60
		
		print hrs, 'hours', mins, 'minutes', sec, 'seconds.'
		
# Code by Himanshu Sharma

