from flask import Flask, request, session, redirect


def auth():
    if request.path.startswith('/static'):
        # 不拦截
        return
    if request.path == '/login':
        # 不拦截
        return
    user_info = session.get('user_info')
    if user_info:
        # 不拦截
        return
    return redirect('/login')


def get_real_name():
    user_info = session.get('user_info')
    real_name = user_info['real_name']
    return real_name


def create_app():
    app = Flask(__name__)
    app.secret_key = 'dingjinfeng'

    from .views import account
    from .views import order

    app.register_blueprint(account.ac)
    app.register_blueprint(order.od)

    app.template_global()(get_real_name)

    return app
