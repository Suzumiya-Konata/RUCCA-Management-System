from flask import Flask, request, render_template, session, redirect
import sqlite3
from datetime import timedelta
from model import User
from module import static_url
from flask_login import login_user, login_required
from flask_login import LoginManager, current_user
from flask_login import logout_user
import os
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
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
    conn.commit()
    conn.close()
    return render_template("index.html", user=user_dict, is_admin=current_user.is_admin)

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
                WHERE id = ?
                ''',(request.form['username'],generate_password_hash(request.form['password']),request.form['phone'],request.form['description'],current_user.id,)
            )
        else:
            cursor.execute(
                '''
                UPDATE person_info
                SET
                    password_hash = ? ,
                    phone = ? ,
                    description = ?
                WHERE id = ?
                ''',(generate_password_hash(request.form['password']),request.form['phone'],request.form['description'],current_user.id,)
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
                WHERE id = ?
                ''',(request.form['username'],request.form['phone'],request.form['description'],current_user.id,)
            )
        else:
            cursor.execute(
            '''
            UPDATE person_info
            SET
                phone = ? ,
                description = ?
            WHERE id = ?
            ''',(request.form['phone'],request.form['description'],current_user.id,)
        )
    conn.commit()
    conn.close()

    #修改成功页面
    if(flag1 or flag2):
        logout_user()
        return redirect('/signin')
    else:
        return redirect('/info_detail')

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
        'is_finished': 'is_finished'
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
            elif arg == 'host':
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
        if tmp[4] == '0':
            tmp[4] = '否'
        else:
            tmp[4] = '是'
        page_item[i] = tmp
    
    conn.commit()
    conn.close()

    # 翻页保持url相对不变
    page_info = static_url(current_url, page_num, all_page_num, len(index_list))

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

    host_id = int(value[1])
    
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
    if value_list[4] == '1':
        value_list[4] = '是'
    else:
        value_list[4] = '否'

    conn.commit()
    conn.close()

    is_display_modify = 0
    if host_id == current_user.id:
        is_display_modify = 1

    issue_dict = {
        'id': value_list[0],
        'hostname': value_list[1],
        'date': value_list[2],
        'description': value_list[3],
        'is_finished': value_list[4]
    }
    return render_template('issue_detail.html', issue=issue_dict, is_display=is_display_modify)

@app.route('/issue_center/<int:issue_id>', methods=['POST'])
@login_required
def delete_issue(issue_id):
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(id) FROM issue")
    max_id = cursor.fetchone()[0]

    # 判断url中的id是否在合法，不合法则返回事务中心
    if issue_id < 1 or issue_id > max_id:
        return redirect('/issue_center')

    cursor.execute("SELECT * FROM issue WHERE id = ?", (issue_id,))
    value = cursor.fetchone()
    if value is None:
        return redirect('/issue_center')

    # 判断是否是host，只有是host才继续进行删除，否则跳回issue_center
    host_id = int(value[1])
    if host_id != current_user.id:
        return redirect('/issue_center')

    cursor.execute('''
        DELETE FROM issue
        WHERE id = ?
    ''', (issue_id,))

    conn.commit()
    conn.close()

    return redirect('/issue_center')

@app.route('/issue_center/modify/<int:issue_id>', methods=['GET'])
@login_required
def modify_issue_detail(issue_id):
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
    
    # TO 林润：
    # 这里没必要再查询一次了
    # 如果上面那个value是None的话已经返回了，那么此时的value中已经包含了当前issue的所有信息
    # 如果身份为host允许修改
    if(int(value[1]) != current_user.id):
        return redirect('/issue_center')
    # 如果身份不为host(可能需要添加对管理员允许),强制返回事务中心


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
        'is_finished': value_list[4]
    }
    return render_template('issue_modify_host.html', issue=issue_dict)
    
