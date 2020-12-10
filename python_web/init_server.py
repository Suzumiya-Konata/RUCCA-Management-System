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

"""

cursor.execute("SELECT username FROM person_info")
value = cursor.fetchall()

print(value)

conn.commit()
conn.close()