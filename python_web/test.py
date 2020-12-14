import sqlite3
conn = sqlite3.connect('../../RUCCA.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM person_info")
v = cursor.fetchall()
print(v)