@app.route('/issue_center/modify/<int:issue_id>', methods=['POST'])
@login_required
def modify_detail(issue_id):
    conn = sqlite3.connect("../../RUCCA.db")
    cursor = conn.cursor()
    if(request.form['is_finished']=='true'):
        is_finished = 1
    else:
        is_finished = 0
    print(is_finished,request.form['is_finished'])
    cursor.execute(
        '''
        UPDATE issue
        SET
            description = ? ,
            is_finished = ?
        WHERE id = ?
        ''',(request.form['description'],is_finished,issue_id,)
    )
    conn.commit()
    conn.close()
    return redirect('/issue_center/'+str(issue_id))

@app.route('/issue_center/create', methods=['GET'])
@login_required
def descrip_issue():
    #创建事务
    #生成除了描述外的其他值
    
    conn = sqlite3.connect("../../RUCCA.db")
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT username
        FROM person_info
        WHERE id = ?
        ''',(current_user.id,)
    )
    value = cursor.fetchone()
    conn.commit()
    conn.close()

    import time
    localtime = time.localtime(time.time())
    date = '{}-{}-{}'.format(localtime.tm_year,localtime.tm_mon,localtime.tm_mday,)
    issue_dict = {
        'host':value[0],
        'date':date
    }
    return render_template('issue_create.html', issue=issue_dict)

@app.route('/issue_center/create', methods=['POST'])
@login_required
def create_issue():
    #基本架构完成
    #可能需要身份核准
    description = request.form['description']
    import time
    localtime = time.localtime(time.time())
    date = '{}-{}-{}'.format(localtime.tm_year,localtime.tm_mon,localtime.tm_mday,)
    conn = sqlite3.connect("../../RUCCA.db")
    cursor = conn.cursor()
    issue_dict = {
        'date':date,
        'description':description,
        'is_finished':0
    }
    cursor.execute(
        '''
        INSERT INTO issue(host_id,start_date,description,is_finished)
        VALUES(?,?,?,?)
        ''',
        (current_user.id,
        issue_dict['date'],
        issue_dict['description'],
        issue_dict['is_finished'])
    )
    cursor.execute('''
        SELECT count(id)
        FROM issue
    ''')
    values = cursor.fetchone()
    conn.commit()
    conn.close()
    return redirect('/issue_center/'+str(values[0]))


@app.route('/maintenance_center', methods=['GET'])
@login_required
def get_main_data_from_center():
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
        return redirect('/maintenance_center')
    else:
        return redirect('/maintenance_center?' + '&'.join(new_index_list))

    # 参数转换，将GET得到的参数转化为SQL查询的参数
    args_dict = {}
    args_trans = {
        'data_id': 'id',
        'host': 'host_id',
        'model': 'model',
        'date': 'added_date'
    }

    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    for arg in args_trans.keys():
        if request.args.get(arg) is not None:
            if arg == 'data_id':
                if str(request.args.get(arg)).isdigit():
                    args_dict[args_trans[arg]] = int(request.args.get(arg))
                else:
                    return redirect('/maintenance_center')
                continue
            elif arg == 'host':
                cursor.execute('''
                    SELECT id
                    FROM person_info
                    WHERE username = ?
                ''', (request.args.get(arg),))
                value = cursor.fetchall()
                if len(value) == 0:
                    return redirect('/maintenance_center')
                args_dict[args_trans[arg]] = value[0][0]
                continue
            args_dict[args_trans[arg]] = request.args.get(arg)
    if request.args.get('my_data') is not None:
        args_dict['host_id'] = current_user.id
    
    # 构建SQL查询语句
    sql_query = '''SELECT id,host_id,added_date,model
     FROM maintenance_data '''
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
                return redirect('/maintenance_center')
        else:
            return redirect('/maintenance_center')
    page_item = value[(page_num - 1) * 10 : page_num * 10]

    # 数据转换：将id转换为用户名
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
        page_item[i] = tmp
    
    conn.commit()
    conn.close()

    # 翻页保持url相对不变
    page_info = static_url(current_url, page_num, all_page_num, len(index_list))

    return render_template('maintenance_center.html', datas=page_item, page_info=page_info)

@app.route('/maintenance_center/<int:data_id>', methods=['GET'])
@login_required
def get_data_detail(data_id):
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(id) FROM maintenance_data")
    max_id = cursor.fetchone()[0]

    # 判断url中的id是否在合法范围内，不合法则返回maintenance_center
    if data_id < 1 or data_id > max_id:
        return redirect('/maintenance_center')

    cursor.execute("SELECT * FROM maintenance_data WHERE id = ?", (data_id,))
    value = cursor.fetchone()
    if value is None:
        return redirect('/maintenance_center')

    host_id = int(value[1])
    
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

    conn.commit()
    conn.close()

    is_display_modify = 0
    if host_id == current_user.id:
        is_display_modify = 1

    data_dict = {
        'id': value_list[0],
        'hostname': value_list[1],
        'date': value_list[2],
        'model': value_list[3],
        'description': value_list[4]
    }
    return render_template('maintenance_detail.html', data=data_dict, is_display=is_display_modify)

@app.route('/maintenance_center/<int:data_id>', methods=['POST'])
@login_required
def delete_maintenance_data(data_id):
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(id) FROM maintenance_data")
    max_id = cursor.fetchone()[0]

    # 判断url中的id是否在合法，不合法则返回maintenance_center
    if data_id < 1 or data_id > max_id:
        return redirect('/maintenance_center')

    cursor.execute("SELECT * FROM maintenance_data WHERE id = ?", (data_id,))
    value = cursor.fetchone()
    if value is None:
        return redirect('/maintenance_center')

    # 判断是否是host，只有是host才继续进行删除，否则跳回maintenance_center
    host_id = int(value[1])
    if host_id != current_user.id:
        return redirect('/maintenance_center')

    cursor.execute('''
        DELETE FROM maintenance_data
        WHERE id = ?
    ''', (data_id,))

    conn.commit()
    conn.close()

    return redirect('/maintenance_center')

@app.route('/maintenance_center/modify/<int:data_id>', methods=['GET'])
@login_required
def edit_maintenence(data_id):
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(id) FROM maintenance_data")
    max_id = cursor.fetchone()[0]

    # 判断url中的id是否在合法，不合法则返回maintenance_center
    if data_id < 1 or data_id > max_id:
        return redirect('/maintenance_center')

    cursor.execute("SELECT * FROM maintenance_data WHERE id = ?", (data_id,))
    value = cursor.fetchone()
    if value is None:
        return redirect('/maintenance_center')

    # 判断是否是host，只有是host才继续进行编辑，否则跳回maintenance_center

    host_id = int(value[1])
    
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

    conn.commit()
    conn.close()

    is_display_modify = 0
    if host_id == current_user.id:
        is_display_modify = 1

    data_dict = {
        'id': value_list[0],
        'hostname': value_list[1],
        'date': value_list[2],
        'model': value_list[3],
        'description': value_list[4]
    }
    return render_template('maintenance_modify.html', data=data_dict, is_display=is_display_modify)

@app.route('/maintenance_center/modify/<int:data_id>', methods=['POST'])
@login_required
def modify_maintenence(data_id):
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(id) FROM maintenance_data")
    max_id = cursor.fetchone()[0]

    # 判断url中的id是否在合法，不合法则返回maintenance_center
    if data_id < 1 or data_id > max_id:
        return redirect('/maintenance_center')

    cursor.execute("SELECT * FROM maintenance_data WHERE id = ?", (data_id,))
    value = cursor.fetchone()
    if value is None:
        return redirect('/maintenance_center')

    # 判断是否是host，只有是host才继续进行编辑，否则跳回maintenance_center
    cursor.execute(
        '''
        UPDATE maintenance_data
        SET
            model = ? ,
            description = ?
        WHERE id = ?
        ''',(request.form['model'],request.form['description'],data_id,)
    )
    conn.commit()
    conn.close()
    return redirect('/maintenance_center/'+str(data_id))

@app.route('/maintenance_center/create', methods=['GET'])
@login_required
def describ_maintenance():
    #创建资料
    #生成除了描述外的其他值
    
    conn = sqlite3.connect("../../RUCCA.db")
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT username
        FROM person_info
        WHERE id = ?
        ''',(current_user.id,)
    )
    value = cursor.fetchone()
    conn.commit()
    conn.close()

    import time
    localtime = time.localtime(time.time())
    date = '{}-{}-{}'.format(localtime.tm_year,localtime.tm_mon,localtime.tm_mday,)
    maintenance_dict = {
        'host':value[0],
        'date':date
    }
    return render_template('maintenance_create.html', maintenance=maintenance_dict)

