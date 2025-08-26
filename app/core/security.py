from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# Loading my environment variables
load_dotenv()

# Getting my security settings from environment
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Setting up password hashing context
# I'm using bcrypt for secure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    I'm verifying a plain password against a hashed password.
    Returns True if they match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    I'm creating a hash from a plain password.
    This is what I'll store in the database.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    I'm creating a JWT token with the provided data.
    If no expiration is provided, I'll use the default from settings.
    """
    # Making a copy so I don't modify the original data
    to_encode = data.copy()
    
    # Setting the expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Adding expiration to the token payload
    to_encode.update({"exp": expire})
    
    # Creating the actual JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    """
    I'm verifying and decoding a JWT token.
    If invalid, I'll raise the provided exception.
    """
    try:
        # Decoding the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # "sub" is standard JWT claim for subject
        
        if username is None:
            raise credentials_exception
            
        return username
    except JWTError:
        raise credentials_exception

def create_reset_password_token(email: str) -> str:
    """
    I'm creating a special token for password reset.
    This token expires in 1 hour for security.
    """
    data = {"sub": email, "type": "password_reset"}
    expires = timedelta(hours=1)
    return create_access_token(data, expires_delta=expires)

def verify_reset_token(token: str) -> Optional[str]:
    """
    I'm verifying a password reset token and returning the email if valid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None