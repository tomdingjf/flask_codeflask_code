from pythonproject import create_app
import time
from worker import main

'''
输出环境 requirements.txt
    pip freeze > requirements.txt

运行 requirements.txt 安装环境
    pip install -r requirements.txt

教学视频：
    https://www.bilibili.com/video/BV1vD421E7cC?p=2&spm_id_from=pageDriver&vd_source=9487a22c8e8addbcaaaade7004791ee5
'''

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
