from pythonproject import create_app

'''
输出环境 requirements.txt
    pip freeze > requirements.txt

运行 requirements.txt 安装环境
    pip install -r requirements.txt

sql输出 dump-day21-202410100821.sql 文件
    选择数据库day21，day21 -> 工具 -> 转储数据库
    
sql文件执行 dump-day21-202410100821.sql
    在DBever选择数据库执行脚本即可


教学视频：
    https://www.bilibili.com/video/BV1vD421E7cC?p=2&spm_id_from=pageDriver&vd_source=9487a22c8e8addbcaaaade7004791ee5
'''

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000,debug=True)
