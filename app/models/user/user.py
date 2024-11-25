from sqlalchemy import Column, Integer, String
import sqlalchemy

Base = sqlalchemy.orm.declarative_base()

class User(Base):
    __tablename__ = 'users';
    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String, index=True)
    email: str = Column(String)
    password: str = Column(String)