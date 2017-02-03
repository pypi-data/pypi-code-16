import sqlite3, openpyxl

# excel에 cell value를 파악해서 sqlite data type 으로 변환해주는 함수
# parameter
#			cell : class openpyxl.cell
def get_sqlite_data_type(cell):
	# cell.data_type : openpyxl.cell RTFM
	if cell.is_date == False:
		if (cell.data_type == 's' or cell.data_type == 'inlineStr'):
			datatype = 'TEXT'						# string
		elif cell.data_type == 'n':
			if cell.value == None:					# null
				datatype = 'NULL'
			elif isinstance(cell.value, int):		# integer
				datatype = 'INTEGER'
			elif isinstance(cell.value, float):		# float
				datatype = 'REAL'
		elif cell.data_type == 'b':					# boolean
			datatype = 'INTEGER'
	else:
		datatype = 'TEXT'							# datetime
	return datatype


# field information list
#	parameters:
#		worksheet : class openpyxl.worksheet
#		field_name_range: ('A1','M1') or ['A1','M1'] 
#		field_example_range: ('A123','M123') or ['A123','M123']
#							  - Null값이 하나도 없어야함
#		primary_key : 'Name' - field name list에 있는 값 중에 하나
def get_field_info_list(
		worksheet, field_name_range, field_example_range, primary_key=None
		):
	fieldNames = [[(str(cell.value).strip()).replace(' ','_') for cell in row] 
		for row in worksheet[field_name_range[0]:field_name_range[1]]]
	fieldTypes = [[get_sqlite_data_type(cell) for cell in row] 
		for row in worksheet[field_example_range[0]:field_example_range[1]]]
	resultList= list(zip(fieldNames[0],fieldTypes[0]))

	if (primary_key != None and primary_key in fieldNames[0]):
		for i in range(len(resultList)):
			if resultList[i][0] == primary_key:
				tmpItem = (resultList[i][0], resultList[i][1], 'PRIMARY KEY')
				resultList[i] = tmpItem
	return (resultList, fieldNames[0], fieldTypes[0])

# create table sql을 만들기
# 	parameters:
#		table_name: 'table_name'
#		field_info_list: [('userID','TEXT','PRIMARY KEY'),('password','TEXT')]
#					- get_field_info_list()로 구함
def get_create_table_sql(table_name, field_info_list):
	fString = ','.join([' '.join(list(field)) for field in field_info_list])
	return "CREATE TABLE {0} ({1});".format(table_name, fString)

# hjxl_dictionary와 keyword list로 부터 sql insert 문에 필요한 리스트를 구함
#	parameters:
#		kwList: keyword list 곧 db의 field name list
#		hjxl_dictionary: hjexcel.get_dictionary로 얻은 데이터 ()
def get_insert_list_from_dictionary(kwList, hjxl_dictionary):
	resultList = []
	for dictKey, dictItem in sorted(
			hjxl_dictionary.items(), key=lambda x:x[0]
			):
		record=[]
		for kword in kwList:
			record.append(dictItem[kword])
		resultList.append(record)
	return resultList

# insert sql template를 구하는 함수
def get_insert_sql_template(table_name, keyword_number):
	return "INSERT INTO {0} VALUES ({1});".format(
		table_name,','.join('?'*keyword_number)
		)

