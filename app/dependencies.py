from fastapi import Depends

from .database import get_db
from .database import SessionLocal


def get_current_db(db: SessionLocal = Depends(get_db)):
    return db
