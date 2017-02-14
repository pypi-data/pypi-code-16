#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql

class DatabaseConnector:
    """Adds MYSQL connectivity and includes query functions."""

    def __init__(self):
        self.static_unit_id_lookup = {}
        self.init_units()
        self.database_host = 'localhost'
        self.database_user='robot',
        self.database_name =  'database_units_checking_analysis'
        self.database_password ='RobotRobot1!'
    
    def init_units(self):
        self.static_unit_id_lookup = {
            'amp': 12,
            'degree_360': 9,
            'degree_celsius':10,
            'kilogram': 4,
            'lux':8,
            'meter': 1,
            'pascal': 6,
            'quaternion':5,
            'radian':3,
            'second':2,
            'tesla':7 ,
            'volt':11
            }

    def execute_this_database_query(self, query_as_string):
        ''' TAKES SQL QUERY AS INPUT AND RUNS IT
            input: query_as_string    SQL query as string
            output: none
            '''
        if self.debug:
            print query_as_string
        conn = pymysql.connect(host=self.database_host,
                             user=self.database_user,
                             password=self.database_password,
                             db=self.database_name)
        c = conn.cursor()
	c.execute(query_as_string)
        lastrowid = c.lastrowid
        self.db_most_recent_insert_id = lastrowid
	conn.commit()
        # SAVE LAST INSERT ID - USEFUL FOR INSERTS IN 1-TO-MANY-TABLES
	conn.close()
        return lastrowid


    def add_class_and_units_to_all_list(self, class_name, units):
        ''' WHEN TRACKING ALL UNIT TYPES, ADD THEM TO DATA STRUCTURE HERE
            input:  class_name str the name of the ROS class or str (ex: 'atan2') that merits units
                    units : the dictionary or units
            output: None, side effect updates local data structures.
            '''
        if not class_name in self.all_classes_and_units_for_this_file_as_dict:
            self.all_classes_and_units_for_this_file_as_dict[class_name] = units
        else:
            pass  # WE DON'T CASE BECAUSE WE'RE ONLY TRACKING UNIQUE UNITS, NOT COUNTS

    def insert_file_unit_class_records(self):
        ''' INSERTS UNIT RECORDS FOR ALL FILES INTO DATABASE
            input: None - Requires self.all_classes_and_units_for_this_file_as_dict
            output: None - side effect: updates database
            '''
        if not self.all_classes_and_units_for_this_file_as_dict:
            return
        query_string = ''' INSERT INTO file_and_units
                    (date_time, file_uri)
                    VALUES
                    (NOW(),'''
        query_string += "'" + str(self.current_file_under_analysis) + "'"
        query_string += ')'
        self.execute_this_database_query(query_string)
        self.file_and_unit_id = self.db_most_recent_insert_id
        for class_name, units in self.all_classes_and_units_for_this_file_as_dict.iteritems():
            query_string = ''' INSERT INTO units_and_classes
                            (
                            file_and_units_id
                            , ros_header_class
                            , units
                            ) VALUES (
                            ''' + str(self.file_and_unit_id)
            query_string += ", '" + class_name + "'"
            query_string += ', "' + str(units) + '"'
            query_string += ')'
            self.execute_this_database_query(query_string)


    def create_database_entry_for_one_time_analysis(self):
        '''UPDATES LOCAL DATABASE FOR ONE ANALYSIS - USUALLY TESTING
            '''
        query_string = ''' INSERT INTO analysis_audit
            (datetime, version, input_file)
            VALUES
            (NOW(),'''
        query_string += "'" + str(self.VERSION) + "',"
        query_string += "'" + str(self.current_file_under_analysis) + "'"
        query_string += ')'
        self.execute_this_database_query(query_string)
        self.db_analysis_audit_row_id = self.db_most_recent_insert_id

    def update_database(self, list_of_unit_error_objects=None):
        ''' UPDATES THE LOCAL DATABASE WITH A SUMMARY OF THE RESULTS OF THE ANALYSIS OF THIS FILE
            requires: the self.db_analysis_audit_row_id is correct
            input:  data_record  list of numbers of each kind of error ordered by unit_error_type [1, 2, 3, 4, 5, 6, 7] 
                    list_of_unit_error_objects   UnitError Objects 
            returns: None
            side-effect(s): new records in the local database
            '''
        query_string = '''INSERT INTO file_analysis
		(
		analysis_audit_id,
		datetime,
		repository,
		file_name,
		some_ROS_units_found
		)
		VALUES
		(''' + str(self.db_analysis_audit_row_id) + ''',
		NOW(),''' 
        query_string += "'" + self.current_repository + "'," 
        query_string += "'" + self.current_file_under_analysis + "'," 
        query_string += str(int(self.found_ros_units_in_this_file)) + ')'
        # query_string += ','.join([str(x) for x in data_record]) + ')'
        # query_string += '''%d,%d,%d,%d,%d,%d,%d)''' % data_record
		# + '''?,?,?,?,?,?,?)''' % data_record
        file_analysis_id = self.execute_this_database_query(query_string)
        # NOW INSERT ERROR DETAILS FOR EACH ERROR
        if list_of_unit_error_objects:
            for e in list_of_unit_error_objects:
                query_string_error_details = '''INSERT INTO error_details
                (
                file_analysis_id,
                linenr,
                token,
                var_name,
                unit_error_types_id,
                file_uri,
                is_unit_propagation_based_on_constants,
                is_unit_propagation_based_on_unknown_variable,
                is_warning
                ) 
                VALUES 
                (''' + str(file_analysis_id)
                query_string_error_details += ',' + str(e.linenr) + ','
                if e.token:
                    query_string_error_details += "'" + e.token.str + "',"
                else:
                    query_string_error_details += "'',"
                query_string_error_details += "'" + e.var_name + "',"
                query_string_error_details += "'" + str(e.ERROR_TYPE) + "',"
                query_string_error_details += "'" + str(e.get_file_URI_where_error_occured()) + "',"
                query_string_error_details += "'" + str(int(e.is_unit_propagation_based_on_constants)) + "',"
                query_string_error_details += "'" + str(int(e.is_unit_propagation_based_on_unknown_variable)) + "',"
                query_string_error_details += "'" + str(int(e.is_warning)) + "')"
                print query_string_error_details
                error_details_id = self.execute_this_database_query(query_string_error_details)

                if e.ERROR_TYPE in [UnitErrorTypes().VARIABLE_MULTIPLE_UNITS, UnitErrorTypes().UNIT_SMELL]:
                    # UPDATE DATABASE WITH UNITS OF FIRST ASSIGNMENT AND UNITS AT PROBLEM LOCATION
                    variable_insert_query = '''INSERT INTO variable  
                        (
                        file_analysis_id,
                        error_details_id,
                        var_name
                        ) VALUES (
                        ''' + str(file_analysis_id) + ','
                    variable_insert_query += str(error_details_id) + ','
                    variable_insert_query += "'" + e.var_name + "'" + ')'
                    variable_id = self.execute_this_database_query(variable_insert_query)
                    for unit_assignment_linenr, dict_of_units_and_tokens in e.all_units_assigned_to_var_as_dict.iteritems():
                        for unit_dict in dict_of_units_and_tokens['units']:  # THIS IS A LIST

                            # INSERT RECORD FOR UNIT ASSIGNMENT
                            variable_unit_assignment_insert_query = '''INSERT INTO variable_unit_assignment
                                (
                                variable_id,
                                linenr
                                ) VALUES (''' + str(variable_id) + ','
                            variable_unit_assignment_insert_query += str(unit_assignment_linenr) + ')'
                            variable_unit_assignment_id = self.execute_this_database_query(variable_unit_assignment_insert_query)
                            # print 'UUUU:%s ' % str(unit_dict)
                            for unit, power in unit_dict.iteritems():
                                unit_assignment_insert_query = ''' INSERT INTO unit_assignment
                                    (
                                    variable_unit_assignment_id,
                                    unit_types_id,
                                    power
                                    ) VALUES ('''
                                unit_assignment_insert_query += str(variable_unit_assignment_id) + ','
                                unit_assignment_insert_query += str(self.database_helper.static_unit_id_lookup[unit]) + ','
                                unit_assignment_insert_query += str(power)
                                unit_assignment_insert_query += ')'
                                print unit_assignment_insert_query
                                self.execute_this_database_query(unit_assignment_insert_query)


