from flask import Flask, request, render_template, session, redirect
import sqlite3
from datetime import timedelta
from model import User
from flask_login import login_user, login_required
from flask_login import LoginManager, current_user
from flask_login import logout_user
import os
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app=app)

# 这个callback函数用于reload User object，根据session中存储的user id
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

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
    print(name)

    user = User(name)
    if user.verify_password(passwd):
        login_user(user)
        return redirect('/index')
    else:
        return '<h3>Bad username or password.</h3>'

@app.route('/index', methods=['GET'])
@login_required
def index_page():
    # 应修改为自己电脑上.db文件的地址
    conn = sqlite3.connect("../../RUCCA.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, name, sex, phone, description
        FROM person_info
        WHERE id = ?
    ''', (current_user.id,))
    value = cursor.fetchone()
    user_dict = {
        'username': value[0],
        'name': value[1],
        'sex': value[2],
        'phone': value[3],
        'description': value[4]
    }
    return render_template("index.html", user=user_dict)

@app.route('/info_detail', methods=['GET'])
@login_required
def get_info_detail():
    return "<h1>To be done by lr</h1>"

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
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    # 应修改为自己电脑上.db文件的地址
    conn = sqlite3.connect("../../RUCCA.db")
    cursor = conn.cursor()

    # 查询允许注册的学号表，查看输入的学号是否在其中
    studentid = request.form.get('stuid')
    cursor.execute('SELECT has_signup FROM allowed_signup WHERE studentid = ?', (studentid,))
    value = cursor.fetchall()

    # 不在允许注册的学号表之中，不允许注册
    if len(value) == 0 or value[0][0] == '1':
        return '''
        <script>
            alert("您没有注册权限，即将返回主页..");
            window.location.href = "/";
        </script>
        '''
    
    # 查询person_info表，查看该用户名是否已经注册过
    username = request.form.get('username')
    cursor.execute('''
        SELECT id
        FROM person_info
        WHERE username = ?
    ''', (username,))
    value = cursor.fetchall()
    # 若注册过，返回到signup重新选择用户名
    if len(value) > 0:
        return '''
        <script>
            alert("该用户名已经注册过，请您更换用户名");
            window.location.href = "/signup";
        </script>
        '''

    # 若允许注册/用户名没注册过，则准许注册，将账号数据插入数据库中
    password = request.form.get('password')
    cursor.execute('''
        INSERT INTO person_info(username, password_hash)
        VALUES(?,?)
    ''', (username, generate_password_hash(password)))
    cursor.execute('''
        UPDATE allowed_signup
        SET has_signup = 1
        WHERE studentid = ?
    ''', (studentid,))

    conn.commit()
    conn.close()

    return '''
    <script>
        alert("注册成功！这是你的奖励（指返回登陆界面）");
        window.location.href = "/signin";
    </script>
    '''
    

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
