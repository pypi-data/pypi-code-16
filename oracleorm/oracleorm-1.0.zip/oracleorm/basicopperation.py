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
