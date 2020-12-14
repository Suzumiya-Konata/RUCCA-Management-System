import sqlite3
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import uuid

conn = sqlite3.connect("../../RUCCA.db")
cursor = conn.cursor()

"""
cursor.execute('''
    CREATE TABLE person_info(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(20) UNIQUE,
        password_hash CHAR(94),
        name VARCHAR(10),
        id_card_number CHAR(18),
        sex CHAR(1),
        phone VARCHAR(11),
        department VARCHAR(10),
        job VARCHAR(10),
        description VARCHAR(100)
    )
''')

cursor.execute('''
    INSERT INTO person_info(
        username,
        password_hash,
        name,
        id_card_number,
        sex,
        phone,
        department,
        job,
        description
    )
    VALUES('Tadokoro', ?, 'Kouji', '11451419190810XXXX', 'M', '1926jzm0817', 'karate', 'senpai', 'enaaaaaaaaaa!')
''', (generate_password_hash('114514'),))

cursor.execute('''
    CREATE TABLE allowed_signup(
        studentid INT PRIMARY KEY
    )
''')

cursor.execute('''
    INSERT INTO allowed_signup
    VALUES(2018202059)
''')

cursor.execute('''
    INSERT INTO allowed_signup
    VALUES(2018202090)
''')

cursor.execute('''
    INSERT INTO allowed_signup
    VALUES(2018202133)
''')

cursor.execute("ALTER TABLE allowed_signup ADD has_signup CHAR")
cursor.execute("UPDATE allowed_signup SET has_signup = '0'")

cursor.execute('''
    CREATE TABLE issue(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        host_id INT,
        start_date DATE,
        description VARCHAR(100),
        is_finished CHAR,
        cert_id INT,
        FOREIGN KEY (host_id)
            REFERENCES person_info(id),
        FOREIGN KEY (cert_id)
            REFERENCES person_info(id)
    )
''')

issue_list = [
    '坚持党对一切工作的领导。',
    '坚持以人民为中心。',
    '坚持全面深化改革。',
    '坚持新发展理念。',
    '坚持人民当家作主。',
    '坚持全面依法治国。',
    '坚持社会主义核心价值体系。',
    '坚持在发展中保障和改善民生。',
    '坚持人与自然和谐共生。',
    '坚持总体国家安全观。',
    '坚持党对人民军队的绝对领导。',
    '坚持“一国两制”和推进祖国统一。',
    '坚持推动构建人类命运共同体。',
    '坚持全面从严治党。'
]

count = 0
for issue in issue_list:
    host = 0
    cert = 0
    if count % 2 == 0:
        host = 1
    else:
        host = 2
        if count % 4 == 1:
            cert = 1
        else:
            cert = 2
    cursor.execute('''
        INSERT INTO issue(host_id, start_date, description, is_finished, cert_id)
        VALUES(?, ?, ?, ?, ?)
    ''', 
    (host, 
    '2020-12-{}'.format(str(7+count).zfill(2)), 
    issue,
    str(count % 2),
    cert
    ))
    count += 1
"""
# 注：cert_id为0代表未被认证

cursor.execute("SELECT * FROM person_info")
value = cursor.fetchall()

for i in value:
    print(i)

conn.commit()
conn.close()