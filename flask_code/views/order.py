from flask import Blueprint, session, redirect, render_template, request
from utils import db, cache
from utils import getnovel

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


@od.route('/order/novel', methods=['GET', 'POST'])
def order_novel():
    print(f'/order/novel:{request.method}')
    if request.method == 'GET':
        return render_template('order_novel.html')
    novelID = request.form.get('novelID')
    print(novelID)

    # 请求用户输入小说ID，用于后续获取小说章节信息
    # 获取标题链接，章节名称
    novel_id = novelID
    novel_name = ''
    # 调用get_chapters函数获取小说的章节标题列表、章节链接列表、小说名称和作者

    title_list, link_list, novel_name, novel_author = getnovel.get_chapters(f'https://www.bigee.cc/book/{novel_id}/')

    # 创建数据库表，以小说名称作为表名，用于存储小说内容
    getnovel.create_db_table(table_name=novel_name)

    # 输出小说的基本信息
    print(f'小说名称：{novel_name}--作者：{novel_author}')

    # 获取标题列表的长度，用于后续生成章节索引列表
    # 初始化变量count，用于存储title_list的长度
    count = len(title_list)
    # 生成章节索引列表，用于标识每个章节的顺序
    # 生成一个列表count_lists，包含从1到count（包含count）的所有整数
    # 这里使用列表推导式，以便简洁地创建一个有序的数字列表
    index_lists = [i for i in range(1, count + 1)]

    # 使用ThreadPoolExecutor创建一个线程池，最大工作线程数为8
    with getnovel.ThreadPoolExecutor(max_workers=8) as t:  # 创建8个线程
        # 遍历章节索引、标题和链接列表，为每个章节提交一个获取内容的任务
        # 每个任务将异步执行，提高程序的执行效率
        for count_list, title, link in zip(index_lists, title_list, link_list):
            print(index_lists, title_list, link_list)

            t.submit(getnovel.get_content, count_list, title, link)  # 启动线程

    return render_template('order_novel.html')


@od.route('/order/getnovel', methods=['GET', 'POST'])
def get_novel():
    print(f'/order/getnovel:{request.method}')
    if request.method == 'POST':
        novelID = request.form.get('novelID')
        print(novelID)
    return render_template('getnovel.html')


@od.route('/order/delete', methods=['GET', 'POST'])
def delete_list():
    if request.method == 'GET':
        print("delete_list")
        return render_template('delete_list.html')
    delete_id = request.form.get('delete_id')
    print(f'delete_id:{delete_id}')
    db.delete_data("delete from `order` where id=%s", [delete_id])
    # db.fetch_one("delete from `order` where id=%s", [order_id])
    return redirect('/order/list')


@od.route('/order/userinfo')
def create_userinfo():
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
