from flask import Blueprint, render_template, request, redirect, session
from utils import db

ac = Blueprint('account', __name__)


# pip uninstall xxx
@ac.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    role = request.form.get('role')
    mobile = request.form.get('mobile')
    pwd = request.form.get('pwd')
    print(role, mobile, pwd)

    # # 去数据库校验
    # import pymysql
    # conn = pymysql.connect(host='localhost', port=3306, user='root', password='123456', db='day21')
    # cursor = conn.cursor()
    # cursor.execute("select * from userinfo where role=%s and mobile=%s and password=%s", [role, mobile, pwd])
    # user_dict = cursor.fetchone()
    # cursor.close()
    # conn.close()

    user_dict = db.fetch_one("select * from userinfo where role=%s and mobile=%s and password=%s", [role, mobile, pwd])
    print(user_dict)

    if user_dict:
        # 登录成功+进行跳转
        session['user_info'] = {'role': user_dict['role'], 'real_name': user_dict['real_name'], 'id': user_dict['id']}
        print(session)
        # <SecureCookieSession{'user_info': {'role': 1, 'real_name': '刘娜', 'id': 2}} >
        # <SecureCookieSession {'user_info': {'role': 2, 'real_name': '丁金枫', 'id': 1}}>
        return redirect('/order/list')

    return render_template('login.html', error='用户名或密码错误')


@ac.route('/users')
def users():
    return '用户'


@ac.route('/')
def first_web():
    return render_template('login.html')
