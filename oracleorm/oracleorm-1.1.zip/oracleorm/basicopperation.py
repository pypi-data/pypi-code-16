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
    con.close()
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
    con.close()