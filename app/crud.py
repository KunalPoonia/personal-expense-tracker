"""
CRUD operations for database models
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, extract
from app import models, schemas
from typing import List, Optional
from fastapi import HTTPException
from datetime import date, datetime
from calendar import monthrange


# ==================== CATEGORY CRUD ====================

def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    """Create a new category"""
    # Check for duplicate name
    existing = db.query(models.Category).filter(
        models.Category.name == category.name
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Category '{category.name}' already exists"
        )
    
    db_category = models.Category(**category.model_dump())
    try:
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")


def get_categories(db: Session) -> List[models.Category]:
    """Get all categories"""
    return db.query(models.Category).order_by(models.Category.type, models.Category.name).all()


def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    """Get category by ID"""
    return db.query(models.Category).filter(
        models.Category.category_id == category_id
    ).first()


def create_default_categories(db: Session) -> List[models.Category]:
    """Create default categories if none exist"""
    existing = db.query(models.Category).count()
    if existing > 0:
        return []
    
    default_categories = [
        # Income categories
        {"name": "Salary", "type": "INCOME"},
        {"name": "Freelance", "type": "INCOME"},
        {"name": "Investment", "type": "INCOME"},
        {"name": "Gift", "type": "INCOME"},
        {"name": "Other Income", "type": "INCOME"},
        # Expense categories
        {"name": "Food & Dining", "type": "EXPENSE"},
        {"name": "Transportation", "type": "EXPENSE"},
        {"name": "Utilities", "type": "EXPENSE"},
        {"name": "Rent", "type": "EXPENSE"},
        {"name": "Entertainment", "type": "EXPENSE"},
        {"name": "Shopping", "type": "EXPENSE"},
        {"name": "Healthcare", "type": "EXPENSE"},
        {"name": "Education", "type": "EXPENSE"},
        {"name": "Travel", "type": "EXPENSE"},
        {"name": "Other Expense", "type": "EXPENSE"},
    ]
    
    created = []
    for cat_data in default_categories:
        category = models.Category(**cat_data)
        db.add(category)
        created.append(category)
    
    db.commit()
    for cat in created:
        db.refresh(cat)
    
    return created


# ==================== TRANSACTION CRUD ====================

def create_transaction(db: Session, transaction: schemas.TransactionCreate) -> models.Transaction:
    """Create a new transaction"""
    # Verify category exists
    category = get_category(db, transaction.category_id)
    if not category:
        raise HTTPException(
            status_code=400,
            detail=f"Category with ID {transaction.category_id} not found"
        )
    
    db_transaction = models.Transaction(**transaction.model_dump())
    try:
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")


def get_transactions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None,
    transaction_type: Optional[str] = None
) -> List[models.Transaction]:
    """Get transactions with optional filters and pagination"""
    query = db.query(models.Transaction)
    
    if start_date:
        query = query.filter(models.Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.transaction_date <= end_date)
    if category_id:
        query = query.filter(models.Transaction.category_id == category_id)
    if transaction_type:
        query = query.filter(models.Transaction.type == transaction_type)
    
    return query.order_by(models.Transaction.transaction_date.desc()).offset(skip).limit(limit).all()


def get_transaction(db: Session, transaction_id: int) -> Optional[models.Transaction]:
    """Get transaction by ID"""
    return db.query(models.Transaction).filter(
        models.Transaction.transaction_id == transaction_id
    ).first()


def update_transaction(
    db: Session,
    transaction_id: int,
    transaction_update: schemas.TransactionUpdate
) -> models.Transaction:
    """Update transaction details"""
    db_transaction = get_transaction(db, transaction_id)
    
    if not db_transaction:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction with ID {transaction_id} not found"
        )
    
    update_data = transaction_update.model_dump(exclude_unset=True)
    
    # Verify category if being updated
    if 'category_id' in update_data:
        category = get_category(db, update_data['category_id'])
        if not category:
            raise HTTPException(
                status_code=400,
                detail=f"Category with ID {update_data['category_id']} not found"
            )
    
    for field, value in update_data.items():
        setattr(db_transaction, field, value)
    
    try:
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")


def delete_transaction(db: Session, transaction_id: int) -> bool:
    """Delete a transaction"""
    db_transaction = get_transaction(db, transaction_id)
    
    if not db_transaction:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction with ID {transaction_id} not found"
        )
    
    db.delete(db_transaction)
    db.commit()
    return True


# ==================== BUDGET CRUD ====================

def create_or_update_budget(db: Session, budget: schemas.BudgetCreate) -> models.Budget:
    """Create or update a budget for a category"""
    # Verify category exists and is expense type
    category = get_category(db, budget.category_id)
    if not category:
        raise HTTPException(
            status_code=400,
            detail=f"Category with ID {budget.category_id} not found"
        )
    if category.type != 'EXPENSE':
        raise HTTPException(
            status_code=400,
            detail="Budgets can only be set for expense categories"
        )
    
    # Check if budget already exists for this category
    existing = db.query(models.Budget).filter(
        models.Budget.category_id == budget.category_id
    ).first()
    
    if existing:
        # Update existing budget
        existing.amount = budget.amount
        existing.period = budget.period
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new budget
    db_budget = models.Budget(**budget.model_dump())
    try:
        db.add(db_budget)
        db.commit()
        db.refresh(db_budget)
        return db_budget
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")


def get_budgets_with_status(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[schemas.BudgetStatus]:
    """Get all budgets with spending status for a given date range"""
    budgets = db.query(models.Budget).all()
    result = []
    
    # Use provided dates or default to current month
    if start_date is None or end_date is None:
        today = date.today()
        start_date = start_date or date(today.year, today.month, 1)
        _, last_day = monthrange(today.year, today.month)
        end_date = end_date or date(today.year, today.month, last_day)
    
    for budget in budgets:
        category = get_category(db, budget.category_id)
        
        # Calculate spent amount for the given date range
        spent = db.query(func.sum(models.Transaction.amount)).filter(
            models.Transaction.category_id == budget.category_id,
            models.Transaction.transaction_date >= start_date,
            models.Transaction.transaction_date <= end_date
        ).scalar() or 0.0
        
        remaining = budget.amount - spent
        percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0
        
        result.append(schemas.BudgetStatus(
            budget_id=budget.budget_id,
            category_id=budget.category_id,
            category_name=category.name if category else "Unknown",
            budget_amount=budget.amount,
            spent_amount=round(spent, 2),
            remaining=round(remaining, 2),
            percentage_used=round(percentage, 1),
            is_over_budget=spent > budget.amount
        ))
    
    return result


# ==================== ANALYTICS FUNCTIONS ====================

def get_summary(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> schemas.SummaryResponse:
    """Get income vs expense summary"""
    query = db.query(models.Transaction)
    
    if start_date:
        query = query.filter(models.Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.transaction_date <= end_date)
    
    transactions = query.all()
    
    total_income = sum(t.amount for t in transactions if t.type == 'INCOME')
    total_expenses = sum(t.amount for t in transactions if t.type == 'EXPENSE')
    
    return schemas.SummaryResponse(
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        balance=round(total_income - total_expenses, 2),
        transaction_count=len(transactions)
    )


def get_category_breakdown(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    transaction_type: Optional[str] = None
) -> List[schemas.CategoryBreakdown]:
    """Get spending/income breakdown by category"""
    query = db.query(
        models.Transaction.category_id,
        models.Category.name,
        models.Category.type,
        func.sum(models.Transaction.amount).label('total'),
        func.count(models.Transaction.transaction_id).label('count')
    ).join(models.Category)
    
    if start_date:
        query = query.filter(models.Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.transaction_date <= end_date)
    if transaction_type:
        query = query.filter(models.Transaction.type == transaction_type)
    
    results = query.group_by(
        models.Transaction.category_id,
        models.Category.name,
        models.Category.type
    ).all()
    
    return [
        schemas.CategoryBreakdown(
            category_id=r[0],
            category_name=r[1],
            type=r[2],
            total_amount=round(r[3], 2),
            transaction_count=r[4]
        )
        for r in results
    ]


def get_monthly_trend(db: Session, months: int = 6) -> List[schemas.MonthlyTrend]:
    """Get monthly income vs expense trend"""
    today = date.today()
    results = []
    
    for i in range(months - 1, -1, -1):
        # Calculate month
        month = today.month - i
        year = today.year
        while month <= 0:
            month += 12
            year -= 1
        
        month_start = date(year, month, 1)
        _, last_day = monthrange(year, month)
        month_end = date(year, month, last_day)
        
        # Get transactions for this month
        transactions = db.query(models.Transaction).filter(
            models.Transaction.transaction_date >= month_start,
            models.Transaction.transaction_date <= month_end
        ).all()
        
        income = sum(t.amount for t in transactions if t.type == 'INCOME')
        expenses = sum(t.amount for t in transactions if t.type == 'EXPENSE')
        
        results.append(schemas.MonthlyTrend(
            month=month_start.strftime('%B'),
            year=year,
            income=round(income, 2),
            expenses=round(expenses, 2),
            balance=round(income - expenses, 2)
        ))
    
    return results


def get_balance(db: Session) -> schemas.BalanceResponse:
    """Get current balance (all-time)"""
    income = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.type == 'INCOME'
    ).scalar() or 0.0
    
    expenses = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.type == 'EXPENSE'
    ).scalar() or 0.0
    
    return schemas.BalanceResponse(
        balance=round(income - expenses, 2),
        total_income=round(income, 2),
        total_expenses=round(expenses, 2)
    )
