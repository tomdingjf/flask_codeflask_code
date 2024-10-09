from flask import Blueprint, session, redirect, render_template, request
from utils import db, cache

od = Blueprint('order', __name__)


@od.route('/order/list')
def order_list():
    user_info = session.get('user_info')
    # print(user_info['id'])
    real_name = user_info['real_name']
    role = user_info['role']  # 2.管理员

    if role == 2:
        # data_list = db.fetch_all("select * from `order`",[])
        data_list = db.fetch_all("select * from `order` left join userinfo on `order`.user_id =userinfo.id;", [])
    else:

        "select * from `order` left join userinfo on `order`.user_id =userinfo.id"
        # data_list = [db.fetch_one("select * from `order` where user_id=%s",[user_info['id'],])]
        data_list = db.fetch_all("select * from `order` left join userinfo on `order`.user_id = userinfo.id where `order`.user_id = %s;", [user_info['id'], ])

    status_dict = {
        1: {"text": '待执行', 'cls': 'primary'},
        2: {"text": '执行中', 'cls': 'info'},
        3: {"text": '已完成', 'cls': 'success'},
        4: {"text": '失败', 'cls': 'danger'}
    }

    print(f"data_list:{data_list}")

    # data_list:[[{'id': 1, 'url': 'http://2c16szdc', 'count': 10, 'user_id': 2, 'status': 1, 'userinfo.id': 2, 'mobile': '13032732453', 'password': '123456', 'real_name': '刘娜', 'role': 1}, {'id': 2, 'url': 'http://sdevs', 'count': 5, 'user_id': 2, 'status': 2, 'userinfo.id': 2, 'mobile': '13032732453', 'password': '123456', 'real_name': '刘娜', 'role': 1}]]
    # data_list:[{'id': 1, 'url': 'http://2c16szdc', 'count': 10, 'user_id': 2, 'status': 1, 'userinfo.id': 2, 'mobile': '13032732453', 'password': '123456', 'real_name': '刘娜', 'role': 1}, {'id': 2, 'url': 'http://sdevs', 'count': 5, 'user_id': 2, 'status': 2, 'userinfo.id': 2, 'mobile': '13032732453', 'password': '123456', 'real_name': '刘娜', 'role': 1}, {'id': 3, 'url': 'http://xahicxuw.com', 'count': 6, 'user_id': 4, 'status': 3, 'userinfo.id': 4, 'mobile': '15242556516', 'password': '999999', 'real_name': '下阿萨', 'role': 1}]

    return render_template('order_list.html', data_list=data_list, status_dict=status_dict)


@od.route('/order/create', methods=['GET', 'POST'])
def create_list():
    if request.method == 'GET':
        return render_template('order_create.html')
    print(request.form)
    url = request.form.get('url')
    count = request.form.get('count')
    print(url, count)

    user_id = session.get('user_info')['id']
    params = [url, count, user_id]
    insert_id = db.insert("insert into `order`(url,count,user_id,status) values(%s,%s,%s,1)", params)
    print(insert_id)

    # 写入redis队列
    cache.push_queue(insert_id)

    return redirect('/order/list')


#   写redis队列


@od.route('/order/create')
def delete_list():
    user_info = session.get('user_info')
    if not user_info:
        return redirect('/login')
    return '删除列表'