@app.route('/maintenance_center/create', methods=['POST'])
@login_required
def create_maintenance():
    conn = sqlite3.connect("../../RUCCA.db")
    cursor = conn.cursor()

    import time
    localtime = time.localtime(time.time())
    date = '{}-{}-{}'.format(localtime.tm_year,localtime.tm_mon,localtime.tm_mday,)
    cursor.execute('''
        INSERT INTO maintenance_data(host_id, added_date, model, description)
        VALUES(?, ?, ?, ?)
    ''', 
    (current_user.id, 
    date, 
    request.form['model'],
    request.form['description']
    ))
    conn.commit()
    conn.close()
    return redirect('/maintenance_center')

@app.route('/activity_center', methods=['GET'])
@login_required
def get_activity_from_center():
    # 处理url，重定向至正确的最简url
    current_url = str(request.full_path)
    indexes = current_url.partition('?')[2]
    if indexes == '':
        index_list = []
    else:
        index_list = indexes.split('&')
    new_index_list = []
    #print(new_index_list)
    for i in index_list:
        if i.find('=') == -1 or i.endswith('=') or i.count('=') > 1:
            continue
        new_index_list.append(i)
    if len(index_list) == 0 or len(index_list) == len(new_index_list):
        pass
    elif len(new_index_list) == 0:
        return redirect('/activity_center')
    else:
        return redirect('/activity_center?' + '&'.join(new_index_list))

    # 参数转换，将GET得到的参数转化为SQL查询的参数
    args_dict = {}
    args_trans = ['id', 'host_id', 'date', 'name']

    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    for arg in args_trans:
        if request.args.get(arg) is not None:
            if arg == 'id':
                if str(request.args.get(arg)).isdigit():
                    args_dict[arg] = int(request.args.get(arg))
                else:
                    return redirect('/activity_center')
            elif arg == 'host_id':
                cursor.execute('''
                    SELECT id
                    FROM person_info
                    WHERE username = ?
                ''', (request.args.get(arg),))
                value = cursor.fetchall()
                if len(value) == 0:
                    return redirect('/activity_center')
                args_dict[arg] = value[0][0]
            else:
                args_dict[arg] = request.args.get(arg)
    if request.args.get('my_create') is not None:
        args_dict['host_id'] = current_user.id
    
    # 构建SQL查询语句
    if request.args.get('my_participate') is not None:
        sql_query = '''
            SELECT activity.id, activity.name, activity.date, activity.location, activity.description, activity.host_id
            FROM activity, activity_participate
            WHERE activity.id = activity_participate.activity_id AND activity_participate.person_id = ? 
        '''
        args_list = [current_user.id]
        if len(args_dict) > 0:
            sql_query += 'AND '
            query_list = []
            for key in args_dict.keys():
                query_list.append("activity." + key + ' = ?')
                args_list.append(args_dict[key])
            sql_query += ' AND '.join(query_list)
        sql_query += ' ORDER BY id DESC'
    else:
        sql_query = '''SELECT id, name, date, location, description, host_id
        FROM activity '''
        args_list = []
        if len(args_dict) > 0:
            sql_query += 'WHERE '
            query_list = []
            for key in args_dict.keys():
                query_list.append(key + ' = ?')
                args_list.append(args_dict[key])
            sql_query += ' AND '.join(query_list)
        sql_query += ' ORDER BY id DESC'
    
    #print(sql_query)
    # 查询部分
    if len(args_list) > 0:
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
                return redirect('/activity_center')
        else:
            return redirect('/activity_center')
    page_item = value[(page_num - 1) * 10 : page_num * 10]

    # 数据转换：将id转换为用户名
    for i in range(len(page_item)):
        tmp = list(page_item[i])
        cursor.execute('''
            SELECT username
            FROM person_info
            WHERE id = ?
        ''', (tmp[5],))
        value = cursor.fetchone()
        if value is None:
            tmp[5] = 'None'
        else:
            tmp[5] = value[0]
        page_item[i] = tmp
    
    conn.commit()
    conn.close()

    # 翻页保持url相对不变
    page_info = static_url(current_url, page_num, all_page_num, len(index_list))

    return render_template('activity_center.html', datas=page_item, page_info=page_info)

