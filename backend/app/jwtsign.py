import time
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from config import JWT_SECRET, JWT_ALGORITHM

bearer = HTTPBearer()

def sign(email):
    payload = {
        "email": email,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    token = credentials.credentials
    try:
        decoded_token = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM]
        )
        return decoded_token
    except:
        raise HTTPException(status_code=401, detail="invalid token")