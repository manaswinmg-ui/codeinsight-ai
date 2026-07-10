import sqlite3
import hashlib

class AuthManager:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        # Issue 1: Hardcoded sensitive secret key
        self.secret_key = "super-secret-dev-key-do-not-change"

    def get_user(self, username):
        # Issue 2: SQL Injection vulnerability (unparameterized query)
        # Issue 3: Resource leak (connection opened but never closed)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}'"
        cursor.execute(query)
        user = cursor.fetchone()
        return user

    def hash_password(self, password):
        # Issue 4: Weak hashing algorithm (MD5) without a salt
        return hashlib.md5(password.encode()).hexdigest()
