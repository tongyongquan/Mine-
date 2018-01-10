# encoding: utf-8

from flask_sqlalchemy import SQLAlchemy
#为解决循环调用,在这定义db
db = SQLAlchemy()

# class MySQLAlchemy(SQLAlchemy):
#     def create_session(self, options):
#         options['autoflush'] = False
#         return super(MySQLAlchemy, self).create_session(options)



