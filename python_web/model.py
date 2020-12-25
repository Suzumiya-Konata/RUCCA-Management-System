from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import UserMixin
import sqlite3

class User(UserMixin):
    def __init__(self, username):
        self.username = username
        self.id = int(self.get_id())
        self.is_admin = self.check_admin()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """save username and password hash to sqlite"""
        self.password_hash = generate_password_hash(password)
        # 应修改为自己电脑上.db文件的地址
        conn = sqlite3.connect("../../RUCCA.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*)
            FROM person_info
            WHERE id = ?
        ''', (self.id,))
        value = cursor.fetchone()[0]
        if value == 0:
            cursor.execute('''
                INSERT INTO person_info(username, password_hash)
                Values(?,?)
                ''', (self.username, self.password_hash,))
        else:
            cursor.execute('''
                UPDATE person_info
                SET password = ?
                WHERE id = ?
            ''', (self.password_hash, self.id,))
        conn.commit()
        conn.close()

    def verify_password(self, password):
        password_hash = self.get_password_hash()
        if password_hash is None:
            return False
        return check_password_hash(password_hash, password)

    def get_password_hash(self):
        """try to get password hash from sqlite.
        return password hash: if the there is corresponding user in 
        the sqlite, return password hash.
        None: if there is no corresponding user, return None.
        """
        # 应修改为自己电脑上.db文件的地址
        conn = sqlite3.connect("../../RUCCA.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT password_hash
            FROM person_info
            WHERE id = ?
        ''', (self.id,))
        value = cursor.fetchall()
        if len(value) == 0:
            return None
        else:
            return value[0][0]
        conn.commit()
        conn.close()
        
    def check_admin(self):
        if self.id != 0:
            conn = sqlite3.connect("../../RUCCA.db")
            cursor = conn.cursor()
            cursor.execute("SELECT job FROM person_info WHERE id = ?", (self.id,))
            
            lev_dict = {'部员':1,'副部长':2,'部长':3,'副会长':4,'会长':5}
            value = cursor.fetchone()[0]

            if value not in lev_dict:
                return False
            if lev_dict[value] > 2:
                return True
            else:
                return False
        return False

    def check_minister(self):
        if self.id != 0:
            conn = sqlite3.connect("../../RUCCA.db")
            cursor = conn.cursor()
            cursor.execute("SELECT job FROM person_info WHERE id = ?", (self.id,))
            
            lev_dict = {'部员':1,'副部长':2,'部长':3,'副会长':4,'会长':5}
            value = cursor.fetchone()[0]
            if value not in lev_dict:
                return False
            if lev_dict[value] == 5:
                return True
            else:
                return False
        return False

    def get_id(self):
        """get username from sqlite
        """
        if self.username is not None:
            # 应修改为自己电脑上.db文件的地址
            conn = sqlite3.connect("../../RUCCA.db")
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id
                FROM person_info
                WHERE username = ?
            ''', (self.username,))
            value = cursor.fetchone()
            conn.commit()
            conn.close()
            if value is not None:
                return str(value[0])
        return "0"

    @staticmethod
    def get(user_id):
        """try to return user_name corresponding User object.
        This method is used by load_user callback function
        """
        if user_id is None:
            return None
        # 应修改为自己电脑上.db文件的地址
        conn = sqlite3.connect("../../RUCCA.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT username
            FROM person_info
            WHERE id = ?
        ''', (user_id,))
        value = cursor.fetchall()
        conn.commit()
        conn.close()
        if len(value) != 0:
            return User(value[0][0])
        return None