from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

# I'm reusing the same categories from my models
class ExpenseCategory(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    HEALTHCARE = "healthcare"
    SHOPPING = "shopping"
    EDUCATION = "education"
    OTHER = "other"

# User schemas
class UserBase(BaseModel):
    """Base schema with common user fields"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user - includes password"""
    password: str = Field(..., min_length=6)  # I'm requiring at least 6 characters

class UserUpdate(BaseModel):
    """Schema for updating user info - all fields optional"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)

class UserResponse(UserBase):
    """Schema for returning user data - never includes password"""
    id: int
    is_active: int
    created_at: datetime
    
    class Config:
        from_attributes = True  # This tells Pydantic to read data from SQLAlchemy models

# Expense schemas
class ExpenseBase(BaseModel):
    """Base schema with common expense fields"""
    title: str = Field(..., max_length=200)
    amount: float = Field(..., gt=0)  # Amount must be greater than 0
    category: ExpenseCategory
    description: Optional[str] = None
    date: Optional[datetime] = None

class ExpenseCreate(ExpenseBase):
    """Schema for creating a new expense"""
    pass  # Inherits everything from ExpenseBase

class ExpenseUpdate(BaseModel):
    """Schema for updating an expense - all fields optional"""
    title: Optional[str] = Field(None, max_length=200)
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = None
    date: Optional[datetime] = None

class ExpenseResponse(ExpenseBase):
    """Schema for returning expense data"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    ai_confidence: Optional[float] = None
    ai_suggested_category: Optional[str] = None
    
    class Config:
        from_attributes = True

# Budget schemas
class BudgetBase(BaseModel):
    """Base schema for budget"""
    category: ExpenseCategory
    amount: float = Field(..., gt=0)
    period: str = Field(default="monthly", pattern="^(monthly|weekly|yearly)$")

class BudgetCreate(BudgetBase):
    """Schema for creating a budget"""
    pass

class BudgetUpdate(BaseModel):
    """Schema for updating a budget"""
    category: Optional[ExpenseCategory] = None
    amount: Optional[float] = Field(None, gt=0)
    period: Optional[str] = Field(None, pattern="^(monthly|weekly|yearly)$")

class BudgetResponse(BudgetBase):
    """Schema for returning budget data"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Token schemas for authentication
class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for data stored in JWT token"""
    username: Optional[str] = None

# Login schema
class UserLogin(BaseModel):
    """Schema for login request"""
    username: str  # Can be username or email
    password: str

# Statistics schemas (for dashboard)
class ExpenseStatistics(BaseModel):
    """Schema for expense statistics"""
    total_expenses: float
    expense_count: int
    average_expense: float
    by_category: dict  # Will contain category: total_amount pairs
    
class MonthlyTrend(BaseModel):
    """Schema for monthly expense trends"""
    month: str
    total: float
    count: int