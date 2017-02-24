import os.path
import numpy as np
import pandas as pd
import json
import sqlite3
import pkg_resources

def generate_feature_df(genes_of_interest,db_id):
    
    config_filename = pkg_resources.resource_filename('atenrich','data/config/db_config.json')
    with open(config_filename, 'r') as f:
        db_config = json.load(f)
    feature_id_column = db_config[db_id]['feature_id_column']
    target_id_column = db_config[db_id]['target_id_column']
    table_name = db_config[db_id]['table_name']
    db_filename = pkg_resources.resource_filename('atenrich','data/db/GeneListDB.db')
#    db = sqlite3.connect(db_config[db_id]['database_file'])
    db = sqlite3.connect(db_filename)
    db_cursor = db.cursor()

    #protect against SQL injection
    table_name = scrub(table_name)
    feature_id_column = scrub(feature_id_column)
    target_id_column = scrub(target_id_column)
    
    #create default feature list
    sql_query = "SELECT {0} FROM {1} GROUP BY {0};".format(feature_id_column,table_name)
    db_cursor.execute(sql_query)
    feature_list = [x[0] for x in db_cursor.fetchall()]

    #generate the accompanying feature matrix for all genes in the gene list
    sql_query = """SELECT {0} FROM {1} WHERE {2}=?;""".format(target_id_column,table_name,feature_id_column)

    feature_df = pd.DataFrame(index=genes_of_interest,columns=feature_list)
    
    for feature_name in feature_list:
        returned_gene_list = query_database(sql_query,feature_name,db_cursor)
        #features for this list
        binary_feature_vector = [int(x in returned_gene_list) for x in genes_of_interest]
        feature_df[feature_name] = binary_feature_vector
    
    db.close()
    return feature_df

def generate_feature_matrix(genes_of_interest,db_id):
    feature_df = generate_feature_df(genes_of_interest,db_id)
    feature_list = [x for x in feature_df.columns]
    return feature_df.as_matrix(),feature_list

def query_database(sql_query,list_name,db_cursor):
    db_cursor.execute(sql_query,[list_name])
    result = db_cursor.fetchall()
    returned_gene_list = [x[0] for x in result]
    return returned_gene_list

def scrub(input_string):
    '''Protect against SQL injection'''
    return ''.join( chr for chr in input_string if (chr.isalnum() or chr=='_'))
