movies=['start',1975,'terry',91,['haha',['mike','john','idle']]]
def view(func):
	for i in func:
		if isinstance(i,list):
			 view(i)
		else: print i
