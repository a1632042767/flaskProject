from flask.views import MethodView
from flask import request
from extension import db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class UserApi(MethodView):
    # 查询数据的接口
    def get(self, id):
        try:
            if not id:
                users: [User] = User.query.all()
                results = [
                    {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'join_time': user.join_time.strftime('%Y-%m-%d')
                    } for user in users
                ]
                return {
                    'status': 'success',
                    'message': '用户查询成功',
                    'results': results
                }
            user: User = User.query.get(id)
            if not user:
                return {
                    'status': 'false',
                    'message': '用户不存在',
                }

            return {
                'status': 'success',
                'message': '数据查询成功',
                'result': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }
        except Exception as e:
            print(e)
            return {
                'status': 'false',
                'message': '用户查询失败'
            }

    def post(self):
        form = request.json
        checkEmail = User.query.filter_by(email=form.get('email')).first()
        checkUser = User.query.filter_by(username=form.get('username')).first()

        if checkEmail:
            return {
                'status': 'false',
                'message': '邮箱已被注册！'
            }
        if checkUser:
            return {
                'status': 'false',
                'message': '用户名重复！'
            }

        try:
            user = User()
            user.username = form.get('username')
            user.password = generate_password_hash(form.get('password'))
            user.email = form.get('email')
            db.session.add(user)
            db.session.commit()

            return {
                'status': 'success',
                'message': '用户添加成功'
            }
        except Exception as e:
            print(e)
            return {
                'status': 'false',
                'message': '用户添加失败'
            }

    def delete(self, id):
        user = User.query.get(id)
        if not user:
            return {
                'status': 'false',
                'message': '用户不存在'
            }
        try:
            db.session.delete(user)
            db.session.commit()

            return {
                'status': 'success',
                'message': '用户删除成功'
            }
        except Exception as e:
            print(e)
            return {
                'status': 'false',
                'message': '用户删除失败'
            }

    def put(self, id):
        username = request.json.get('username')
        password = request.json.get('password')
        email = request.json.get('email')
        checkEmail = User.query.filter_by(email=email).first()
        checkUser = User.query.filter_by(username=username).first()
        if checkEmail and checkEmail.id != id:
            return {
                'status': 'false',
                'message': '邮箱已被注册！'
            }
        if checkUser and checkUser.id != id:
            return {
                'status': 'false',
                'message': '用户名重复！'
            }
        try:
            user: User = User.query.get(id)
            user.username = username
            if not password:
                user.password = generate_password_hash(password)
            user.email = email
            db.session.commit()

            return {
                'status': 'success',
                'message': '用户修改成功'
            }
        except Exception as e:
            print(e)
            return {
                'status': 'false',
                'message': '用户修改失败'
            }
