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

lev_dict = {'部员':1,'副部长':2,'部长':3,'副会长':4,'会长':5}

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
        if remember_me is not None:
            time = timedelta(weeks=1)
            login_user(user, remember=True, duration=time)
        else:
            login_user(user)
        return redirect('/index')
    else:
        return '<script>alert("用户名或密码错误");window.location.href = "/signin"</script>'

@app.route('/intro', methods=['GET', 'POST'])
def intro():
    return render_template('intro.html')

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
    return render_template("index.html", user=user_dict, is_admin=current_user.check_admin())

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
        'id': value[0],
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
    return render_template("info_detail.html", user=user_dict, identification=1, way=1)

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
        'id': value[0],
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
    return render_template("info_modify.html", user=user_dict, way=1)

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
    try:
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
    except:
        return '<script>alert("您输入的数据不合法，请您重新输入！");window.location.href="/info_modify"</script>'
    conn.commit()
    conn.close()

    #修改成功页面
    if(flag1 or flag2):
        logout_user()
        return redirect('/signin')
    else:
        return redirect('/info_detail')

@app.route('/member_list', methods=['GET'])
@login_required
def get_member_list():
    if current_user.check_admin() == False:
        redirect('/index')
    
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
        return redirect('/member_list')
    else:
        return redirect('/member_list?' + '&'.join(new_index_list))

    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    cursor.execute("pragma table_info(person_info)")
    value = cursor.fetchall()
    args_list = []
    for i in value:
        if i[1] == 'password_hash':
            continue
        args_list.append(i[1])

    args_dict = {}
    for key in args_list:
        if request.args.get(key) is not None:
            args_dict[key] = request.args.get(key)
    
    # 构建SQL查询语句
    sql_query = 'SELECT {} FROM person_info '.format(','.join(args_list))
    args_l = []
    if len(args_dict) > 0:
        sql_query += 'WHERE '
        query_list = []
        for key in args_dict.keys():
            query_list.append(key + ' = ?')
            args_l.append(args_dict[key])
        sql_query += ' AND '.join(query_list)
    sql_query += ' ORDER BY id ASC'

    # 查询部分
    if len(args_dict) > 0:
        cursor.execute(sql_query, args_l)
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
                return redirect('/member_list')
        else:
            return redirect('/member_list')
    page_item = value[(page_num - 1) * 10 : page_num * 10]

    conn.commit()
    conn.close()

    # 翻页保持url相对不变
    page_info = static_url(current_url, page_num, all_page_num, len(index_list))

    return render_template('member_list.html', input=args_list, issues=page_item, page_info=page_info, is_memberls=True)

