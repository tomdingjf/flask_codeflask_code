import redis
import pymysql
from dbutils.pooled_db import PooledDB
from pymysql import cursors
from concurrent.futures import ThreadPoolExecutor
import time

DB_POOL = PooledDB(creator=pymysql,  # 指定数据库连接器
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

POOL = redis.ConnectionPool(host='localhost',
                            port=6379,
                            password='123456',
                            encoding='utf-8',
                            max_connections=1000)


def fetch_one(sql, params):
    coon = DB_POOL.connection()
    cursor = coon.cursor(cursor=cursors.DictCursor)
    cursor.execute(sql, params)
    result = cursor.fetchone()
    cursor.close()
    coon.close()  # 将此链接交还给连接连接池
    return result


def fetch_all(sql, params):
    coon = DB_POOL.connection()
    cursor = coon.cursor(cursor=cursors.DictCursor)
    cursor.execute(sql, params)
    result = cursor.fetchall()
    cursor.close()
    coon.close()  # 将此链接交还给连接连接池
    return result


def pop_queue():
    conn = redis.Redis(connection_pool=POOL)

    data = conn.brpop(['DAY21_TASK_QUEUE'], timeout=10)

    if not data:
        return
    data = data[1].decode('utf-8')
    return data


def fetch_total_queue():
    conn = redis.Redis(connection_pool=POOL)
    total_count = conn.llen('DAY21_TASK_QUEUE')
    conn.lrange(name='DAY21_TASK_QUEUE', start=0, end=11)


def db_queue_init():
    '''
    1.去数据库中找待执行的订单id
    2.去redis中找待执行的id
    3.找到数据库中有，但redis没有的订单，加入到队列中

    :return:
    '''

    db_list = fetch_all("select id from `order` where status=1", [])

    #     [{'id': 1}, {'id': 4}, {'id': 5}, {'id': 6}, {'id': 7}, {'id': 8}, {'id': 9}, {'id': 10}]
    db_id_dict = {item['id'] for item in db_list}
    # print(db_id_dict)
    #     [1, 4, 5, 6, 7, 8, 9, 10]

    # 在reids中找所以有的id
    conn = redis.Redis(connection_pool=POOL)
    total_count = conn.llen('DAY21_TASK_QUEUE')
    cache_list = conn.lrange(name='DAY21_TASK_QUEUE', start=0, end=total_count)
    cache_int_dict = {int(item.decode('utf-8')) for item in cache_list}

    # 3.找到数据库中有，但redis没有的订单，加入到队列中
    need_push = db_id_dict - cache_int_dict

    # 4.放到redis队列中
    print(need_push)

    if need_push:
        # conn.lpush(name='DAY21_TASK_QUEUE',  * need_push)
        conn.lpush('DAY21_TASK_QUEUE', *need_push)


def get_order_obj(order_id):
    res = fetch_one("select * from `order` where id=%s", [order_id])
    return res


def db_update(sql, params):
    coon = DB_POOL.connection()
    cursor = coon.cursor(cursor=cursors.DictCursor)
    cursor.execute(sql, params)
    coon.commit()
    cursor.close()
    coon.close()  # 将此链接交还给连接连接池


def update_order(order_id, status):
    db_update("update `order` set status = %s where id=%s", [status, order_id])


def task(info_dict):
    print('开始执行')
    time.sleep(3)
    print(f'执行完成！{info_dict}' )


def main():

    db_queue_init()

    while True:
        insert_id = pop_queue()
        print(insert_id)
        if not insert_id:
            continue

        # 订单是否存在
        order_dict = get_order_obj(insert_id)
        if not order_dict:
            continue

        # 4.更新订单状态
        update_order(insert_id, 2)

        # 5.执行订单
        print('执行订单', order_dict)
        thread_pool = ThreadPoolExecutor(10)

        print('开始执行订单', order_dict['count'])

        for i in range(order_dict['count']):

            thread_pool.submit(task, order_dict)

        thread_pool.shutdown()

        # 6.更新订单状态
        update_order(insert_id, 3)


if __name__ == '__main__':
    main()
