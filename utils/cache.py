# pip install redis

import redis

# 需要下载 redis

'''
教学：
    https://www.bilibili.com/video/BV17D4y1M7ha/?spm_id_from=333.337.search-card.all.click&vd_source=9487a22c8e8addbcaaaade7004791ee5

下载地址：
    https://github.com/tporadowski/redis
    https://github.com/lework/RedisDesktopManager-Windows

cmd配置：
    C:/Users\Administrator>redis-cli
    127.0.0.1:6379> set name flove
    OK
    127.0.0.1:6379> get name
    "flove"
    127.0.0.1:6379> set key flove
    OK
    127.0.0.1:6379> get key
    "flove"
    127.0.0.1:6379> config set requirepass 123456
    OK
    127.0.0.1:6379> get name
    (error) NOAUTH Authentication required.
    127.0.0.1:6379> auth 123456
    OK
    127.0.0.1:6379> get name
    "flove"
'''

POOL = redis.ConnectionPool(host='localhost',
                            port=6379,
                            password='123456',
                            encoding='utf-8',
                            max_connections=1000)


def push_queue(value):
    conn = redis.Redis(connection_pool=POOL)

    conn.lpush('DAY21_TASK_QUEUE', value)
