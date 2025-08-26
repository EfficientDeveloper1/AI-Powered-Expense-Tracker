from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from app.core.database import get_db
from app.core.security import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.core.dependencies import get_current_active_user
from app.models.models import User
from app.schemas.schemas import (
    UserCreate, 
    UserResponse, 
    Token, 
    UserLogin,
    UserUpdate
)

# Creating my auth router
router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    I'm creating a new user account.
    This checks for existing email/username and hashes the password.
    """
    # Checking if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Checking if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Creating new user with hashed password
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    # Saving to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # This gets the generated ID and default values
    
    return new_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    I'm handling user login.
    Users can login with either username or email.
    Returns a JWT token on successful authentication.
    """
    # Trying to find user by username first, then by email
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        # Maybe they used email instead of username
        user = db.query(User).filter(User.email == form_data.username).first()
    
    # Checking if user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Checking if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Creating access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    I'm returning the current user's profile.
    This requires authentication.
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    I'm updating the current user's profile.
    All fields are optional.
    """
    # Checking if new email is already taken (if email is being updated)
    if user_update.email and user_update.email != current_user.email:
        existing = db.query(User).filter(User.email == user_update.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
    
    # Checking if new username is already taken (if username is being updated)
    if user_update.username and user_update.username != current_user.username:
        existing = db.query(User).filter(User.username == user_update.username).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Updating user fields
    if user_update.email:
        current_user.email = user_update.email
    if user_update.username:
        current_user.username = user_update.username
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    if user_update.password:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    # Saving changes
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.post("/logout")
async def logout():
    """
    I'm handling logout.
    Since I'm using JWT tokens, I just return a success message.
    The client should remove the token from storage.
    """
    return {"message": "Successfully logged out"}

@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    I'm allowing users to delete their own account.
    This will also delete all their expenses (cascade delete).
    """
    db.delete(current_user)
    db.commit()
    
    return {"message": "Account deleted successfully"}