from fastapi import Depends, HTTPException, status

from .database import get_db
from .database import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from .utils.auth import (
    ALGORITHM,
    JWT_SECRET_KEY
)

from jose import jwt, JWTError
from pydantic import ValidationError
from .schemas import TokenSerializer, TokenPayloadSerializer
from datetime import datetime
from .models import User
from sqlalchemy.orm import Session

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/users/login",
    scheme_name="JWT"
)


def get_current_db(db: SessionLocal = Depends(get_db)):
    return db


async def get_current_user(token: str = Depends(reuseable_oauth), db: Session = Depends(get_current_db)) -> User:
    try:
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayloadSerializer(**payload)
    except(JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.username == token_data.sub).first()
    return user
