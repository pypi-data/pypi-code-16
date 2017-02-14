import cx_Oracle as orcl

def conn(username,passwd,host,port,sid):
    dsn = orcl.makedsn(host,port,sid)
    con = orcl.connect(username,passwd,dsn)
    return con
def selall(con,tablename):
    cursor =con.cursor()
    sql = "select * from "+tablename
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()

    return result
def insertall(con,tablename,value):
    cursor = con.cursor()
    sql = "insert into "+tablename+" values("
    for v in range(0,len(value)-1):
        if isinstance(value[v], str):
         sql+="'"+str(value[v])+"',"
        else:
         sql += str(value[v]) + ","
    if isinstance(value[len(value)-1], str):
       sql+="'"+str(value[len(value)-1])+"')"
    else:
        sql += str(value[len(value) - 1]) + ")"
    print sql
    cursor.execute(sql)
    con.commit()
    cursor.close()

def updateall(con,tablename,dict1,dict2):
    cursor = con.cursor()
    sql="update "+tablename+" set "
    flag=0
    flag2=0
    for key,value in dict1.items():
        flag=flag+1
        if flag<len(dict1):
            if isinstance(value, str):
                sql+=str(key)+"='"+str(value)+"',"
            else:
                sql += str(key) + "=" + str(value) + ","
        else:
            if isinstance(value, str):
                sql+=str(key)+"='"+str(value)+"' where"
            else:
                sql += str(key) + "=" + str(value) + " where "
    for key,value in dict2.items():
        flag2=flag2+1
        if flag2 < len(dict1):
            if isinstance(value, str):
                sql += str(key) + "='" + str(value) + "' and "
            else:
                sql += str(key) + "=" + str(value) + " and "
        else:
            if isinstance(value, str):
                sql += str(key) + "='" + str(value)+"'"
            else:
                sql += str(key) + "=" + str(value)
    cursor.execute(sql)
    con.commit()
    cursor.close()

def deleteall(con,tablename):
    cursor = con.cursor()
    sql="delete from "+tablename
    cursor.execute(sql)
    con.commit()
    cursor.close()
