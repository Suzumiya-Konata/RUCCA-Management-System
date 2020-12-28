import sqlite3
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import uuid

conn = sqlite3.connect("../../RUCCA.db")
cursor = conn.cursor()

# 注：sqlite不支持ALTER TABLE DROP COLUMN的形式
#cursor.execute("DROP TABLE maintenance_data")
"""
cursor.execute(
    '''
    DROP TABLE act_attend
    '''
)

cursor.execute('''
    CREATE TABLE activity(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(20),
        date DATE,
        location VARCHAR(40),
        description VARCHAR(50),
        host_id INT,
        FOREIGN KEY (host_id)
            REFERENCES person_info(id)
    )
''')

cursor.execute("INSERT INTO activity(name, date, location, description, host_id) VALUES('Foundation', '2020-12-19', 'RUC TouHuu.7', 'Blessings for the birthay of RUCCA Management System', 1)")
cursor.execute('''
    CREATE TABLE activity_participate(
        activity_id INT,
        person_id INT,
        content VARCHAR(100),
        PRIMARY KEY(activity_id, person_id),
        FOREIGN KEY (activity_id)
            REFERENCES activity(id),
        FOREIGN KEY (person_id)
            REFERENCES person_info(id)
    )
''')

cursor.execute("INSERT INTO activity_participate VALUES(1, 1, 'Soudayo!')")

cursor.execute('''
    CREATE TABLE reply(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_id INT,
        submitter VARCHAR(10),
        contact VARCHAR(20),
        content VARCHAR(100),
        suggestion VARCHAR(100),
        FOREIGN KEY (activity_id)
            REFERENCES activity(id)
    )
''')

# 获取表中的信息
#cursor.execute('DROP TABLE bill')
cursor.execute(
    '''
    CREATE TABLE bill(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        count INT,
        responsible_person INT,
        description VARCHAR(500),
        activity_id INT,
        FOREIGN KEY (activity_id)
            REFERENCES activity(id),
        FOREIGN KEY (responsible_person)
            REFERENCES person_info(id)
    )'''
)
cursor.execute(
    '''
    INSERT INTO bill
    VALUES(1,50000,1,?,1)
''',("fortest",))
cursor.execute(
    '''
    SELECT * FROM bill 
    '''
)

cursor.execute(
    '''
    CREATE TABLE item(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(20),
        status INT,
        description VARCHAR(500),
        get_date DATE,
        abandon_date DATE,
        rep_person INT,
        rel_bill INT,
        FOREIGN KEY (rep_person)
            REFERENCES person_info(id),
        FOREIGN KEY (rel_bill)
            REFERENCES bill(id)
    )'''
)
cursor.execute(
    '''
    INSERT INTO item
    VALUES(1,'UDisk',1,'fortest',?,?,1,2)
''',(None,None,))
cursor.execute(
    '''
    SELECT * FROM item
    '''
)
value = cursor.fetchall()

cursor.execute("DROP TABLE allowed_signup")
cursor.execute('''
    CREATE TABLE signup_token(
        student_id VARCHAR(10) PRIMARY KEY,
        relate_account INT,
        FOREIGN KEY (relate_account)
            REFERENCES person_info(id)
    )
''')

cursor.execute("INSERT INTO signup_token VALUES(?, ?)", ('2018202059', 2, ))
cursor.execute("INSERT INTO signup_token VALUES(?, ?)", ('2018202090', 5, ))
cursor.execute("INSERT INTO signup_token VALUES(?, ?)", ('2018202133', 1, ))
"""
cursor.execute("INSERT INTO activity_participate VALUES(1, 2, '114514')")
value = cursor.fetchone()

print(value)
conn.commit()
conn.close()