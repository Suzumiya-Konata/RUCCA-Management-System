import sqlite3
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import uuid

conn = sqlite3.connect("../../RUCCA.db")
cursor = conn.cursor()

# 注：sqlite不支持ALTER TABLE DROP COLUMN的形式
#cursor.execute("DROP TABLE maintenance_data")

cursor.execute(
    '''
    UPDATE maintenance_data
    SET
        description = '123&#10;123'
    WHERE id = 23
    '''
)

conn.commit()
conn.close()