@app.route('/member_list/<int:person_id>', methods=['GET'])
@login_required
def get_member_detail(person_id):
    if current_user.check_admin() == False:
        return redirect('/index')
    
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM person_info WHERE id = ?',(person_id,))
    values = cursor.fetchone()
    print(type(values))
    if(type(values) == type(None)):
        conn.commit()
        conn.close()
        return '<script>alert("Invalid url!");window.location.href = "/member_list"</script>'

    cursor.execute("SELECT * FROM person_info WHERE id = ?", (person_id,))
    value = cursor.fetchall()

    if len(value) == 0:
        conn.commit()
        conn.close()
        return redirect('/member_list')
    
    cursor.execute('''
        SELECT *
        FROM person_info
        WHERE id = ?
    ''', (person_id,))
    value = cursor.fetchone()
    user_dict = {
        'id': value[0],
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
    job = cursor.execute(
        '''
        SELECT job
        FROM person_info
        WHERE id = ?
        ''',(current_user.id,)
    ).fetchone()[0]
    identify = 0
    if lev_dict[job] == 5:
        identify = 2
    conn.commit()
    conn.close()
    return render_template("info_detail.html", user=user_dict, identification=identify, way=2)

@app.route('/member_list/modify/<int:person_id>', methods=['GET'])
@login_required
def edit_member_detail(person_id):
    if current_user.check_admin() == False:
        return redirect('/index')
    if current_user.check_minister() == False:
        return redirect('/member_list')
    conn = sqlite3.connect("../../RUCCA.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM person_info WHERE id = ?',(person_id,))
    values = cursor.fetchone()
    print(type(values))
    if(type(values) == type(None)):
        conn.commit()
        conn.close()
        return '<script>alert("Invalid url!");window.location.href = "/member_list"</script>'
    cursor.execute('''
        SELECT *
        FROM person_info
        WHERE id = ?
    ''', (person_id,))
    value = cursor.fetchone()
    user_dict = {
        'id': value[0],
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
    user = User(user_dict['username'])
    modify = 1
    if user.check_minister():
        modify = 0
    conn.commit()
    conn.close()
    return render_template("info_modify.html", user=user_dict, way=2, can_be_modify=modify)

@app.route('/member_list/modify/<int:person_id>', methods=['POST'])
@login_required
def modify_member_detail(person_id):
    if current_user.check_admin() == False:
        return redirect('/index')
    if current_user.check_minister() == False:
        return redirect('/member_list')
    conn = sqlite3.connect("../../RUCCA.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM person_info WHERE id = ?',(person_id,))
    values = cursor.fetchone()
    print(type(values))
    if(type(values) == type(None)):
        conn.commit()
        conn.close()
        return '<script>alert("Invalid url!");window.location.href = "/member_list"</script>'
    if(request.form['identification']=='other'):
        if(request.form['job']=='会长'):
            cursor.execute(
                '''
                UPDATE person_info SET job = ? WHERE id = ?
                ''',('部员',current_user.id,)
            )
        cursor.execute(
            '''
            UPDATE person_info SET department = ?, job = ? WHERE id = ?
            ''',(request.form['department'],request.form['job'],person_id,)
        )
    else:
        cursor.execute(
            '''
            UPDATE person_info SET department = ? WHERE id = ?
            ''',(request.form['department'],person_id,)
        )
    conn.commit()
    conn.close()
    return redirect('/member_list/'+str(person_id))

@app.route('/signup_management', methods=['GET'])
@login_required
def get_signup_list():
    # 若不是管理员，则返回index页
    if current_user.check_admin() == False:
        return redirect('/index')

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
        return redirect('/signup_management')
    else:
        return redirect('signup_management?' + '&'.join(new_index_list))

    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    args = ['student_id', 'relate_account']
    args_dict = {}
    for arg in args:
        if request.args.get(arg) is not None:
            args_dict[arg] = request.args.get(arg)

    sql_query = "SELECT student_id,relate_account FROM signup_token "
    args_l = []
    if len(args_dict) > 0:
        sql_query += 'WHERE '
        query_list = []
        for key in args_dict.keys():
            query_list.append(key + ' = ?')
            args_l.append(args_dict[key])
        sql_query += ' AND '.join(query_list)
    sql_query += ' ORDER BY student_id DESC'

    # 查询部分
    if len(args_dict) > 0:
        cursor.execute(sql_query, args_l)
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
                conn.commit()
                conn.close()
                return redirect('/member_list')
        else:
            conn.commit()
            conn.close()
            return redirect('/member_list')
    page_item = value[(page_num - 1) * 10 : page_num * 10]

    conn.commit()
    conn.close()

    # 翻页保持url相对不变
    page_info = static_url(current_url, page_num, all_page_num, len(index_list))
    return render_template('member_list.html', input=args, issues=page_item, page_info=page_info, is_memberls=False)

@app.route('/signup_management/create', methods=['GET'])
@login_required
def signup_list_form():
    # 若不是管理员，则返回index页
    if current_user.check_admin() == False:
        return redirect('/index')

    return render_template('member_add.html')

@app.route('/signup_management/create', methods=['POST'])
@login_required
def signup_list_append():
    # 若不是管理员，则返回index页
    if current_user.check_admin() == False:
        return redirect('/index')

    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    student_id = request.form.get('student_id')

    cursor.execute("SELECT COUNT(*) FROM signup_token WHERE student_id = ?", (student_id, ))
    count = cursor.fetchone()[0]

    if count > 0:
        conn.commit()
        conn.close()
        return redirect('/signup_management')
    
    cursor.execute("INSERT INTO signup_token VALUES(?, ?)", (student_id, 0, ))

    conn.commit()
    conn.close()
    return redirect('/signup_management')

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
    cursor.execute('SELECT relate_account FROM signup_token WHERE student_id = ?', (studentid,))
    value = cursor.fetchall()

    # 不在允许注册的学号表之中，或已经注册过，则不允许注册
    print(len(value))
    if len(value) == 0 or int(value[0][0]) > 0:
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
        INSERT INTO person_info(username, password_hash,job)
        VALUES(?,?,?)
    ''', (username, generate_password_hash(password),'部员',))
    cursor.execute("SELECT id FROM person_info WHERE username = ?", (username, ))
    account_id = cursor.fetchone()[0]
    cursor.execute('''
        UPDATE signup_token
        SET relate_account = ?
        WHERE student_id = ?
    ''', (account_id, studentid,))

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
    if (host_id == current_user.id) or current_user.check_admin():
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
    if (host_id != current_user.id) and (current_user.check_admin() == False):
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
        conn.commit()
        conn.close()
        return redirect('/issue_center')

    cursor.execute("SELECT * FROM issue WHERE id = ?", (issue_id,))
    value = cursor.fetchone()
    if value is None:
        conn.commit()
        conn.close()
        return redirect('/issue_center')
    
    # TO 林润：
    # 这里没必要再查询一次了
    # 如果上面那个value是None的话已经返回了，那么此时的value中已经包含了当前issue的所有信息
    # 如果身份为host或管理员允许修改
    if(int(value[1]) != current_user.id) and (current_user.check_admin() == False):
        conn.commit()
        conn.close()
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
    cursor.execute('SELECT * FROM issue WHERE id = ?',(issue_id,))
    values = cursor.fetchone()
    print(type(values))
    if(type(values) == type(None)):
        conn.commit()
        conn.close()
        return '<script>alert("Invalid url!");window.location.href = "/issue_center"</script>'
    #身份验证为host或admin才可以修改
    cursor.execute("SELECT * FROM issue WHERE id = ?", (issue_id,))
    value = cursor.fetchone()
    if(int(value[1]) != current_user.id) and (current_user.check_admin() == False):
        conn.commit()
        conn.close()
        return redirect('/issue_center')

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
    if (host_id == current_user.id) or (current_user.check_admin() == True):
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
        conn.commit()
        conn.close()
        return redirect('/maintenance_center')

    cursor.execute("SELECT * FROM maintenance_data WHERE id = ?", (data_id,))
    value = cursor.fetchone()
    if value is None:
        conn.commit()
        conn.close()
        return redirect('/maintenance_center')

    # 判断是否是host，只有是host才继续进行删除，否则跳回maintenance_center
    host_id = int(value[1])
    if (host_id != current_user.id) and (current_user.check_admin() == False):
        conn.commit()
        conn.close()
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
        conn.commit()
        conn.close()
        return redirect('/maintenance_center')

    cursor.execute("SELECT * FROM maintenance_data WHERE id = ?", (data_id,))
    value = cursor.fetchone()
    if (value is None)or((int(value[1])!=current_user.id)and(current_user.check_admin()==False)):
        conn.commit()
        conn.close()
        return redirect('/maintenance_center')
    # 判断是否是host或admin，只有是host才继续进行编辑，否则跳回maintenance_center

    
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

    data_dict = {
        'id': value_list[0],
        'hostname': value_list[1],
        'date': value_list[2],
        'model': value_list[3],
        'description': value_list[4]
    }
    return render_template('maintenance_modify.html', data=data_dict)

@app.route('/maintenance_center/modify/<int:data_id>', methods=['POST'])
@login_required
def modify_maintenence(data_id):
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(id) FROM maintenance_data")
    max_id = cursor.fetchone()[0]

    # 判断url中的id是否在合法，不合法则返回maintenance_center
    if data_id < 1 or data_id > max_id:
        conn.commit()
        conn.close()
        return redirect('/maintenance_center')

    cursor.execute("SELECT * FROM maintenance_data WHERE id = ?", (data_id,))
    value = cursor.fetchone()
    if (value is None)or((int(value[1])!=current_user.id)and(current_user.check_admin()==False)):
        conn.commit()
        conn.close()
        return redirect('/maintenance_center')

    # 判断是否是host或admin，只有是host才继续进行编辑，否则跳回maintenance_center
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

    identification = current_user.check_admin()
    return render_template('activity_center.html', datas=page_item, page_info=page_info,is_admin=identification)

@app.route('/activity_center/<int:act_id>', methods=['GET'])
@login_required
def activity_detail(act_id):
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM activity WHERE id = ?',(act_id,))
    values = cursor.fetchone()
    print(type(values))
    if(type(values) == type(None)):
        conn.commit()
        conn.close()
        return '<script>alert("Invalid url!");window.location.href = "/activity_center"</script>'
    cursor.execute(
        '''
        SELECT *
        FROM activity
        WHERE id = ?
        ''',(act_id,)
    )
    values = cursor.fetchone()

    if values is None:
        return redirect('/activity_center')

    host_id = values[5]
    hostname = cursor.execute(
        '''
        SELECT username
        FROM person_info
        WHERE id = ?
        ''',(host_id,)
    ).fetchone()[0]
    
    act_detail = {
        'id':values[0],
        'name':values[1],
        'date':values[2],
        'location':values[3],
        'description':values[4],
        'hostname':hostname
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

    is_display_modify = 0
    if (host_id == current_user.id) or (current_user.check_admin() == True):
        is_display_modify = 1
    
    if (not is_participate):
        status = 0
    else:
        status = 1

    return render_template('activity_detail.html', act=act_detail, is_display=is_display_modify,is_participate=status)

@app.route('/activity_center/<int:act_id>', methods=['POST'])
@login_required
def delete_activity(act_id):
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM activity WHERE id = ?',(act_id,))
    values = cursor.fetchone()
    print(type(values))
    if(type(values) == type(None)):
        conn.commit()
        conn.close()
        return '<script>alert("Invalid url!");window.location.href = "/activity_center"</script>'
    if(request.form['action_type']=='drop'):
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
        cursor.execute(
            '''
            INSERT INTO activity_participate VALUES(?, ?, 'Soudayo!')
            ''',(act_id,current_user.id,)
        )
        conn.commit()
        conn.close()
        
        return redirect('/activity_center/'+str(act_id))
    elif(request.form['action_type']=='quit'):
        cursor.execute(
            '''
            DELETE FROM activity_participate 
            WHERE activity_id = ? AND person_id = ?
            ''',(act_id,current_user.id,)
        )
        conn.commit()
        conn.close()
        return redirect('/activity_center/'+str(act_id))

@app.route('/activity_center/<int:act_id>/participate', methods=['GET'])
@login_required
def get_activity_participate(act_id):
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM activity WHERE id = ?", (act_id, ))
    count = int(cursor.fetchone()[0])

    if count == 0:
        conn.commit()
        conn.close()
        return redirect('/activity_center')
    if current_user.check_admin() == False:
        conn.commit()
        conn.close()
        return redirect('/activity_center/{}'.format(act_id))

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
        conn.commit()
        conn.close()
        return redirect('/activity_center/{}/participate'.format(act_id))
    else:
        conn.commit()
        conn.close()
        return redirect('/activity_center/{}/participate?'.format(act_id) + '&'.join(new_index_list))

    args_list = ['id', 'name', 'department', 'job', 'content']
    args_dict = {}
    for arg in args_list:
        if request.args.get(arg) is not None:
            args_dict[arg] = request.args.get(arg)
    
    sql_query = '''
        SELECT person_info.id, person_info.name, person_info.department, person_info.job, activity_participate.content
        FROM person_info, activity_participate
        WHERE activity_participate.activity_id = ? AND person_info.id = activity_participate.person_id 
    '''
    args_l = [act_id]
    if len(args_dict) > 0:
        sql_query += 'AND '
        query_list = []
        for key in args_dict.keys():
            if key != 'content':
                query_list.append("person_info." + key + ' = ?')
            else:
                query_list.append("activity_participate." + key + ' = ?')
            args_l.append(args_dict[key])
        sql_query += ' AND '.join(query_list)
    sql_query += ' ORDER BY id DESC'

    if len(args_list) > 0:
        cursor.execute(sql_query, args_l)
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
                conn.commit()
                conn.close()
                return redirect('/activity_center/{}'.format(act_id))
        else:
            conn.commit()
            conn.close()
            return redirect('/activity_center/{}'.format(act_id))
    page_item = value[(page_num - 1) * 10 : page_num * 10]

    conn.commit()
    conn.close()

    # 翻页保持url相对不变
    page_info = static_url(current_url, page_num, all_page_num, len(index_list))
    return render_template('activity_participate.html',act_id=act_id,datas=page_item,page_info=page_info)

@app.route('/activity_center/<int:act_id>/participate/<int:person_id>', methods=['GET'])
@login_required
def modify_activity_participate_form(act_id, person_id):
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM activity_participate WHERE activity_id = ? AND person_id = ?", (act_id, person_id, ))
    count = cursor.fetchone()[0]

    if count == 0:
        conn.commit()
        conn.close()
        return redirect('/activity_center')
    if current_user.check_admin() == False:
        conn.commit()
        conn.close()
        return redirect('/activity_center')

    cursor.execute("SELECT name FROM activity WHERE id = ?", (act_id, ))
    act_name = cursor.fetchone()[0]
    cursor.execute("SELECT name FROM activity WHERE id = ?", (act_id, ))
    person_name = cursor.fetchone()[0]

    cursor.execute("SELECT content FROM activity_participate WHERE activity_id = ? AND person_id = ?", (act_id, person_id, ))
    content = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    info_dict = {
        'act_id':act_id,
        'act_name':act_name,
        'person_id':person_id,
        'person_name':person_name,
        'content':content
    }

    return render_template('activity_participate_modify.html', info_dict=info_dict)

@app.route('/activity_center/<int:act_id>/participate/<int:person_id>', methods=['POST'])
@login_required
def modify_activity_participate(act_id, person_id):
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM activity_participate WHERE activity_id = ? AND person_id = ?", (act_id, person_id, ))
    count = cursor.fetchone()[0]

    if count == 0:
        conn.commit()
        conn.close()
        return redirect('/activity_center')
    if current_user.check_admin() == False:
        conn.commit()
        conn.close()
        return redirect('/activity_center')

    cursor.execute("UPDATE activity_participate SET content = ? WHERE activity_id = ? AND person_id = ?", (request.form.get('content'), act_id, person_id, ))

    conn.commit()
    conn.close()

    return redirect('/activity_center/{}/participate'.format(act_id))

@app.route('/activity_center/<int:act_id>/participate/delete', methods=['GET'])
@login_required
def remove_activity_participate(act_id):
    if request.args.get('id') is None:
        return redirect('/activity_center/{}'.format(act_id))
    if current_user.check_admin() == False:
        return redirect('/activity_center/{}'.format(act_id))
    person_id = request.args.get('id')
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM activity_participate WHERE activity_id = ? AND person_id = ?", (act_id, person_id, ))
    count = cursor.fetchone()[0]
    if count == 0:
        conn.commit()
        conn.close()
        return redirect('/activity_center/{}'.format(act_id))

    cursor.execute("DELETE FROM activity_participate WHERE activity_id = ? AND person_id = ?", (act_id, person_id, ))
    conn.commit()
    conn.close()
    return redirect('/activity_center/{}/participate'.format(act_id))

@app.route('/activity_center/<int:act_id>/add', methods=['GET'])
@login_required
def get_activity_participate_form(act_id):
    if current_user.check_admin() == False:
        return redirect('/activity_center/{}'.format(act_id))
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM activity WHERE id = ?", (act_id, ))
    count = cursor.fetchone()[0]

    if count == 0:
        conn.commit()
        conn.close()
        return redirect('/activity_center')

    info_dict = {
        'act_id': act_id
    }

    return render_template('activity_participate_add.html',info_dict=info_dict)

@app.route('/activity_center/<int:act_id>/add', methods=['POST'])
@login_required
def post_activity_participate_form(act_id):
    if current_user.check_admin() == False:
        return redirect('/activity_center/{}'.format(act_id))
    if request.form.get('person_id') is None:
        return redirect('/activity_center/{}'.format(act_id))
    person_id = request.form.get('person_id')
    content = request.form.get('content')

    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM activity WHERE id = ?", (act_id, ))
    count = cursor.fetchone()[0]

    if count == 0:
        conn.commit()
        conn.close()
        return redirect('/activity_center')

    cursor.execute("SELECT COUNT(*) FROM person_info WHERE id = ?", (person_id, ))
    count = cursor.fetchone()[0]

    if count == 0:
        conn.commit()
        conn.close()
        return redirect('/activity_center/{}'.format(act_id))

    cursor.execute("SELECT COUNT(*) FROM activity_participate WHERE activity_id = ? AND person_id = ?", (act_id, person_id, ))
    count = cursor.fetchone()[0]

    if count > 0:
        conn.commit()
        conn.close()
        return redirect('/activity_center/{}'.format(act_id))

    cursor.execute("INSERT INTO activity_participate VALUES(?, ?, ?)", (act_id, person_id, content, ))
    conn.commit()
    conn.close()

    return redirect('/activity_center/{}/participate'.format(act_id))

@app.route('/activity_center/<int:act_id>/reply', methods=['GET'])
@login_required
def get_activity_reply(act_id):
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM activity WHERE id = ?", (act_id, ))
    count = int(cursor.fetchone()[0])

    if count == 0:
        conn.commit()
        conn.close()
        return redirect('/activity_center')
    if current_user.check_admin() == False:
        conn.commit()
        conn.close()
        return redirect('/activity_center/{}'.format(act_id))

    cursor.execute("SELECT id, submitter, contact, content, suggestion FROM reply WHERE activity_id = ?", (act_id, ))
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
                conn.commit()
                conn.close()
                return redirect('/activity_center/{}'.format(act_id))
        else:
            conn.commit()
            conn.close()
            return redirect('/activity_center/{}'.format(act_id))
    page_item = value[(page_num - 1) * 10 : page_num * 10]

    conn.commit()
    conn.close()

    current_url = str(request.full_path)
    indexes = current_url.partition('?')[2]
    if indexes == '':
        index_list = []
    else:
        index_list = indexes.split('&')

    # 翻页保持url相对不变
    page_info = static_url(current_url, page_num, all_page_num, len(index_list))
    return render_template('activity_reply.html', act_id=act_id, datas=page_item, page_info=page_info)

@app.route('/activity_center/modify/<int:act_id>', methods=['GET'])
@login_required
def edit_activity(act_id):
    if current_user.check_admin() == False:
        return redirect('/activity_center')
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM activity WHERE id = ?',(act_id,))
    values = cursor.fetchone()
    print(type(values))
    if(type(values) == type(None)):
        conn.commit()
        conn.close()
        return '<script>alert("Invalid url!");window.location.href = "/activity_center"</script>'
    cursor.execute(
        '''
        SELECT *
        FROM activity
        WHERE id = ?
        ''',(act_id,)
    )
    values = cursor.fetchone()
    host_id = values[5]
    hostname = cursor.execute(
        '''
        SELECT username
        FROM person_info
        WHERE id = ?
        ''',(host_id,)
    ).fetchone()[0]
    
    act_detail = {
        'id':values[0],
        'name':values[1],
        'date':values[2],
        'location':values[3],
        'description':values[4],
        'hostname':hostname
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

    is_display_modify = 0
    if (host_id == current_user.id) or (current_user.check_admin() == True):
        is_display_modify = 1
    
    if (not is_participate):
        status = 0
    else:
        status = 1

    return render_template('activity_modify.html', act=act_detail, is_display=is_display_modify,is_participate=status)

@app.route('/activity_center/modify/<int:act_id>', methods=['POST'])
@login_required
def save_activity(act_id):
    if(current_user.check_admin()==False):
        redirect('/activity_center')
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM activity WHERE id = ?',(act_id,))
    values = cursor.fetchone()
    if(type(values)==type(None)):
        conn.commit()
        conn.close()
        return'''
        <script>
            alert("Invalid url!");
            window.location.herf='/activity_center'
        </script>
        '''
    cursor.execute(
        '''
        UPDATE activity
        SET
            name = ?,
            date = ?,
            location = ?,
            description = ?
        WHERE id = ?
        ''',(request.form['name'],request.form['date'],request.form['location'],request.form['description'],act_id,)
    )
    conn.commit()
    conn.close()

    return redirect('/activity_center/'+str(act_id))

@app.route('/activity_center/create',methods=['GET'])
@login_required
def edit_new_activity():
    if current_user.check_admin() == False:
        return redirect('/activity_center')
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
    if current_user.check_admin() == False:
        return redirect('/activity_center')
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

@app.route('/finance_center', methods=['GET'])
@login_required
def get_finance_data_from_center():
    if current_user.check_admin() == False:
        return redirect('/index')
    
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
        return redirect('/finance_center')
    else:
        return redirect('/finance_center?' + '&'.join(new_index_list))

    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    cursor.execute("pragma table_info(bill)")
    value = cursor.fetchall()
    args_list = []
    for i in value:
        args_list.append(i[1])

    args_dict = {}
    for key in args_list:
        if request.args.get(key) is not None:
            args_dict[key] = request.args.get(key)
    
    # 构建SQL查询语句
    sql_query = 'SELECT {} FROM bill '.format(','.join(args_list))
    args_l = []
    if len(args_dict) > 0:
        sql_query += 'WHERE '
        query_list = []
        for key in args_dict.keys():
            query_list.append(key + ' = ?')
            args_l.append(args_dict[key])
        sql_query += ' AND '.join(query_list)
    sql_query += ' ORDER BY id ASC'

    # 查询部分
    if len(args_dict) > 0:
        cursor.execute(sql_query, args_l)
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
                return redirect('/finance_center')
        else:
            return redirect('/finance_center')
    page_item = value[(page_num - 1) * 10 : page_num * 10]
    # 数据转换：将id转换为用户名，将1/0转换为是/否
    for i in range(len(page_item)):
        tmp = list(page_item[i])
        cursor.execute('''
            SELECT username
            FROM person_info
            WHERE id = ?
        ''', (tmp[2],))
        value = cursor.fetchone()
        if value is None:
            tmp[2] = 'None'
        else:
            tmp[2] = value[0]
        cursor.execute('''
            SELECT name
            FROM activity
            WHERE id = ?
        ''', (tmp[4],))
        value = cursor.fetchone()
        if value is None:
            tmp[4] = 'None'
        else:
            tmp[4] = value[0]
        page_item[i] = tmp
        
    sum = cursor.execute('SELECT SUM(count) FROM bill').fetchone()[0]
    conn.commit()
    conn.close()

    # 翻页保持url相对不变
    page_info = static_url(current_url, page_num, all_page_num, len(index_list))
    #args_list=['账单号','金额','负责人','详情描述','所属活动']
    return render_template('finance_center.html', input=args_list, bills=page_item, page_info=page_info, account_re=sum)

@app.route('/finance_center/create', methods=['GET'])
@login_required
def edit_new_bill():
    if current_user.check_admin() == False:
        return redirect('/index')
    return render_template('bill_create.html')

@app.route('/finance_center/create', methods=['POST'])
@login_required
def create_new_bill():
    if current_user.check_admin() == False:
        return redirect('/index')
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM person_info WHERE username = ?',(request.form['responsible_person'],))
    values = cursor.fetchall()
    if (type(values)!=type(None)):
        responsible_person_id = values[0][0]
    else:
        conn.commit()
        conn.close()
        return '''
        <script>
            alert("账单负责人不存在..");
            window.location.href = "/finance_center/create";
        </script>
        '''
    if request.form['rel_act'] != '':
        cursor.execute('SELECT id FROM activity WHERE name = ?',(request.form['rel_act'],))
        values = cursor.fetchone()
        if (type(values)!=type(None)):
            responsible_activity_id = values[0]
        else:
            responsible_activity_id = 0
    print((int(request.form['count']),responsible_person_id,request.form['description'],responsible_activity_id,))
    cursor.execute('INSERT INTO bill(count,responsible_person,description,activity_id) VALUES(?,?,?,?)',
    (int(request.form['count']),responsible_person_id,request.form['description'],responsible_activity_id,))
    conn.commit()
    conn.close()
    return redirect('/finance_center')

@app.route('/finance_center/<int:bill_id>', methods=['GET'])
@login_required
def bill_detail(bill_id):
    if current_user.check_admin() == False:
        return redirect('/index')
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bill WHERE id = ?',(bill_id,))
    values = cursor.fetchone()
    if(type(values)==type(None)):
        conn.commit()
        conn.close()
        return '<script>alert("Invalid url!");window.location.href = "/finance_center"</script>'
    else:
        bill_dict={
            'id': values[0],
            'count': values[1],
            'responsible_person': values[2],
            'description': values[3],
            'rel_act': values[4]
        }
        cursor.execute('SELECT username FROM person_info WHERE id = ?',(bill_dict['responsible_person'],))
        bill_dict['responsible_person']=cursor.fetchone()[0]
        cursor.execute('SELECT name FROM activity WHERE id = ?',(bill_dict['rel_act'],))
        values = cursor.fetchone()
        if(type(values)==type(None)):
            bill_dict['rel_act']='None'
        else:
            bill_dict['rel_act']=values[0]
        identification = 1
        if current_user.check_minister() == False:
            identification = 0
        return render_template('bill_detail.html', bill=bill_dict, is_minister=identification)

@app.route('/finance_center/<int:bill_id>', methods=['POST'])
@login_required
def bill_delete(bill_id):
    if current_user.check_admin() == False:
        return redirect('/index')
    if current_user.check_minister() == False:
        return redirect('/finance_center')
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bill WHERE id = ?',(bill_id,))
    values = cursor.fetchone()
    if(type(values)==type(None)):
        conn.commit()
        conn.close()
        return '<script>alert("Invalid url!");window.location.href = "/finance_center"</script>'
    else:
        cursor.execute('DELETE FROM bill WHERE id = ?',(bill_id,))
        conn.commit()
        conn.close()
        return redirect('/finance_center')

@app.route('/finance_center/modify/<int:bill_id>', methods=['GET'])
@login_required
def edit_bill_detail(bill_id):
    if current_user.check_admin() == False:
        return redirect('/index')
    if current_user.check_minister() == False:
        return redirect('/finance_center')
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bill WHERE id = ?',(bill_id,))
    values = cursor.fetchone()
    if(type(values)==type(None)):
        conn.commit()
        conn.close()
        return '<script>alert("Invalid url!");window.location.href = "/finance_center"</script>'
    else:
        bill_dict={
            'id': values[0],
            'count': values[1],
            'responsible_person': values[2],
            'description': values[3],
            'rel_act': values[4]
        }
        cursor.execute('SELECT username FROM person_info WHERE id = ?',(bill_dict['responsible_person'],))
        bill_dict['responsible_person']=cursor.fetchone()[0]
        cursor.execute('SELECT name FROM activity WHERE id = ?',(bill_dict['rel_act'],))
        values = cursor.fetchone()
        if(type(values)==type(None)):
            bill_dict['rel_act']='None'
        else:
            bill_dict['rel_act']=values[0]
        return render_template('bill_modify.html', bill=bill_dict)

@app.route('/finance_center/modify/<int:bill_id>', methods=['POST'])
@login_required
def modify_bill_detail(bill_id):
    if current_user.check_admin() == False:
        return redirect('/index')
    if current_user.check_minister() == False:
        return redirect('/finance_center')
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bill WHERE id = ?',(bill_id,))
    values = cursor.fetchone()
    if(type(values)==type(None)):
        conn.commit()
        conn.close()
        return '<script>alert("Invalid url!");window.location.href = "/finance_center"</script>'
    else:
        cursor.execute('SELECT id FROM person_info WHERE username = ?',(request.form['rep_person'],))
        values = cursor.fetchone()
        if (type(values)!=type(None)):
            responsible_person_id = values[0]
        else:
            conn.commit()
            conn.close()
            return '''
            <script>
                alert("账单负责人不存在..");
                window.location.href = "/finance_center";
            </script>
            '''
        if request.form['rel_act'] != '':
            cursor.execute('SELECT id FROM activity WHERE name = ?',(request.form['rel_act'],))
            values = cursor.fetchone()
            if len(values) > 0:
               responsible_activity_id = values[0]
            else:
                responsible_activity_id = 0
        cursor.execute(
            '''
            UPDATE bill
            SET
                responsible_person = ?,
                count = ?,
                description = ?,
                activity_id = ?
            WHERE id = ?
            ''',(responsible_person_id,int(request.form['count']),request.form['description'],responsible_activity_id,bill_id,)
        )
        conn.commit()
        conn.close()
        return redirect('/finance_center/'+str(bill_id))

@app.route('/item_center', methods=['GET'])
@login_required
def get_item_info_from_center():
    if current_user.check_admin() == False:
        return redirect('/index')
    
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
        return redirect('/item_center')
    else:
        return redirect('/item_center?' + '&'.join(new_index_list))

    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()

    cursor.execute("pragma table_info(item)")
    value = cursor.fetchall()
    args_list = []
    for i in value:
        args_list.append(i[1])

    args_dict = {}
    for key in args_list:
        if request.args.get(key) is not None:
            args_dict[key] = request.args.get(key)
    
    # 构建SQL查询语句
    sql_query = 'SELECT {} FROM item '.format(','.join(args_list))
    args_l = []
    if len(args_dict) > 0:
        sql_query += 'WHERE '
        query_list = []
        for key in args_dict.keys():
            query_list.append(key + ' = ?')
            args_l.append(args_dict[key])
        sql_query += ' AND '.join(query_list)
    sql_query += ' ORDER BY id ASC'

    # 查询部分
    if len(args_dict) > 0:
        cursor.execute(sql_query, args_l)
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
                return redirect('/finance_center')
        else:
            return redirect('/finance_center')
    page_item = value[(page_num - 1) * 10 : page_num * 10]
    # 数据转换：将id转换为用户名
    for i in range(len(page_item)):
        tmp = list(page_item[i])
        cursor.execute('''
            SELECT username
            FROM person_info
            WHERE id = ?
        ''', (tmp[6],))
        value = cursor.fetchone()
        if value is None:
            tmp[6] = 'None'
        else:
            tmp[6] = value[0]
        status_dict = {1:'使用中',2:'已弃用'}
        tmp[2]=status_dict[tmp[2]]
        page_item[i] = tmp
        
    count= cursor.execute('SELECT COUNT(id) FROM item').fetchone()[0]
    conn.commit()
    conn.close()

    # 翻页保持url相对不变
    page_info = static_url(current_url, page_num, all_page_num, len(index_list))
    #args_list=['财物编号','财物名称','财物状态','财物描述','收录时间','弃用时间','负责人','所属账单编号']
    return render_template('item_center.html', input=args_list, items=page_item, page_info=page_info, account_re=count)

@app.route('/item_center/create', methods=['GET'])
@login_required
def edit_new_item():
    if current_user.check_admin() == False:
        return redirect('/index')
    return render_template('item_add.html')

@app.route('/item_center/create', methods=['POST'])
@login_required
def add_new_item():
    if current_user.check_admin() == False:
        return redirect('/index')
    import time
    localtime = time.localtime(time.time())
    date = '{}-{}-{}'.format(localtime.tm_year,localtime.tm_mon,localtime.tm_mday,)
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM person_info WHERE username = ?',(request.form['rep_person'],))
    values = cursor.fetchone()
    if (type(values)!=type(None)):
            responsible_person_id = values[0]
    else:
        conn.commit()
        conn.close()
        return '''
        <script>
            alert("财物负责人不存在..");
            window.location.href = "/finance_center";
        </script>
        '''   
    cursor.execute('SELECT * FROM bill WHERE id = ?',(request.form['rel_bill']))
    values = cursor.fetchone()
    if (type(values)!=type(None)):
        pass
    else:
        conn.commit()
        conn.close()
        return '''
        <script>
            alert("相关账单不存在..");
            window.location.href = "/finance_center";
        </script>
        '''
    status_dict = {'使用中':1,'已弃用':2}
    cursor.execute(
        '''
        INSERT INTO item(name,status,description,get_date,abandon_date,rep_person,rel_bill)
        VALUES(?,?,?,?,?,?,?)
        ''',(
            request.form['name'],
            status_dict[request.form['status']],
            request.form['description'],
            date,
            None,
            responsible_person_id,
            request.form['rel_bill'],
        )
    )
    conn.commit()
    conn.close()
    return redirect('/item_center')

@app.route('/item_center/<int:item_id>', methods=['GET'])
@login_required
def item_detail(item_id):
    if current_user.check_admin() == False:
        return redirect('/index')
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM item WHERE id = ?',(item_id,))
    values = cursor.fetchone()
    if(type(values)==type(None)):
        conn.commit()
        conn.close()
        return '<script>alert("Invalid url!");window.location.href = "/item_center"</script>'
    else:
        item_dict = {
            'id': values[0],
            'name': values[1],
            'status': values[2],
            'description': values[3],
            'get_date': values[4],
            'abandon_date': values[5],
            'rep_person': values[6],
            'rel_bill': values[7]
        }
        rep_person = cursor.execute('SELECT username From person_info WHERE id = ?',(item_dict['rep_person'],)).fetchone()[0]
        item_dict['rep_person'] = rep_person
        conn.commit()
        conn.close()
        identification = 0
        if current_user.check_minister() == True:
            identification = 1
        return render_template('item_detail.html', item=item_dict, is_minister=identification)

@app.route('/item_center/<int:item_id>', methods=['POST'])
@login_required
def item_abandon(item_id):
    if current_user.check_admin() == False:
        return redirect('/index')
    if current_user.check_minister() == False:
        return redirect('/item_center')
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM item WHERE id = ?',(item_id,))
    values = cursor.fetchone()
    if(type(values)==type(None)):
        conn.commit()
        conn.close()
        return '<script>alert("Invalid url!");window.location.href = "/item_center"</script>'
    else:
        cursor.execute('SELECT status FROM item WHERE id = ?',(item_id,))
        values = cursor.fetchone()[0]
        if(values==2):
            conn.commit()
            conn.close()
            return redirect('/item_center/'+str(item_id))
        import time
        localtime = time.localtime(time.time())
        date = '{}-{}-{}'.format(localtime.tm_year,localtime.tm_mon,localtime.tm_mday,)
        cursor.execute('UPDATE item SET status = 2 , abandon_date = ? WHERE id = ?',(date,item_id,))
        conn.commit()
        conn.close()
        return redirect('/item_center/'+str(item_id))

@app.route('/item_center/modify/<int:item_id>', methods=['GET'])
@login_required
def item_edit(item_id):
    if current_user.check_admin() == False:
        return redirect('/index')
    if current_user.check_minister() == False:
        return redirect('/item_center')
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM item WHERE id = ?',(item_id,))
    values = cursor.fetchone()
    if(type(values)==type(None)):
        conn.commit()
        conn.close()
        return '<script>alert("Invalid url!");window.location.href = "/item_center"</script>'
    else:
        item_dict = {
            'id': values[0],
            'name': values[1],
            'status': values[2],
            'description': values[3],
            'get_date': values[4],
            'abandon_date': values[5],
            'rep_person': values[6],
            'rel_bill': values[7]
        }
        rep_person = cursor.execute('SELECT username From person_info WHERE id = ?',(item_dict['rep_person'],)).fetchone()[0]
        item_dict['rep_person'] = rep_person
        conn.commit()
        conn.close()
        identification = 0
        if current_user.check_minister() == True:
            identification = 1
        return render_template('item_modify.html', item=item_dict, is_minister=identification)

@app.route('/item_center/modify/<int:item_id>', methods=['POST'])
@login_required
def item_modify(item_id):
    if current_user.check_admin() == False:
        return redirect('/index')
    if current_user.check_minister() == False:
        return redirect('/item_center')
    conn = sqlite3.connect('../../RUCCA.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM item WHERE id = ?',(item_id,))
    values = cursor.fetchone()
    if(type(values)==type(None)):
        conn.commit()
        conn.close()
        return '<script>alert("Invalid url!");window.location.href = "/item_center"</script>'
    else:
        cursor.execute('SELECT id FROM person_info WHERE username = ?',(request.form['rep_person'],))
        values = cursor.fetchone()
        if (type(values)!=type(None)):
            responsible_person_id = values[0]
        else:
            conn.commit()
            conn.close()
            return '''
            <script>
                alert("财物负责人不存在..");
                window.location.href = "/finance_center";
            </script>
            '''   
        cursor.execute(
            '''
            UPDATE item
            SET
                name = ?,
                status = ?,
                get_date = ?,
                abandon_date = ?,
                rel_bill = ?,
                rep_person = ?,
                description = ?
            WHERE id = ?
            ''',(
                request.form['name'],
                request.form['status'],
                request.form['get_date'],
                request.form['abandon_date'],
                request.form['rel_bill'],
                responsible_person_id,
                request.form['description'],
                item_id
            )
        )
        present_status = cursor.execute('SELECT status FROM item WHERE id = ?',(item_id,)).fetchone()[0]
        if(present_status==1):
            cursor.execute("UPDATE item SET abandon_date = null WHERE id = ?",(item_id,))
        elif(present_status==2):
            import time
            localtime = time.localtime(time.time())
            date = '{}-{}-{}'.format(localtime.tm_year,localtime.tm_mon,localtime.tm_mday,)
            if(request.form['abandon_date']>date):
                cursor.execute('UPDATE item SET abandon_date = ? WHERE id = ?',(date,item_id,))
        if(request.form['get_date']>date):
            cursor.execute('UPDATE item SET get_date = ? WHERE id = ?',(date,item_id,))
        conn.commit()
        conn.close()
        return redirect('/item_center/'+str(item_id))

if __name__ == '__main__':
    app.run(debug=True)
