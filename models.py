# encoding: utf-8
from datetime import datetime
from sqlalchemy.dialects import mysql
from exts import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.VARCHAR(100), nullable=False)
    password = db.Column(db.VARCHAR(100), nullable=False, default='123456', server_default='123456')
    create_time = db.Column(db.DATETIME, nullable=False, default=datetime.now, server_default=db.func.now())
    modify_time = db.Column(db.DATETIME, nullable=False, default=datetime.now, server_default=db.func.now())
    avatar_path = db.Column(db.VARCHAR(100), nullable=False, default='images/avatar/default.png')



class Label(db.Model):
    __tablename__ = 'label'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.VARCHAR(50), nullable=False, default='', server_default='')
    parent_id = db.Column(db.BigInteger, db.ForeignKey('label.id'))

    parent = db.relationship(
        'Label',
        uselist=False,
        remote_side=[id],
        backref=db.backref('children')
    )


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    title = db.Column(db.VARCHAR(100), nullable=False, default='', server_default='')
    info = db.Column(db.Text, nullable=False, default='')
    content = db.Column(mysql.LONGTEXT(), nullable=False, default='')
    create_time = db.Column(db.DATETIME, nullable=False, default=datetime.now, server_default=db.func.now())
    modify_time = db.Column(db.DATETIME, nullable=False, default=datetime.now, server_default=db.func.now())
    good_count = db.Column(db.BigInteger, nullable=False, default=0, server_default='0')
    click_count = db.Column(db.BigInteger, nullable=False, default=0, server_default='0')
    author_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    label_id = db.Column(db.BigInteger, db.ForeignKey('label.id'), nullable=False)

    author = db.relationship('User', backref=db.backref('articles'), order_by=modify_time.desc())
    label = db.relationship('Label', backref=db.backref('articles', order_by=modify_time.desc()))


class Good(db.Model):
    __tablename__ = 'good'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    article_id = db.Column(db.BigInteger, db.ForeignKey('article.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)

    article = db.relationship('Article', backref=db.backref('goods'))
    user = db.relationship('User', backref=db.backref('goods'))
    __table_args__ = (db.UniqueConstraint('article_id', 'user_id', name='unique_article_user'),)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False, default='')
    create_time = db.Column(db.DATETIME, nullable=False, default=datetime.now, server_default=db.func.now())
    article_id = db.Column(db.BigInteger, db.ForeignKey('article.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)

    article = db.relationship('Article', backref=db.backref('comments'), cascade='all, delete',
                              order_by=create_time.desc())
    user = db.relationship('User', backref=db.backref('comments'), order_by=create_time.desc())


class UserAuthority(db.Model):
    __tablename__ = 'user_authority'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    authority = db.Column(db.VARCHAR(100), nullable=False, default='admin', server_default='admin')
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('user_authorities'))