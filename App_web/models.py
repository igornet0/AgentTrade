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
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    balance = db.Column(db.Float)
    path_agent = db.Column(db.String(80), nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db.session.add(self)
        db.session.commit()


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    url = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)
    text = db.Column(db.String, nullable=False)
    img_folder = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(80), nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db.session.add(self)
        db.session.commit()


class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price_now = db.Column(db.Float)
    status_parser = db.Column(db.String(80))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db.session.add(self)
        db.session.commit()

    def update_price(self, new_price):
        self.price_now = new_price
        db.session.commit()

    def get_price(self):
        return self.price_now


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_agent = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    id_stock = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    time_publish = db.Column(db.Date, nullable=False)
    time_accept = db.Column(db.Date)
    type = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float)
    amount = db.Column(db.Float)
    status = db.Column(db.String(80), nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db.session.add(self)
        db.session.commit()

    def update_status(self, new_status):
        if not new_status in ["published", "accepted", "rejected", "canceled"]:
            return {"error": "Invalid status"}
        
        self.status = new_status
        db.session.commit()

        return {"status": self.status}

    def change_price(self, new_price):
        self.price = new_price
        db.session.commit()

    def change_amount(self, new_amount):
        self.amount = new_amount
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()


class AgentList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_agent = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    id_stock = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    amount = db.Column(db.Float)
    price_avg = db.Column(db.Float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db.session.add(self)
        db.session.commit()

    def update_amount(self, new_amount):
        if new_amount == 0:
            self.delete()
            return
        
        self.amount = new_amount
        db.session.commit()

    def update_price_avg(self, new_price_avg):
        self.price_avg = new_price_avg
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    

class StockHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_stock = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    time = db.Column(db.Date, nullable=False)
    price_open = db.Column(db.Float)
    price_close = db.Column(db.Float)
    price_high = db.Column(db.Float)
    price_low = db.Column(db.Float)
    value = db.Column(db.Float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db.session.add(self)
        db.session.commit()


