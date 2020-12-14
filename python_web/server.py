from flask import Flask, request, render_template, session, redirect
import sqlite3
from datetime import timedelta
from model import User
from flask_login import login_user, login_required
from flask_login import LoginManager, current_user
from flask_login import logout_user
import os
from werkzeug.security import generate_password_hash
import re

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

@app.route('/issue_center', methods=['GET'])
@login_required
def get_issue_from_center():
    # 处理url，重定向至正确的最简url
    current_url = str(request.full_path)
    indexes = current_url.partition('?')[2]
    if indexes == '':
        index_list = []
    else:
        index_list = indexes.split('&')
    new_index_list = []
    for i in index_list:
        if i.find('=') == -1 or i.endswith('=') or i.count('=') > 1:
            continue
        new_index_list.append(i)
    if len(index_list) == 0 or len(index_list) == len(new_index_list):
        pass
    elif len(new_index_list) == 0:
        return redirect('/issue_center')
    else:
        return redirect('/issue_center?' + '&'.join(new_index_list))

    # 参数转换，将GET得到的参数转化为SQL查询的参数
    args_dict = {}
    args_trans = {
        'issue_id': 'id',
        'host': 'host_id',
        'date': 'start_date',
        'is_finished': 'is_finished',
        'cert': 'cert_id'
    }

    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    for arg in args_trans.keys():
        if request.args.get(arg) is not None:
            if arg == 'is_finished':
                if request.args.get(arg) == 'true':
                    args_dict['is_finished'] = '1'
                    continue
                else:
                    args_dict['is_finished'] = '0'
                    continue
            elif arg == 'issue_id':
                if str(request.args.get(arg)).isdigit():
                    args_dict[args_trans[arg]] = int(request.args.get(arg))
                else:
                    return redirect('/issue_center')
                continue
            elif arg == 'host' or arg == 'cert':
                cursor.execute('''
                    SELECT id
                    FROM person_info
                    WHERE username = ?
                ''', (request.args.get(arg),))
                value = cursor.fetchall()
                if len(value) == 0:
                    return redirect('/issue_center')
                args_dict[args_trans[arg]] = value[0][0]
                continue
            args_dict[args_trans[arg]] = request.args.get(arg)
    if request.args.get('my_issue') is not None:
        args_dict['host_id'] = current_user.id
    if request.args.get('my_cert') is not None:
        args_dict['cert_id'] = current_user.id

    # 构建SQL查询语句
    sql_query = 'SELECT * FROM issue '
    args_list = []
    if len(args_dict) > 0:
        sql_query += 'WHERE '
        query_list = []
        for key in args_dict.keys():
            query_list.append(key + ' = ?')
            args_list.append(args_dict[key])
        sql_query += ' AND '.join(query_list)
    sql_query += ' ORDER BY id DESC'

    # 查询部分
    if len(args_dict) > 0:
        cursor.execute(sql_query, args_list)
        value = cursor.fetchall()
    else:
        cursor.execute(sql_query)
        value = cursor.fetchall()

    # 页面显示设置&翻页参数设置
    all_page_num = 0
    if len(value) % 10 != 0:
        all_page_num = len(value) // 10 + 1
    else:
        all_page_num = len(value) / 10

    page_num = 1
    recv_page_num = request.args.get('page')
    if recv_page_num is not None:
        if str(recv_page_num).isdigit():
            page_num = int(recv_page_num)
            if page_num < 1 or page_num > all_page_num:
                return redirect('/issue_center')
        else:
            return redirect('/issue_center')
    page_item = value[(page_num - 1) * 10 : page_num * 10]

    # 数据转换：将id转换为用户名，将1/0转换为是/否
    for i in range(len(page_item)):
        tmp = list(page_item[i])
        cursor.execute('''
            SELECT username
            FROM person_info
            WHERE id = ?
        ''', (tmp[1],))
        value = cursor.fetchone()
        if value is None:
            tmp[1] = 'None'
        else:
            tmp[1] = value[0]
        if tmp[5] == 0:
            tmp[5] = '未认证'
        else:
            cursor.execute('''
                SELECT username
                FROM person_info
                WHERE id = ?
            ''', (tmp[5],))
            value = cursor.fetchone()
            if value is None:
                tmp[1] = 'None'
            else:
                tmp[1] = value[0]
            tmp[5] = value
        if tmp[4] == '0':
            tmp[4] = '是'
        else:
            tmp[4] = '否'
        page_item[i] = tmp
    
    conn.commit()
    conn.close()

    # 翻页保持url相对不变
    result = re.search(r'page=[0-9]+', current_url)
    if result != None:
        first_page_url = re.sub(r'page=[0-9]+', 'page={}'.format(1), current_url)
        end_page_url = re.sub(r'page=[0-9]+', 'page={}'.format(all_page_num), current_url)
        prev_page_url = current_url
        if page_num > 1:
            prev_page_url = re.sub(r'page=[0-9]+', 'page={}'.format(page_num-1), current_url)
        next_page_url = current_url
        if page_num < all_page_num:
            next_page_url = re.sub(r'page=[0-9]+', 'page={}'.format(page_num+1), current_url)
    else: # 现在已经在第一页中
        if len(index_list) == 0:
            first_page_url = current_url.replace('?','') + '?page=1'
            end_page_url = current_url.replace('?','') + '?page={}'.format(all_page_num)
            prev_page_url = first_page_url
            next_page_url = current_url.replace('?','') + '?page=2'
        else:
            first_page_url = current_url + '&page=1'
            end_page_url = current_url + '&page={}'.format(all_page_num)
            prev_page_url = first_page_url
            next_page_url = current_url + '&page=2'

    page_info = {
        'first_page_url': first_page_url,
        'prev_page_url': prev_page_url,
        'next_page_url': next_page_url,
        'end_page_url': end_page_url,
        'cur_page_num': page_num,
        'max_page_num': all_page_num
    }

    return render_template('issue_center.html', issues=page_item, page_info=page_info)

@app.route('/issue_center/<int:issue_id>', methods=['GET'])
@login_required
def get_issue_detail(issue_id):
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(id) FROM issue")
    max_id = cursor.fetchone()[0]

    # 判断url中的id是否在合法范围内，不合法则返回事务中心
    if issue_id < 1 or issue_id > max_id:
        return redirect('/issue_center')

    cursor.execute("SELECT * FROM issue WHERE id = ?", (issue_id,))
    value = cursor.fetchone()
    if value is None:
        return redirect('/issue_center')
    
    value_list = list(value)
    cursor.execute('''
        SELECT username
        FROM person_info
        WHERE id = ?
    ''', (value_list[1],))
    value = cursor.fetchone()
    if value is None:
        value_list[1] = 'None'
    else:
        value_list[1] = value[0]
    if value_list[5] == 0:
        value_list[5] = '未认证'
    else:
        cursor.execute('''
            SELECT username
            FROM person_info
            WHERE id = ?
       ''', (value_list[5],))
        value = cursor.fetchone()
        if value is None:
            value_list[1] = 'None'
        else:
            value_list[1] = value[0]
        value_list[5] = value
    if value_list[4] == '0':
        value_list[4] = '是'
    else:
        value_list[4] = '否'

    conn.commit()
    conn.close()

    issue_dict = {
        'id': value_list[0],
        'hostname': value_list[1],
        'date': value_list[2],
        'description': value_list[3],
        'is_finished': value_list[4],
        'certname': value_list[5]
    }
    return render_template('issue_detail.html', issue=issue_dict)

if __name__ == '__main__':
    app.run(debug=True)
