from flask import Flask, request, render_template, session, redirect
import sqlite3
from datetime import timedelta
from model import User
from flask_login import login_user, login_required
from flask_login import LoginManager, current_user
from flask_login import logout_user
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app=app)

# 这个callback函数用于reload User object，根据session中存储的user id
@login_manager.user_loader
def load_user(user_name):
    return User.get(user_name)

# 主页，指向登录页、注册页、信息页、反馈页
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html")

# 登陆页
@app.route('/signin', methods=['GET'])
def signin_form():
    return render_template("login.html")

# 登陆验证
@app.route('/signin', methods=['POST'])
def signin():
    name = request.form['username']
    passwd = request.form['password']
    remember_me = request.form.get('remember_me')
    print(remember_me)

    user = User(name)
    if user.verify_password(passwd):
        login_user(user)
        return redirect('/index')
    else:
        return '<h3>Bad username or password.</h3>'

@app.route('/index', methods=['GET'])
@login_required
def index_page():
    return '''
    <h3 style="text-align: center;">Hello, {name}!</h3>
    <button style="text-align: center;"><a href="/logout">登出</a></button>
    '''.format(name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/signin')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect('/signin')

@app.route('/signup', methods=['GET'])
def signup_form():
    return '''<form action="/signup" method="POST" name="signup">
        <h3>请输入要注册的用户名和密码：</h3>
        <p>新用户名<input name="new_username"></p>
        <p>密码：<input name="new_password" type="password"></p>
        <p><button type="submit">Sign Up</button></p>
        </form>'''

@app.route('/signup', methods=['POST'])
def signup():
    # 应修改为自己电脑上.db文件的地址
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    name = request.form['new_username']
    pwd = request.form['new_password']
    cursor.execute('''
        SELECT username
        FROM user
        WHERE username = '{name}'
    '''.format(name=name))

    values = cursor.fetchall()
    if len(values) != 0:
        return '''
            <h3>注册失败：用户已存在!</h3>
        '''
    
    cursor.execute('''
        INSERT INTO user
        VALUES('{name}','{pwd}')
    '''.format(name=name, pwd=pwd))
    conn.commit()
    conn.close()

    result = '''
    <h3>欢迎来到我们的社区，{name}！</h3>
    <p>请保存好你的用户名和密码！</p>
    '''.format(name=name)
    return result

@app.route('/search', methods=['GET'])
def search_form():
    return '''<form action="/search" method="POST" name="search">
        <h3>请输入要查找的姓名：</h3>
        <p><input name="username"></p>
        <p><button type="submit">Search</button></p>
        </form>'''

@app.route('/search', methods=['POST'])
def search():
    # 应修改为自己电脑上.db文件的地址
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    name = request.form['username']

    string = '''
        SELECT *
        FROM info
        WHERE username = '{name}'
    '''.format(name=name)
    cursor.execute(string)

    values = cursor.fetchall()

    conn.commit()
    conn.close()

    if len(values) == 0:
        return '''
            <h3>用户{name}不存在!</h3>
        '''.format(name=name)
    
    return '''
        <h3>个人信息：</h3>
        <table border="1">
        <tr>
            <td>用户名</td>
            <td>年龄</td>
            <td>所在部门</td>
        </tr>
        <tr>
            <td>{0}</td>
            <td>{1}</td>
            <td>{2}</td>
        </tr>
        </table>
    '''.format(values[0][0], values[0][1], values[0][2])

if __name__ == '__main__':
    app.run()
