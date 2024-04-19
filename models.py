# coding: utf-8
from extension import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    join_time = db.Column(db.DateTime, default=datetime.now)
    downloadpath = db.Column(db.String(50), default=f"C:\\")


class EmailCode(db.Model):
    __tablename__ = 'emailcode'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(100), nullable=False)


class UserInfoByBaidu(db.Model):
    __tablename__ = 'userinfobybaidu'

    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    cookies = db.Column(db.Text)


class UserInfoDouding(db.Model):
    __tablename__ = 'userinfobydouding'

    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    cookies = db.Column(db.Text)

# flask db init: 只需要执行一次
# flask db migrate: 将orm模型生成迁移脚本
# flask db upgrade: 将迁移脚本映射到数据库

    #
    # def to_json(self):
    #     return {
    #         'id': self.id,
    #         'username': self.username,
    #         'password': self.password,
    #         'email': self.email
    #     }
