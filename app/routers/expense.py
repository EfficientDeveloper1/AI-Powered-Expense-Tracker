from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.models import User, Expense, ExpenseCategory
from app.schemas.schemas import (
    ExpenseCreate, 
    ExpenseUpdate, 
    ExpenseResponse,
    ExpenseStatistics
)

# Creating my expenses router
router = APIRouter(
    prefix="/api/expenses",
    tags=["Expenses"]
)

@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    I'm creating a new expense for the authenticated user.
    """
    # Creating expense with the current user as owner
    new_expense = Expense(
        **expense_data.dict(),
        user_id=current_user.id
    )
    
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    
    return new_expense

@router.get("/", response_model=List[ExpenseResponse])
async def get_expenses(
    skip: int = Query(0, ge=0),  # For pagination
    limit: int = Query(100, ge=1, le=100),  # Max 100 items per page
    category: Optional[ExpenseCategory] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    I'm getting all expenses for the current user with optional filters.
    """
    # Starting with base query
    query = db.query(Expense).filter(Expense.user_id == current_user.id)
    
    # Applying filters if provided
    if category:
        query = query.filter(Expense.category == category)
    
    if start_date:
        query = query.filter(Expense.date >= start_date)
    
    if end_date:
        query = query.filter(Expense.date <= end_date)
    
    # Ordering by date (newest first) and applying pagination
    expenses = query.order_by(Expense.date.desc()).offset(skip).limit(limit).all()
    
    return expenses

@router.get("/statistics", response_model=ExpenseStatistics)
async def get_expense_statistics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    I'm calculating statistics for the user's expenses.
    """
    # Building base query
    query = db.query(Expense).filter(Expense.user_id == current_user.id)
    
    # Applying date filters
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
    
    expenses = query.all()
    
    # Calculating statistics
    if not expenses:
        return ExpenseStatistics(
            total_expenses=0,
            expense_count=0,
            average_expense=0,
            by_category={}
        )
    
    total = sum(e.amount for e in expenses)
    count = len(expenses)
    
    # Grouping by category
    by_category = {}
    for expense in expenses:
        category = expense.category.value
        if category not in by_category:
            by_category[category] = 0
        by_category[category] += expense.amount
    
    return ExpenseStatistics(
        total_expenses=total,
        expense_count=count,
        average_expense=total / count if count > 0 else 0,
        by_category=by_category
    )

@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    I'm getting a specific expense by ID.
    """
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id  # Ensuring user owns this expense
    ).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    return expense

@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    I'm updating an existing expense.
    """
    # Finding the expense
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    # Updating fields that were provided
    update_data = expense_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expense, field, value)
    
    # Updating the updated_at timestamp
    expense.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(expense)
    
    return expense

@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    I'm deleting an expense.
    """
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    db.delete(expense)
    db.commit()
    
    return {"message": "Expense deleted successfully"}

@router.get("/recent/week", response_model=List[ExpenseResponse])
async def get_week_expenses(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    I'm getting expenses from the last 7 days.
    """
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.date >= week_ago
    ).order_by(Expense.date.desc()).all()
    
    return expenses

@router.get("/recent/month", response_model=List[ExpenseResponse])
async def get_month_expenses(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    I'm getting expenses from the last 30 days.
    """
    month_ago = datetime.utcnow() - timedelta(days=30)
    
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.date >= month_ago
    ).order_by(Expense.date.desc()).all()
    
    return expenses