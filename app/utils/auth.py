import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "verysecret"
ALGORITHM = "HS256"
EXPIRE_MINUTES = 3600

security = HTTPBearer()


def create_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        username = decode_token(token)
        if not username:
            raise HTTPException(status_code=403, detail="Invalid token")
        return username
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
