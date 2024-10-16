import os
from concurrent.futures import ThreadPoolExecutor
from time import sleep
import pymysql
import requests
from lxml import etree


# '''
# 数据库名称：day21
# '''


def create_db_table(table_name='table_name'):
    """
    根据给定的表名创建数据库表。

    :param table_name: 表的名字，默认为'table_name'。
    :return: 创建的表名。
    """
    # 获取数据库连接和游标
    db_connection, cursor = get_conn()

    # 构建创建表的SQL语句
    # 使用format字符串格式化方法创建SQL语句，用以创建新表
    sql = f'''
    create table {table_name}(
    id int,
    chapter_name varchar(100),
    content text
    );
    '''

    try:
        # 尝试执行SQL语句来创建表
        # 执行SQL语句
        cursor.execute(sql)
    except Exception as e:
        # 如果出现异常，打印错误信息
        print(f'创建表失败：{e}')
    else:
        # 如果没有异常，提交事务
        # 提交更改
        db_connection.commit()

    finally:
        # 确保关闭游标和数据库连接
        # 确保游标和数据库连接被关闭
        cursor.close()
        db_connection.close()

    # 返回表名
    return table_name


def get_conn(db_name='day21'):
    """
    获取数据库连接及游标。

    本函数尝试根据环境变量配置连接到MySQL数据库，如果环境变量未设置，则使用默认值。
    默认数据库名为'day21'，可以通过参数进行修改。

    参数:
    db_name (str): 需要连接的数据库名称，默认为'day21'。

    返回:
    tuple: 包含数据库连接对象和游标对象的元组，如果连接失败则返回None。
    """
    # 从环境变量中获取数据库主机地址，默认为'localhost'
    # 创建连接
    # 从环境变量读取数据库连接信息，提高安全性
    db_host = os.getenv('DB_HOST', 'localhost')
    # 从环境变量中获取数据库用户名，默认为'root'
    db_user = os.getenv('DB_USER', 'root')
    # 从环境变量中获取数据库密码，默认为'123456'
    db_password = os.getenv('DB_PASSWORD', '123456')
    # 从环境变量中获取数据库端口号，默认为3306，转换为整型
    db_port = int(os.getenv('DB_PORT', 3306))

    # 尝试建立到MySQL数据库的连接
    # 连接MySQL数据库
    try:
        # 使用pymysql库建立连接
        db_connection = pymysql.Connect(host=db_host, user=db_user, password=db_password, port=db_port, db=db_name, charset='utf8mb4')
    except Exception as e:
        # 如果连接过程中出现异常，打印错误信息并返回None
        print(f"数据库连接失败：{e}")
        return None

    # 创建游标对象
    # 创建游标
    cursor = db_connection.cursor()
    # 返回数据库连接对象和游标对象的元组
    return db_connection, cursor


def close_conn(db_connection, cursor):
    cursor.close()
    db_connection.close()


def get_xpath_resp(url):
    cookies = {
        'Hm_lvt_985c57aa6304c183e46daae6878b243b': '1718583213',
        'Hm_lvt_b147be33903fb4b5cd5f16843ab81a1d': '1717989626,1718583189,1718722956,1718762511',
        'Hm_lpvt_b147be33903fb4b5cd5f16843ab81a1d': '1718763530',
    }

    headers = {
        'referer': 'https://www.bigee.cc/',

        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    }

    resp = requests.get(url, cookies=cookies, headers=headers)
    sleep(0.5)
    resp.encoding = 'utf-8'
    tree = etree.HTML(resp.text)  # 用etree解析html
    # print(resp.text)
    return tree, resp


def get_chapters(url):
    tree, _ = get_xpath_resp(url)
    # 获取小说名字
    novel_name = tree.xpath('//h1/text()')[0]
    novel_author = tree.xpath('/html/body/div/div/div/span/text()')[0]
    # 获取小说数据节点
    title_list = tree.xpath('//*/div[@class="listmain"]/dl//dd/a/text()')
    link_list = tree.xpath('//*/div[@class="listmain"]/dl//dd/a//@href')
    link_list1 = []
    for i in link_list:
        link = 'https://www.bigee.cc/' + i
        link_list1.append(link)
    link_list = link_list1
    # print(novel_name, title_list, link_list)
    return title_list, link_list, novel_name, novel_author


def get_content(count_list, title, url):
    """
    从指定的URL获取小说内容，并将其存储到数据库中。

    :param count_list: 用于唯一标识小说章节的序列号列表
    :param title: 小说章节的标题
    :param url: 小说章节内容的URL
    """
    try:
        # 初始化数据库连接和游标
        cursor = None
        conn = None
        conn, cursor = get_conn()

        # 准备插入数据的SQL语句
        # 插入数据的sql
        sql = f'INSERT INTO {novel_name} (id,chapter_name,content) VALUES(%s,%s,%s)'

        # 获取网页内容并解析
        tree, resp = get_xpath_resp(url)
        # 提取章节内容，去除无关信息
        # 获取内容
        content = ''.join(tree.xpath('//*[@id="chaptercontent"]/text()'))
        content = content.replace('请收藏本站：https://www.bigee.cc。笔趣阁手机版：https://m.bigee.cc', '')

        # 执行SQL语句，将章节信息插入数据库
        print(f'正在写入数据库：{title}')
        cursor.execute(sql, [count_list, title, content])  # 插入数据
        conn.commit()  # 提交事务保存数据
    except Exception as e:
        print(e)
        print('出错啦')
    finally:
        # 确保数据库连接关闭
        sleep(2)
        close_conn(conn, cursor)  # 关闭数据库


# 当模块作为主程序运行时，执行以下代码
if __name__ == '__main__':
    # 请求用户输入小说ID，用于后续获取小说章节信息
    # 获取标题链接，章节名称
    novel_id = input('请输入小说ID：')
    # 调用get_chapters函数获取小说的章节标题列表、章节链接列表、小说名称和作者
    title_list, link_list, novel_name, novel_author = get_chapters(f'https://www.bigee.cc/book/{novel_id}/')
    # 创建数据库表，以小说名称作为表名，用于存储小说内容
    create_db_table(table_name=novel_name)

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
    with ThreadPoolExecutor(max_workers=8) as t:  # 创建8个线程
        # 遍历章节索引、标题和链接列表，为每个章节提交一个获取内容的任务
        # 每个任务将异步执行，提高程序的执行效率
        for count_list, title, link in zip(index_lists, title_list, link_list):
            t.submit(get_content, count_list, title, link)  # 启动线程
