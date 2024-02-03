from fastapi import APIRouter, Depends, HTTPException, status
from ..dependencies import get_current_db, get_current_user
from ..models import User
from ..schemas import UserAuthSerializer, UserOutSerializer, TokenSerializer, UserLoginSerializer
from ..utils.auth import create_access_token, create_refresh_token, verify_password, get_hashed_password
import uuid
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing_extensions import Annotated


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post('/signup', summary="Create new user", response_model=UserOutSerializer)
async def create_user(data: UserAuthSerializer, db=Depends(get_current_db)):
    user = User(
        username=data.username,
        email=data.email,
        password=get_hashed_password(data.password),
        uuid=uuid.uuid4()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post('/login', summary="Login user", response_model=TokenSerializer)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db=Depends(get_current_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(form_data.username)
    refresh_token = create_refresh_token(form_data.username)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@router.get('/me', summary="Get current user", response_model=UserOutSerializer)
async def get_current_user(current_user: User = Depends(get_current_user)):
    return current_user
