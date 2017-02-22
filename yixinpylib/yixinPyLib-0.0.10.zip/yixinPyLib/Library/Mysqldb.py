# _*_ coding:utf-8 _*_
'''
Created on 2016年12月9日

@author: wuyunpeng
'''
import MySQLdb
import CommonMethod

def search(sql):
    db = MySQLdb.connect(CommonMethod.getdbconf("ip"),CommonMethod.getdbconf("username"),CommonMethod.getdbconf("pwd"),CommonMethod.getdbconf("db"),charset='utf8')
    cursor = db.cursor()
    cursor.execute(sql)
    data = cursor.fetchone()
    db.close()
    return data
def update(sql):
    db = MySQLdb.connect(CommonMethod.getdbconf("ip"),CommonMethod.getdbconf("username"),CommonMethod.getdbconf("pwd"),CommonMethod.getdbconf("db"),charset='utf8')
    cursor = db.cursor()
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()

    # 关闭数据库连接
    db.close()
def insert(sql):
    db = MySQLdb.connect(CommonMethod.getdbconf("ip"),CommonMethod.getdbconf("username"),CommonMethod.getdbconf("pwd"),CommonMethod.getdbconf("db"),charset='utf8')
    cursor = db.cursor()
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        # Rollback in case there is any error
        print "sql报错，回滚"
        db.rollback()
        

    # 关闭数据库连接
    db.close()
    
if __name__ == "__main__":
    data = search("select * from cc_gift where ID = '4028188558c291f20158c2a2e6150006'")
    print data
    for i in range(len(data)):
        print data[i]
    
    
    