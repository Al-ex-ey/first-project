# from sqlalchemy import Column,  Integer
# from src.db import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, declared_attr, sessionmaker

from src.configs import *

engine = create_async_engine(settings.database_url, echo=True)


class PreBase:

    @declared_attr
    def __tablename__(cls):
        # Именем таблицы будет название модели в нижнем регистре.
        return cls.__name__.lower()

    # Во все таблицы будет добавлено поле ID.
    id = Column(Integer, primary_key=True)

Base = declarative_base(cls=PreBase)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)

class Arenda(Base):
    arendator = Column("ФИО арендатора", String(100)) # название арендатора
    contract = Column(String(100), unique=True) # название договора
    debet = Column(Integer) # сумма долга
    credit = Column(Integer) # сумма перплаты   
    insurance_fee = Column(Integer) # страховая сумма
    note = Column(String(200)) # примечание
    business_type = Column(String(100)) # сфера деятельности
    email = Column(String(50)) # адрес эл. почты (официльный адрес прописанный в договоре)
    email2 = Column(String(50)) # адрес эл. почты для дублирования (не оф.)
    email3 = Column(String(50)) # адрес эл. почты для дублирования (не оф. 2)
    phone_nomber = Column(String(60)) # номер телефона (основной)
    phone_nomber2 = Column(String(60)) # номер телефона (запасной)
    phone_nomber3 = Column(String(60)) # номер телефона (запасной 2)





