"""
Authentication and Security Module for GoalMate.
Handles password hashing with bcrypt, JWT token generation, and token validation.
"""
import os
import datetime
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from backend.database import get_db

load_dotenv()

# Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "goalmate_academic_hackathon_super_secret_jwt_key_2026_x99")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

# Password context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    """Hashes plain text password securely using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain text password against stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Any, email: Optional[str] = None, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Creates signed JWT token with payload and expiration."""
    if isinstance(data, dict):
        to_encode = data.copy()
    else:
        to_encode = {"sub": str(data), "email": email or ""}
    expire = datetime.datetime.now(datetime.timezone.utc) + (
        expires_delta or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.datetime.now(datetime.timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates signed JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except (JWTError, Exception):
        return None


def register_user(*args, **kwargs):
    """Registers a new user and returns (new_user, error_str). Supports multiple calling conventions."""
    db = None
    email = ""
    name = ""
    password = ""

    if len(args) == 4:
        # register_user(db, name, email, password)
        db, name, email, password = args
    elif len(args) == 3:
        # register_user(email, name, password)
        email, name, password = args
    elif len(args) == 2:
        # register_user(email, password)
        email, password = args
    
    email = kwargs.get("email", email)
    name = kwargs.get("name", name)
    password = kwargs.get("password", password)
    db = kwargs.get("db", db)

    close_db = False
    if db is None:
        from backend.services import get_session
        db = get_session()
        close_db = True

    try:
        from backend.models import User
        clean_email = email.lower().strip()
        existing = db.query(User).filter(User.email == clean_email).first()
        if existing:
            return None, "An account with this email already exists."
        new_user = User(
            name=name.strip() or clean_email.split('@')[0].capitalize(),
            email=clean_email,
            password_hash=hash_password(password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user, None
    except Exception as e:
        return None, str(e)
    finally:
        if close_db:
            db.close()


def authenticate_user(*args, **kwargs):
    """Verifies user email and password against hash. Supports (db, email, password) or (email, password)."""
    db = None
    email = ""
    password = ""

    if len(args) == 3:
        # authenticate_user(db, email, password)
        db, email, password = args
    elif len(args) == 2:
        # authenticate_user(email, password)
        email, password = args

    email = kwargs.get("email", email)
    password = kwargs.get("password", password)
    db = kwargs.get("db", db)

    close_db = False
    if db is None:
        from backend.services import get_session
        db = get_session()
        close_db = True

    try:
        from backend.models import User
        clean_email = email.lower().strip()
        user = db.query(User).filter(User.email == clean_email).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        return user
    finally:
        if close_db:
            db.close()



def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """FastAPI dependency for extracting authenticated user from JWT Bearer token."""
    from backend.models import User
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise credentials_exception
    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception
    return user
