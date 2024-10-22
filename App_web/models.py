from random import randint
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import numpy 
import datetime
from . import db

def delete_data(db):
    try:
        # Перебираем все таблицы
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        print("All data deleted.")
    except Exception as e:
        db.session.rollback()
        print("Failed to delete data:", e)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time = db.Column(db.String(80), nullable=False)
    stock = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float)
    col = db.Column(db.Float)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time = db.Column(db.String(80), nullable=False)
    stock = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float)
    col = db.Column(db.Float)

class Portfolio(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock = db.Column(db.String(80), nullable=False)
    col = db.Column(db.Float)
    