from flask_login import UserMixin
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db.session.add(self)
        db.session.commit()


class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    balance = db.Column(db.Float)
    path_agent = db.Column(db.String(80), nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db.session.add(self)
        db.session.commit()


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket = db.Column(db.String(80), nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db.session.add(self)
        db.session.commit()


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    time = db.Column(db.String(80), nullable=False)
    ticket = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    type = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float)
    value = db.Column(db.Float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db.session.add(self)
        db.session.commit()


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    time = db.Column(db.String(80), nullable=False)
    ticket = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    price = db.Column(db.Float)
    value = db.Column(db.Float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db.session.add(self)
        db.session.commit()


class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    ticket = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    value = db.Column(db.Float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db.session.add(self)
        db.session.commit()
    