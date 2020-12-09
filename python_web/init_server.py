import sqlite3
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

conn = sqlite3.connect("test.db")
cursor = conn.cursor()

"""
cursor.execute('''
    CREATE TABLE info
    (
    username VARCHAR(20) PRIMARY KEY,
    age INT,
    dept VARCHAR(20),
    FOREIGN KEY(username) REFERENCES user(usernamess)
    )
''')


cursor.execute('''
    INSERT INTO info
    VALUES('Tadokoro', '24', 'karate')
''')

cursor.execute('''
    INSERT INTO info
    VALUES('innovation', '27', 'starcraft')
''')

cursor.execute('''
    INSERT INTO info
    VALUES('TainakaRitsu', '16', 'k-on')
''')
"""

password_hash = generate_password_hash('114514')

cursor.execute('''
    SELECT * FROM user WHERE username = 'Tadokoro'
''')

values = cursor.fetchall()
print(values)

conn.commit()
conn.close()