import sqlite3
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import uuid

conn = sqlite3.connect("../../RUCCA.db")
cursor = conn.cursor()

# 注：sqlite不支持ALTER TABLE DROP COLUMN的形式
#cursor.execute("DROP TABLE maintenance_data")

cursor.execute('''
    CREATE TABLE maintenance_data(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        host_id INT,
        added_date DATE,
        model VARCHAR(50),
        description VARCHAR(2000),
        FOREIGN KEY (host_id)
            REFERENCES person_info(id)
    )
''')

'''issue_list = [
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
]'''
import time
localtime = time.localtime(time.time())

for count in range(1,20):
    host = 0
    if count % 2 == 0:
        host = 1
    else:
        host = 2
    cursor.execute('''
        INSERT INTO maintenance_data(host_id, added_date, model, description)
        VALUES(?, ?, ?, ?)
    ''', 
    (host, 
    '{}-{}-{}'.format(localtime.tm_year,localtime.tm_mon,localtime.tm_mday,), 
    'model'+str(count),
    'maintenance_data'+str(count)
    ))

cursor.execute("SELECT * FROM maintenance_data")
value = cursor.fetchall()

for i in value:
    print(i)

conn.commit()
conn.close()