# encoding: utf-8
from datetime import datetime
# from sqlalchemy.dialects import mysql#
from exts import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.VARCHAR(100), nullable=False)
    password = db.Column(db.VARCHAR(100), nullable=False, default='123456', server_default='123456')
    create_time = db.Column(db.DATETIME, nullable=False, default=datetime.now, server_default=db.func.now())
    modify_time = db.Column(db.DATETIME, nullable=False, default=datetime.now, server_default=db.func.now())
    avatar_path = db.Column(db.VARCHAR(100), nullable=False, default='images/avatar/default.png')



