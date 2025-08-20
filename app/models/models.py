from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum

# I'm creating an enum for expense categories to keep them consistent
class ExpenseCategory(str, enum.Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    HEALTHCARE = "healthcare"
    SHOPPING = "shopping"
    EDUCATION = "education"
    OTHER = "other"

class User(Base):
    """My User model for authentication and linking expenses to users"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Integer, default=1)  # Using Integer since MySQL doesn't have native boolean
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Setting up relationship - one user can have many expenses
    expenses = relationship("Expense", back_populates="owner", cascade="all, delete-orphan")

class Expense(Base):
    """My Expense model for tracking individual expenses"""
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(Enum(ExpenseCategory), nullable=False)
    description = Column(Text)
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Linking each expense to a user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Creating the relationship back to user
    owner = relationship("User", back_populates="expenses")
    
    # Adding AI fields for when I implement AI categorization
    ai_confidence = Column(Float)  # I'll store how confident the AI was
    ai_suggested_category = Column(String(50))  # I'll store what the AI suggested

class Budget(Base):
    """My Budget model for setting spending limits per category"""
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(Enum(ExpenseCategory), nullable=False)
    amount = Column(Float, nullable=False)
    period = Column(String(20), default="monthly")  # I'll support monthly, weekly, yearly
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Linking budget to user
    owner = relationship("User")