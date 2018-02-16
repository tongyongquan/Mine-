# encoding: utf-8
import os

#开启debug模式
DEBUG = True

#SQLAlchemy连接数据库配置
DIALECT = 'mysql'
DRIVER = 'pymysql'   #'mysqldb'是python2的mysql驱动
USERNAME = 'user'
PASSWORD = 'happy100'
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = 'Mine'
SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT,
                                                                       DATABASE)
SQLALCHEMY_TRACK_MODIFICATIONS = False

#设置session的安全密匙
SECRET_KEY = os.urandom(4)

# 用户session的过期时间 天
session_lifetime = 5