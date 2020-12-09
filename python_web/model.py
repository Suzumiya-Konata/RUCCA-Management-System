from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import UserMixin
import sqlite3

class User(UserMixin):
    def __init__(self, username):
        self.username = username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """save username and password hash to sqlite"""
        self.password_hash = generate_password_hash(password)
        conn = sqlite3.connect("test.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*)
            FROM user
            WHERE username = ?
        ''', (self.username,))
        value = cursor.fetchone()[0]
        if value == 0:
            cursor.execute('''
                INSERT INTO user
                Values(?,?)
                ''', (self.username, self.password_hash,))
        else:
            cursor.execute('''
                UPDATE user
                SET password = ?
                WHERE username = ?
            ''', (self.password_hash, self.username,))
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
        conn = sqlite3.connect("test.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT *
            FROM user
            WHERE username = ?
        ''', (self.username,))
        value = cursor.fetchall()
        if len(value) == 0:
            return None
        else:
            return value[0][1]
        conn.commit()
        conn.close()
        

    def get_id(self):
        """get username from sqlite
        """
        if self.username is not None:
            conn = sqlite3.connect("test.db")
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*)
                FROM user
                WHERE username = ?
            ''', (self.username,))
            value = cursor.fetchone()[0]
            conn.commit()
            conn.close()
            if value != 0:
                return self.username
        return None

    @staticmethod
    def get(user_name):
        """try to return user_name corresponding User object.
        This method is used by load_user callback function
        """
        if user_name is None:
            return None
        conn = sqlite3.connect("test.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*)
            FROM user
            WHERE username = ?
        ''', (user_name,))
        value = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        if value != 0:
            return User(user_name)
        return None