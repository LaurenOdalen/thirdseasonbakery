from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import app
from flask import Flask, flash 
import re
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

class User:
    def __init__(self,data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']


    @classmethod
    def new_user(cls,data):
        ha_shalom = bcrypt.generate_password_hash(data['password'])
        user = {
            "first_name": data['first_name'],
            "last_name": data['last_name'],
            "email": data['email'],
            "password": ha_shalom
        }
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, NOW(), NOW())"
        return connectToMySQL("third_season_schema").query_db(query, user)


    @classmethod
    def get_all(cls):
            query = "SELECT * FROM users;"
            results = connectToMySQL("third_season_schema").query_db(query)
            users = []
            for row in results:
                users.append(cls(row))
            return users


    @classmethod
    def select_email(cls, data):
        query = "SELECT * FROM users WHERE email = %(email)s"
        results = connectToMySQL("third_season_schema").query_db(query, data)
        if results:
            return cls(results[0])
        return False


    @classmethod
    def select_id(cls,data):
        query = "SELECT * FROM users WHERE id = %(id)s"
        results = connectToMySQL("third_season_schema").query_db(query,data)
        return cls(results[0])


    # method to validate user who is already in database
    @staticmethod
    def validate_email(data):
        user = User.select_email(data)
        if not user:
            flash("Invalid email and or password", "login")
            return False
        if not bcrypt.check_password_hash(user.password, data['password']):
            flash('Invalid email and or password', "login")
            return False
        return True 


    # method to validate new user who is yet to be in database
    @staticmethod
    def validate_user(data):
        is_valid = True 
        if len(data['first_name']) < 3:
            flash("First name must be at least 3 characters.", "register")
            is_valid = False
        if len(data['last_name']) < 3:
            flash("Last name must be at least 3 characters.", "register")
            is_valid = False
        if not EMAIL_REGEX.match(data['email']): 
            flash("Ivalid email address")
            is_valid = False
        elif User.select_email(data):
            flash("Email already in use", "register")
            is_valid = False
        if len(data['password']) < 8:
            flash("Password must be at least 8 characters.", "register")
            is_valid = False
        elif (data['confirm_password']) != (data['password']):
            flash("Password does not match", "register")
            is_valid = False
        return is_valid

