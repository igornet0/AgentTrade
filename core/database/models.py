# модели для БД

from sqlalchemy import DateTime, ForeignKey, Float, String, Text, BigInteger, func, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from passlib.context import CryptContext

# Создаем объект для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# создаем базовый класс для всех остальных
class Base(DeclarativeBase):
    # дата создания записи в БД, тип DateTime, func.now() - текущее время
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    # дата изменения записи в БД
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=True)
    phone: Mapped[str] = mapped_column(String(13), nullable=True)
    balance: Mapped[float] = mapped_column(Float, default=0)
    login: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Метод для хеширования пароля
    def set_password(self, password: str):
        self.password = pwd_context.hash(password)

    # Метод для проверки пароля
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)


class Portfolio(Base):
    __tablename__ = 'portfolio'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    coin_id: Mapped[int] = mapped_column(ForeignKey('coin.id', ondelete='CASCADE'), nullable=False)
    coin: Mapped['Coin'] = relationship(back_populates='portfolio')
    user: Mapped['User'] = relationship(backref='portfolio')
    amount: Mapped[float] = mapped_column(Float, default=0)


class Coin(Base):
    __tablename__ = 'coin'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    price_now: Mapped[float] = mapped_column(Float, default=0)

    timeseries: Mapped[list['Timeseries']] = relationship(back_populates='coin')


class Timeseries(Base):
    __tablename__ = 'timeseries'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    coin_id: Mapped[int] = mapped_column(ForeignKey('coin.id'))  
    timestamp: Mapped[str] = mapped_column(String(50)) 
    path_dataset: Mapped[str] = mapped_column(String(100), unique=True)

    coin: Mapped['Coin'] = relationship(back_populates='timeseries')


class Transaction(Base):
    __tablename__ = 'transaction'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(30), default="new")
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    coin_id: Mapped[int] = mapped_column(ForeignKey('coin.id', ondelete='CASCADE'), nullable=False)
    coin: Mapped['Coin'] = relationship(back_populates='transaction')
    user: Mapped['User'] = relationship(backref='transaction')

    def set_status(self, new_status):
        assert not new_status in ["new", "open", "close", "cancel"]

        self.status = new_status


class News(Base):
    __tablename__ = 'news'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(50), default="news")
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    text: Mapped[str] = mapped_column(String(1000), nullable=False)
    date: Mapped[DateTime] = mapped_column(DateTime, default=func.now())


class Agent(Base):
    __tablename__ = 'agent'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    path_model: Mapped[str] = mapped_column(String(100), unique=True)
    version: Mapped[int] = mapped_column(Integer, unique=True)

class NewsModel(Base):
    __tablename__ = 'news_model'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    path_model: Mapped[str] = mapped_column(String(100), unique=True)
    version: Mapped[int] = mapped_column(Integer, unique=True)

class RiskModel(Base):
    __tablename__ = 'risk_model'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    path_model: Mapped[str] = mapped_column(String(100), unique=True)
    version: Mapped[int] = mapped_column(Integer, unique=True)

class MMM(Base):
    __tablename__ = 'mmm'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    path_model: Mapped[str] = mapped_column(String(100), unique=True)
    version: Mapped[int] = mapped_column(Integer, unique=True)

# # класс для банера
# class Banner(Base):
#     __tablename__ = 'banner'

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     # имя банера
#     name: Mapped[str] = mapped_column(String(15), unique=True)
#     description: Mapped[str] = mapped_column(Text, nullable=True)


# # категория товара
# class Category(Base):
#     __tablename__ = 'category'

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(String(150), nullable=False)
#     image: Mapped[str] = mapped_column(String(150), nullable=True)

# class PodCategory(Base):
#     __tablename__ = 'podcategory'

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     category_id: Mapped[int] = mapped_column(ForeignKey('category.id', ondelete='CASCADE'), nullable=False)
#     name: Mapped[str] = mapped_column(String(150), nullable=False)
#     category: Mapped['Category'] = relationship(backref='podcategory')

