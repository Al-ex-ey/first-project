from sqlalchemy import Column, Integer, String
from src.db import Base

class Arenda(Base):
    arendator = Column("ФИО арендатора", String(100)) # название арендатора
    contract = Column(String(100), unique=True) # название договора
    debet = Column(Integer) # сумма долга
    credit = Column(Integer) # сумма перплаты   
    insurance_fee = Column(Integer) # страховая сумма
    note = Column(String(400)) # примечание
    business_type = Column(String(100)) # сфера деятельности
    email = Column(String(50)) # адрес эл. почты (официльный адрес прописанный в договоре)
    email2 = Column(String(50)) # адрес эл. почты для дублирования (не оф.)
    email3 = Column(String(50)) # адрес эл. почты для дублирования (не оф. 2)
    phone_nomber = Column(String(60)) # номер телефона (основной)
    phone_nomber2 = Column(String(60)) # номер телефона (запасной)
    phone_nomber3 = Column(String(60)) # номер телефона (запасной 2)
