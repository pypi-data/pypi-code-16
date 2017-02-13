# -*- encode: UTF-8 -*-

def print_lol(the_list, indent=False, level=0):
	""" Este é o módulo "nester.py", e fornece uma função chamada print_lol()
	que imprime listas que podem ou não incluir listas aninhadas"""
	for each_item in the_list:
		""" Esta função requer um argumento posicional chamado "the_list", que é
		qualquer lista Python (de possíveis listas aninhadas). Cada item de dados na
		lista fornecida é (recursivamente) impresso na tela em sua própria linha 
		Um segundo argumento 'level' é usado para inserir tabulacoes quando uma
		lista aninhada é encontrada	"""
		if isinstance(each_item, list):
			print_lol(each_item, indent, level+1)
		else:
			if indent:
				#print("\t"*level, end='')
				for num in range(level):
					print("\t", end='')
			print(each_item)