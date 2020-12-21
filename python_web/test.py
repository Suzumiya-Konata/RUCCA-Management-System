import sqlite3
from werkzeug.security import generate_password_hash
conn = sqlite3.connect('../../RUCCA.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM person_info WHERE id = 14")
v = cursor.fetchall()
conn.commit()
conn.close()
print(v)