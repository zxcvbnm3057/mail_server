# -*- coding: utf-8 -*-

import pymysql

def auth(username,passwd):
    sql="SELECT passwd FROM auth_db WHERE user={}".format(username)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()[0]
        if result==passwd:
            return True
        else:
            return False
    except:
        return False

def get_username(username):
    sql="SELECT user FROM WHERE user={}".format(username)
    try:
        cursor.execute(sql)
        if not cursor.fetchall()[0]:
            return True
        else:
            return False
    except:
        return False
        
def register(username,passwd):
    sql = "INSERT INTO auth_db (user,passwd) VALUES ({0},{1})".format(username,passwd)
    try:
        cursor.execute(sql)
        auth_db.commit()
        return True
    except:
        auth_db.rollback()
        return False

def unsubscribe(username):
    sql = "DELETE FROM auth_db WHERE user = {1}".format(username)
    try:
        cursor.execute(sql)
        auth_db.commit()
        return True
    except:
        auth_db.rollback()
        return False

def reset_passwd(username,newpasswd):
    sql = "UPDATE auth_db SET passwd = {0} WHERE user = {1}".format(newpasswd,username)
    try:
        cursor.execute(sql)
        auth_db.commit()
        return True
    except:
        auth_db.rollback()
        return False

def init(db_host,db_name,db_user,db_passwd):
    global cursor,auth_db
    auth_db=pymysql.connect(db_host,db_user,db_passwd,db_name)
    cursor=auth_db.cursor()
