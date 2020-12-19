import sqlite3
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import uuid

conn = sqlite3.connect("../../RUCCA.db")
cursor = conn.cursor()

# 注：sqlite不支持ALTER TABLE DROP COLUMN的形式
#cursor.execute("DROP TABLE maintenance_data")
"""
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
"""
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

conn.commit()
conn.close()