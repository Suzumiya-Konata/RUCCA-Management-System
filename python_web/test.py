'''import sqlite3
from werkzeug.security import generate_password_hash
conn = sqlite3.connect('../../RUCCA.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM activity_participate")
v = cursor.fetchall()
conn.commit()
conn.close()
print(v)'''
import time
localtime = time.localtime(time.time())
date = '{}-{}-{}'.format(localtime.tm_year,localtime.tm_mon,localtime.tm_mday,)
test_date = '{}-{}-{}'.format(2000,9,25)
if(date>test_date):
    print(1)