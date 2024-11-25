from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
import sqlalchemy
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

app = FastAPI()

# Database setup
DATABASE_URL = 'sqlite:///sanquin.db';
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()


class User(Base):
    __tablename__ = 'users';
    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String, index=True)
    email: str = Column(String)
    password: str = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

@app.post('/users/', response_model=UserResponse)
async def create_user(item: UserCreate, db: Session = Depends(get_db)):
    db_item = User(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get('/users/{user_id}', response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return user

@app.get('/users/login', response_model=UserResponse)
async def login_user(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).filter(User.password == password).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return user

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=8000)