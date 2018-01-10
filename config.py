# encoding: utf-8

#开启debug模式
DEBUG = True

#SQLAlchemy连接数据库配置
DIALECT = 'mysql'
DRIVER = 'mysqldb'
USERNAME = 'user'
PASSWORD = 'happy100'
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = 'Mine'
SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT,
                                                                       DATABASE)
SQLALCHEMY_TRACK_MODIFICATIONS = False