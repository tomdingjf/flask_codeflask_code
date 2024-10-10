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

    if not url or not count:
        return render_template('order_create.html')
    print(url, count)

    user_id = session.get('user_info')['id']
    params = [url, count, user_id]
    insert_id = db.insert("insert into `order`(url,count,user_id,status) values(%s,%s,%s,1)", params)
    print(insert_id)

    # 写入redis队列
    cache.push_queue(insert_id)

    return redirect('/order/list')


@od.route('/order/userinfo')
def delete_list():
    # 判断是否为管理员
    my_role = session.get('user_info')['role']
    print(f"角色是：{my_role}")

    my_id = session.get('user_info')['id']
    print(f"您的id是：{my_id}")

    if my_role == 2:
        userinfo = db.fetch_all("select * from userinfo", [])
        print(f"userinfo_管理员:{userinfo}")
        return render_template('userinfo.html', userinfo=userinfo)
    else:
        userinfo = [db.fetch_one("select * from userinfo where userinfo.id = %s  ", [my_id])]

        print(f"userinfo_用户:{userinfo}")
        return render_template('userinfo.html', userinfo=userinfo)


@od.route('/order/createuser', methods=['GET', 'POST'])
def create_user():
    my_role = session.get('user_info')['role']
    if my_role != 2:
        print(f"您的角色是：客户,无法添再加账户")
        text = "您的角色是：客户,无法添再加账户"
        # return redirect('/order/userinfo')
        return render_template('user_result.html', text=text)

    if request.method == 'GET':
        return render_template('create_user.html')
    print(f"request.form:{request.form}")

    # 获取输入的数据
    my_mobile = request.form.get('mobile')
    my_password = request.form.get('password')
    my_real_name = request.form.get('real_name')
    my_role = request.form.get('role')
    print(my_mobile, my_password, my_real_name, my_role)

    # 添加到数据库
    if my_mobile and my_password and my_real_name and my_role:
        params = [my_mobile, my_password, my_real_name, my_role]
        insert_user = db.insert("insert into userinfo (mobile,password,real_name,role) values(%s,%s,%s,%s)", params)
        print(insert_user)
        return redirect('/order/userinfo')
    else:
        return render_template('create_user.html')