# # место доставки
# class Place(Base):
#     __tablename__ = 'place'

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(String(150), nullable=False)
#     filter_categorys: Mapped[str] = mapped_column(String, nullable=True)


# class Sirop(Base):
#     __tablename__ = 'sirop'

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(String(150), nullable=False)
#     price: Mapped[int] =  mapped_column(Float, nullable=True)

# class Dop(Base):
#     __tablename__ = 'dop'

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(String(150), nullable=False)
#     price: Mapped[int] =  mapped_column(Float, nullable=True)
#     category_id: Mapped[int] = mapped_column(ForeignKey('category.id', ondelete='CASCADE'), nullable=False)

# # создаем таблицу для продуктов
# class Product(Base):
#     # название таблицы в БД
#     __tablename__ = 'product'

#     # поля (атрибуты), где указываем типы данных полей через Mapped
#     # mapped_column - дополнительные свойства для атрибутов
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     # максимальная длина 150 символов, nullable=False - не может быть пустым
#     name: Mapped[str] = mapped_column(String(150), nullable=False)
#     # указываем тип Text вместо VarChar, чтобы хранить больший объем текста для описания
#     description: Mapped[str] = mapped_column(Text, nullable=True)
#     weight: Mapped[str] = mapped_column(Text, nullable=False)  # Поле для веса товара (целое число)
#     # 4 знака максимум, 2 знака после запятой
#     price: Mapped[str] = mapped_column(Text, nullable=False)
#     # image: Mapped[str] = mapped_column(String(150), nullable=False)
#     # id категории, CASCADE - если удаляется категория, то все продукты также удалятся
#     category_id: Mapped[int] =  mapped_column(ForeignKey('category.id', ondelete='CASCADE'), nullable=True)
#     podcategory_id: Mapped[int] = mapped_column(ForeignKey('podcategory.id', ondelete='CASCADE'), nullable=True)


# class User(Base):
#     __tablename__ = 'user'

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     # идентификатор пользователя в телеграмме
#     user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
#     first_name: Mapped[str] = mapped_column(String(150), nullable=True)
#     last_name: Mapped[str] = mapped_column(String(150), nullable=True)
#     phone: Mapped[str] = mapped_column(String(13), nullable=True)


# class Cart(Base):
#     __tablename__ = 'cart'

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     # идентификатор пользователя в телеграмме
#     # если пользователя удаляют, то его корзина тоже удаляется
#     status: Mapped[str] = mapped_column(String(20), nullable=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
#     # если продукт удаляется, то корзина с этим товаром тоже удаляется
#     product_id: Mapped[int] = mapped_column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
#     # количество товара
#     quantity: Mapped[int]
#     weight: Mapped[int]
#     price: Mapped[float]
#     dop: Mapped[int] = mapped_column(ForeignKey('dop.id', ondelete='CASCADE'), nullable=True)
#     sirop: Mapped[int] = mapped_column(ForeignKey('sirop.id', ondelete='CASCADE'), nullable=True)
#     # обратная взаимосвязь с таблицами user и product,
#     # чтобы выбрать все корзины пользователя и дополнительную информацию о товаре, который заказан
#     place_id: Mapped[int] = mapped_column(ForeignKey('place.id', ondelete='CASCADE'), nullable=True)
#     product: Mapped['Product'] = relationship(backref='cart')
#     place: Mapped['Place'] = relationship(backref='cart')


# class AdminList(Base):
#     __tablename__ = 'admin'
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
#     place: Mapped[int] = mapped_column(Integer, nullable=True)

# class Order(Base):
#     __tablename__ = 'order'
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     status: Mapped[str] = mapped_column(String(20), nullable=False)
#     user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
#     place: Mapped[int] = mapped_column(Integer, nullable=False)
#     data: Mapped[str] = mapped_column(String(100), nullable=False)
#     cards: Mapped[str] = mapped_column(String(150), nullable=False)
#     type_give: Mapped[str] = mapped_column(String(20), nullable=False)
#     summa: Mapped[float] = mapped_column(Float, nullable=False)