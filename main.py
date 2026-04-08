from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
import models, schemas, auth

Base.metadata.create_all(bind=engine)

app= FastAPI()

#Database Connection

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Register

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed = auth.hash_password(user.password)
    new_user = models.User(email=user.email, password=hashed)
    db.add(new_user)
    db.commit()
    return {"message" : "User created"}

#Login

@app.post("/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user or not auth.verify_password(user.passsword, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    token = auth.create_token({"user_id": db_user.id})
    return {"access_token":token}

