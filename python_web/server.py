from flask import Flask, request, render_template, session, redirect
import sqlite3
from datetime import timedelta
from model import User
from flask_login import login_user, login_required
from flask_login import LoginManager, current_user
from flask_login import logout_user
import os
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

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
    conn.commit()
    conn.close()
    return render_template("index.html", user=user_dict)

@app.route('/info_detail', methods=['GET'])
@login_required
def get_info_detail():
    conn = sqlite3.connect("../../RUCCA.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT *
        FROM person_info
        WHERE id = ?
    ''', (current_user.id,))
    value = cursor.fetchone()
    user_dict = {
        'username': value[1],
        'password_hash': value[2],
        'name': value[3],
        'id_card_number': value[4],
        'sex': value[5],
        'phone': value[6],
        'department': value[7],
        'job': value[8],
        'description': value[9]
    }
    conn.commit()
    conn.close()
    return render_template("info_detail.html", user=user_dict)

@app.route('/info_modify', methods=['GET'])
@login_required
def modify_info_detail():
    conn = sqlite3.connect("../../RUCCA.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT *
        FROM person_info
        WHERE id = ?
    ''', (current_user.id,))
    value = cursor.fetchone()
    user_dict = {
        'username': value[1],
        'password_hash': value[2],
        'name': value[3],
        'id_card_number': value[4],
        'sex': value[5],
        'phone': value[6],
        'department': value[7],
        'job': value[8],
        'description': value[9]
    }
    conn.commit()
    conn.close()
    return render_template("info_modify.html", user=user_dict)

@app.route('/info_modify', methods=['POST'])
@login_required
def modifying_info_detail():
    conn = sqlite3.connect("../../RUCCA.db")
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT *
        FROM person_info
        WHERE id = ?
        ''',(current_user.id,)
    )
    value = cursor.fetchone()
    user_dict = {
        'username': value[1],
        'password_hash': value[2],
        'name': value[3],
        'id_card_number': value[4],
        'sex': value[5],
        'phone': value[6],
        'department': value[7],
        'job': value[8],
        'description': value[9]
    }
    #验证密码
    passwd = request.form['before_passwd']
    user = User(user_dict['username'])
    if(user.verify_password(passwd)):
        pass
    else:
        #验证失败页面
        conn.commit()
        conn.close()
        return '<h3>Bad username or password.</h3>'
    #查看是否修改用户名和密码
    flag1 = flag2 = 0
    if(request.form['username']!=user_dict['username']):
        flag1 = 1
    if(request.form['password']!=""):
        flag2 = 1
    #数据库内容修改
    if(flag2):
        if(flag1):
            cursor.execute(
                '''
                UPDATE person_info
                SET
                    username = ? ,
                    password_hash = ? ,
                    phone = ? ,
                    description = ?
                ''',(request.form['username'],generate_password_hash(request.form['password']),request.form['phone'],request.form['description'],)
            )
        else:
            cursor.execute(
                '''
                UPDATE person_info
                SET
                    password_hash = ? ,
                    phone = ? ,
                    description = ?
                ''',(generate_password_hash(request.form['password']),request.form['phone'],request.form['description'],)
            )
    else:
        if(flag1):
            cursor.execute(
                '''
                UPDATE person_info
                SET
                    username = ? ,
                    phone = ? ,
                    description = ?
                ''',(request.form['username'],request.form['phone'],request.form['description'],)
            )
        else:
            cursor.execute(
            '''
            UPDATE person_info
            SET
                phone = ? ,
                description = ?
            ''',(request.form['phone'],request.form['description'],)
        )
    conn.commit()
    conn.close()

    #修改成功页面
    if(flag1 or flag2):
        logout_user()
        return redirect('/signin')
    else:
        return redirect('/info_detail')
    return '''<h1>to do by lr</h1>'''

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
