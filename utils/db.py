import pymysql
from dbutils.pooled_db import PooledDB
from pymysql import cursors




POOL = PooledDB(creator=pymysql,  # 指定数据库连接器
                mincached=2,  # 连接池中初始最少空闲连接数
                maxcached=10,  # 连接池中最多空闲连接数
                maxconnections=20,  # 连接池允许的最大连接数
                blocking=True,  # 当连接池中没有可用连接时，是否阻塞等待
                setsession=[],  # 开始会话前执行的命令列表，如：['set tx isolation level read committed']
                ping=0,  # 检查数据库连接是否可用的频率，0表示不检查
                host='localhost',  # 数据库主机地址
                port=3306,  # 数据库端口
                user='root',  # 数据库用户名
                password='123456',  # 数据库密码
                db='day21',  # 要连接的数据库名
                charset='utf8mb4')  # 字符集


def fetch_one(sql, params):
    coon = POOL.connection()
    cursor = coon.cursor(cursor=cursors.DictCursor)
    cursor.execute(sql, params)
    result = cursor.fetchone()
    cursor.close()
    coon.close()  # 将此链接交还给连接连接池
    return result


def fetch_all(sql, params):
    coon = POOL.connection()
    cursor = coon.cursor(cursor=cursors.DictCursor)
    cursor.execute(sql, params)
    result = cursor.fetchall()
    cursor.close()
    coon.close()  # 将此链接交还给连接连接池
    return result


def insert(sql, params):
    coon = POOL.connection()
    cursor = coon.cursor(cursor=cursors.DictCursor)
    cursor.execute(sql, params)
    coon.commit()
    cursor.close()
    coon.close()  # 将此链接交还给连接连接池
    insert_id = cursor.lastrowid
    return insert_id
