from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import bcrypt

import db.mongo
from sentiment import sentiment_analysis
from jwtsign import sign, decode
from schemas import signupschema, signinschema, analysisschema


app = FastAPI()
ORIGINS = ["http://localhost:8501"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the MoodLens"}

@app.post("/signup")
def sign_up(request: signupschema):
    existing_user = db.mongo.get_user(request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt())
    user = {
        "name": request.name,
        "email": request.email,
        "password": hashed_password.decode('utf-8')
    }
    db.mongo.add_user(user)
    token = sign(request.email)
    return {"token": token}

@app.post("/signin")
def sign_in(request: signinschema):
    user = db.mongo.get_user(request.email)
    password_valid = bcrypt.checkpw(
        request.password.encode('utf-8'), 
        user['password'].encode('utf-8')
    )
    if not user:
        raise HTTPException(status_code=400, detail="Email not registered")
    
    if not password_valid:
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    token = sign(user['email'])
    return {"token": token}

@app.post("/authtest")
def auth_test(decoded: dict = Depends(decode)):
    return decoded            

@app.post("/analysis")
def analyze_text(request: analysisschema, decoded: dict = Depends(decode)):
    try:
        sentiment_result = sentiment_analysis(request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")
    data = {
        "email": decoded["email"],
        "text": request.text,
        "sentiment": sentiment_result
    }
    db.mongo.add_data(data)
    return {"text": request.text, "sentiment": sentiment_result}

@app.get("/history")
def get_history(decoded: dict = Depends(decode)):
    user_data = db.mongo.get_data({"email": decoded["email"]})
    return user_data