@app.route('/activity_center/<int:act_id>', methods=['GET'])
@login_required
def activity_detail(act_id):
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT *
        FROM activity
        WHERE id = ?
        ''',(act_id,)
    )
    values = cursor.fetchone()
    host_id = values[5]
    cursor.execute(
        '''
        SELECT username
        FROM person_info
        WHERE id = ?
        ''',(host_id,)
    )
    act_detail = {
        'id':values[0],
        'name':values[1],
        'date':values[2],
        'location':values[3],
        'description':values[4],
        'hostname':host_id
    }
    #print(act_detail)

    cursor.execute(
        '''
        SELECT *
        FROM activity_participate
        WHERE person_id = ? AND activity_id = ?
        ''',(current_user.id,act_id,)
    )
    is_participate = cursor.fetchone()
    conn.commit()
    conn.close()

    if host_id==current_user.id:
        is_display_modify = 1
    else:
        is_display_modify = 0
    
    if (not is_participate):
        status = 0
    else:
        status = 1
    return render_template('activity_detail.html', act=act_detail, is_display=is_display_modify,is_participate=status)

@app.route('/activity_center/<int:act_id>', methods=['POST'])
@login_required
def delete_activity(act_id):
    if(request.form['action_type']=='drop'):
        conn = sqlite3.connect('../../RUCCA.db')
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT host_id
            FROM activity
            WHERE id = ?
            ''',(act_id,)
        )
        host_id = cursor.fetchone()
        if(host_id[0]!=current_user.id):
            conn.commit()
            conn.close()
        else:
            cursor.execute(
                '''
                DELETE FROM activity
                WHERE id = ?
                ''',(act_id,)
            )
            cursor.execute(
                '''
                DELETE FROM activity_participate
                WHERE activity_id = ?
                ''',(act_id,)
            )
            conn.commit()
            conn.close()
        return redirect('/activity_center')
    elif(request.form['action_type']=='part'):
        conn = sqlite3.connect('../../RUCCA.db')
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO activity_participate VALUES(?, ?, 'Soudayo!')
            ''',(act_id,current_user.id,)
        )
        conn.commit()
        conn.close()
        
        return redirect('/activity_center/'+str(act_id))
    elif(request.form['action_type']=='quit'):
        conn = sqlite3.connect('../../RUCCA.db')
        cursor = conn.cursor()
        cursor.execute(
            '''
            DELETE FROM activity_participate 
            WHERE activity_id = ? AND person_id = ?
            ''',(act_id,current_user.id,)
        )
        conn.commit()
        conn.close()
        return redirect('/activity_center/'+str(act_id))

@app.route('/activity_center/create',methods=['GET'])
@login_required
def edit_new_activity():
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT username
        FROM person_info
        WHERE id = ?
        ''',(current_user.id,)
    )
    values = cursor.fetchone()
    conn.commit()
    conn.close()
    act_dict={
        'host':values[0]
    }
    return render_template('activity_create.html',act=act_dict)

