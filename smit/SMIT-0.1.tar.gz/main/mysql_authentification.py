from django.conf import settings
import MySQLdb

def mysqlAuthentification(email, password):
    
    db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                      passwd="null", # your password
                      db="auth_db") # name of the data base

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor() 

# Use all the SQL you like
    cur.execute("SELECT * FROM authentification")

# print all the first cell of all the rows
    for row in cur.fetchall() :
    print row[0]
    print row[1]

    print "mysql enter"
    
    result = {
        'userEmail':"",
        'userName':"",
        'department':""
        }
    print "test"
    print "user = %s " % email 
    print "password = %s " % password
    
        
    result['userEmail']=row[0]
    result['userName']=row[1]
        
    try:
        result['department']="informatique"#str(dict[''])[2:-2]
    except KeyError:
        result['department']=None
        

    print result    
    return result

print mysqlAuthentification("admin@test.fr","admin312")
