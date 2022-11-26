import pymysql
import logging
import time, sys, re
from password_generator import id_generator
from write_to_file import *

# SET LOGGING
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler('./logs/mysql_onboard_user_error.log')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
t = time.localtime()
timestamp = time.strftime('%b-%d-%Y %H:%M', t)

onboard_user_pass = id_generator(size=15)

### This will get host name of the Mysql user ####
def get_host_for_user(user):
    db = pymysql.connect(host='10.*.*.*', user='root', passwd='********', db='mysql', port=3306)
    cursor1 = db.cursor()
    cursor1.execute('SELECT host FROM mysql.user WHERE user=?', (user))
    result_set = cursor1.fetchall()
    host_var = result_set[0]["host"]
    db.commit()
    cursor1.close()
    db.close()
    
    return host_var

### This will delete DEV Specific Account ####
def Mysql_User_Dev_Delete(firstname, lastname):
    db = pymysql.connect(host='10.*.*.*', user='root', passwd='********', db='mysql', port=3306)
    onboarding_user_name = firstname + "." + lastname
    cursor1 = db.cursor()
    checkUsername = cursor1.execute('SELECT User FROM user WHERE User=?', (onboarding_user_name))
    
    if checkUsername != 0:
      print('Username not exist in the DB...skipping the operation...')
      pass
    else:
      print('User exists!')
      host_var = get_host_for_user(onboarding_user_name)
      drop_user_query = "DROP USER '%s'@'%s'" % (onboarding_user_name, host_var)
      cursor1.execute(drop_user_query)
      db.commit()
      cursor1.close()
    
    db.close()

### Onboarding user with Dev Mysql Account ####
def Mysql_User_Dev_Create(firstname, lastname):
    db = pymysql.connect(host='10.*.*.*', user='root', passwd='********', db='mysql', port=3306)
    onboarding_user_name = firstname + "." + lastname
    file = firstname + "." + lastname
    try:
        ### Create User ###
        create_query = "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s'" %(onboarding_user_name, onboard_user_pass)
        cursor1 = db.cursor()
        cursor1.execute(create_query)
        db.commit()
        cursor1.close()

        ### Grant role to the created user ###
        grant_role_query = "GRANT SELECT ON *.* TO '%s'@'%';" %(onboarding_user_name)
        cursor1 = db.cursor()
        cursor1.execute(grant_role_query)
        db.commit()
        cursor1.close()

        db.close()
        write_to_file("Mysql dev env user creating ", file, onboarding_user_name, "<please reset password from homepage>")
    except:
        db.rollback()
        logger.exception('MysqlDevUserCreate using portal ################ ERROR ##############')
        write_exception("MysqlDevUserCreate", file)