@app.route('/activity_center/create',methods=['POST'])
@login_required
def create_new_activity():
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO activity(name, date, location, description, host_id)
        VALUES(?, ?, ?, ?, ?)
        ''',
        (
            request.form['name'],
            request.form['date'],
            request.form['location'],
            request.form['description'],
            current_user.id
        )
    )
    conn.commit()
    conn.close()
    return redirect('/activity_center')

@app.route('/reply', methods=['GET'])
def get_activity_from_out():
    # 处理url，重定向至正确的最简url
    current_url = str(request.full_path)
    indexes = current_url.partition('?')[2]
    if indexes == '':
        index_list = []
    else:
        index_list = indexes.split('&')
    new_index_list = []
    #print(new_index_list)
    for i in index_list:
        if i.find('=') == -1 or i.endswith('=') or i.count('=') > 1:
            continue
        new_index_list.append(i)
    if len(index_list) == 0 or len(index_list) == len(new_index_list):
        pass
    elif len(new_index_list) == 0:
        return redirect('/reply')
    else:
        return redirect('/reply?' + '&'.join(new_index_list))

    # 参数转换，将GET得到的参数转化为SQL查询的参数
    args_dict = {}
    args_trans = ['id', 'host_id', 'date', 'name']

    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    for arg in args_trans:
        if request.args.get(arg) is not None:
            if arg == 'id':
                if str(request.args.get(arg)).isdigit():
                    args_dict[arg] = int(request.args.get(arg))
                else:
                    return redirect('/activity_center')
            elif arg == 'host_id':
                cursor.execute('''
                    SELECT id
                    FROM person_info
                    WHERE username = ?
                ''', (request.args.get(arg),))
                value = cursor.fetchall()
                if len(value) == 0:
                    return redirect('/activity_center')
                args_dict[arg] = value[0][0]
            else:
                args_dict[arg] = request.args.get(arg)\
    
    sql_query = '''SELECT id, name, date, location, description, host_id
        FROM activity '''
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
    if len(args_list) > 0:
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
                return redirect('/reply')
        else:
            return redirect('/reply')
    page_item = value[(page_num - 1) * 10 : page_num * 10]

    # 数据转换：将id转换为用户名
    for i in range(len(page_item)):
        tmp = list(page_item[i])
        cursor.execute('''
            SELECT username
            FROM person_info
            WHERE id = ?
        ''', (tmp[5],))
        value = cursor.fetchone()
        if value is None:
            tmp[5] = 'None'
        else:
            tmp[5] = value[0]
        page_item[i] = tmp
    
    conn.commit()
    conn.close()

    # 翻页保持url相对不变
    page_info = static_url(current_url, page_num, all_page_num, len(index_list))
    return render_template('reply_list.html', datas=page_item, page_info=page_info)

@app.route('/reply/<int:reply_id>', methods=['GET'])
def get_reply_form(reply_id):
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM activity WHERE id = ?", (reply_id,))
    value = cursor.fetchall()

    if len(value) == 0:
        return '<script>alert("Invalid url!");window.location.href = "/reply"</script>'

    return render_template('reply_form.html',reply_id=reply_id)

@app.route('/reply/<int:reply_id>', methods=['POST'])
def post_reply_form(reply_id):
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM activity WHERE id = ?", (reply_id,))
    value = cursor.fetchall()

    if len(value) == 0:
        return '<script>alert("Invalid url!");window.location.href = "/reply"</script>'

    cursor.execute(
        '''
        INSERT INTO reply(activity_id, submitter, contact, content, suggestion)
        VALUES(?, ?, ?, ?, ?)
        ''',
        (
            reply_id,
            request.form['submitter'],
            request.form['contact'],
            request.form['content'],
            request.form['suggestion']
        )
    )
    conn.commit()
    conn.close()
    return redirect('/reply')

if __name__ == '__main__':
    app.run(debug=True)
