def print_lol(the_list):
	""" Este é o módulo "nester.py", e fornece uma função chamada print_lol()
	que imprime listas que podem ou não incluir listas aninhadas"""
	for each_item in the_list:
		""" Esta função requer um argumento posicional chamado "the_list", que é
		qualquer lista Python (de possíveis listas aninhadas). Cada item de dados na
		lista fornecida é (recursivamente) impresso na tela em sua própria linha """
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)