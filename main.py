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

class UserLogin(BaseModel):
    username: str
    password: str

@app.post('/users/', response_model=UserResponse)
async def create_user(item: UserCreate, db: Session = Depends(get_db)):
    try:
        db_item = User(**item.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        output = UserResponse(id=db_item.id, name=db_item.username, email=db_item.email)
        return output
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@app.get('/users/{user_id}', response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail='User not found')
        output = UserResponse(id=user.id, name=user.username, email=user.email)
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading user: {str(e)}")

@app.get('/users/login/', response_model=UserResponse)
async def login_user(user:UserLogin, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == user.username).filter(User.password == user.password).first()
        if user is None:
            raise HTTPException(status_code=404, detail='User not found')
        output = UserResponse(id=user.id, name=user.username, email=user.email)
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging in user: {str(e)}")

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=8000)
