from sqlalchemy import Column, String
from src.db import Base


class Arenda(Base):
    name = Column(String(100), unique=True, nullable=False)