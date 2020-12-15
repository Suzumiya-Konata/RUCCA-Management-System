import sqlite3
from werkzeug.security import generate_password_hash
conn = sqlite3.connect('../../RUCCA.db')
cursor = conn.cursor()
cursor.execute("UPDATE person_info SET id = 2 WHERE username = 'Suzumiya_Konata'")
cursor.execute("INSERT INTO person_info(username,password_hash) VALUES('linrun',?)", (generate_password_hash('linrun'),))
cursor.execute("SELECT * FROM person_info")
v = cursor.fetchall()
conn.commit()
conn.close()
print(v)