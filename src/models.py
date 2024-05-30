# from sqlalchemy import Column,  Integer
# from src.db import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, declared_attr, sessionmaker

from src.configs import settings


class PreBase:

    @declared_attr
    def __tablename__(cls):
        # Именем таблицы будет название модели в нижнем регистре.
        return cls.__name__.lower()

    # Во все таблицы будет добавлено поле ID.
    id = Column(Integer, primary_key=True)

Base = declarative_base(cls=PreBase)

engine = create_async_engine(settings.database_url)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)

class Arenda(Base):
    arendator = Column("ФИО арендатора", String(100))
    contract = Column(String(100), unique=True)
    debet = Column(Integer)
    credit = Column(Integer)
    insurance_fee = Column(Integer)
    note = Column(String(200))
    business_type = Column(String(100))
    email = Column(String(50))
    email2 = Column(String(50))
    email3 = Column(String(50))
    phone_nomber = Column(String(60))
    phone_nomber2 = Column(String(60))
    phone_nomber3 = Column(String(60))





