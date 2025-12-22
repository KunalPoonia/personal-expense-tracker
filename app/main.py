"""
FastAPI application main file - Personal Finance Tracker
"""
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
from app import models, schemas, crud, auth
from app.database import get_db, init_db

# Initialize database tables
init_db()

# Create FastAPI app
app = FastAPI(
    title="Personal Finance Tracker API",
    description="RESTful API for managing personal income and expenses with JWT authentication",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for dashboard integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize default categories on startup"""
    db = next(get_db())
    try:
        crud.create_default_categories(db)
    finally:
        db.close()


@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint with API information"""
    return {
        "message": "Personal Finance Tracker API",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth/",
            "categories": "/categories/",
            "transactions": "/transactions/",
            "budgets": "/budgets/",
            "analytics": "/analytics/"
        }
    }


# ==================== AUTH ENDPOINTS ====================

@app.post(
    "/auth/register",
    response_model=schemas.Token,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"]
)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - **username**: Unique username (3-50 characters)
    - **email**: Valid email address
    - **password**: Password (min 6 characters)
    - **full_name**: Optional full name
    """
    user = auth.create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserResponse.model_validate(user)
    )


@app.post(
    "/auth/login",
    response_model=schemas.Token,
    tags=["Authentication"]
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login with username and password (OAuth2 compatible)
    
    Returns JWT access token
    """
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserResponse.model_validate(user)
    )


@app.post(
    "/auth/login/json",
    response_model=schemas.Token,
    tags=["Authentication"]
)
def login_json(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Login with JSON body (alternative to OAuth2 form)
    
    Returns JWT access token
    """
    user = auth.authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserResponse.model_validate(user)
    )


@app.get(
    "/auth/me",
    response_model=schemas.UserResponse,
    tags=["Authentication"]
)
def get_current_user_info(current_user: models.User = Depends(auth.get_current_user_required)):
    """Get current logged in user information (requires authentication)"""
    return current_user


@app.get(
    "/auth/verify",
    tags=["Authentication"]
)
def verify_token(current_user: models.User = Depends(auth.get_current_user)):
    """Verify if token is valid"""
    if current_user:
        return {"valid": True, "username": current_user.username}
    return {"valid": False, "username": None}


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Check if API and database are healthy"""
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )


# ==================== CATEGORY ENDPOINTS ====================

@app.post(
    "/categories/",
    response_model=schemas.Category,
    status_code=status.HTTP_201_CREATED,
    tags=["Categories"]
)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    """
    Create a new category
    
    - **name**: Category name (unique, required)
    - **type**: Either 'INCOME' or 'EXPENSE'
    """
    return crud.create_category(db=db, category=category)


@app.get(
    "/categories/",
    response_model=List[schemas.Category],
    tags=["Categories"]
)
def get_categories(db: Session = Depends(get_db)):
    """Retrieve all categories"""
    return crud.get_categories(db=db)


# ==================== TRANSACTION ENDPOINTS ====================

@app.post(
    "/transactions/",
    response_model=schemas.Transaction,
    status_code=status.HTTP_201_CREATED,
    tags=["Transactions"]
)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new transaction
    
    - **amount**: Transaction amount (must be > 0)
    - **type**: Either 'INCOME' or 'EXPENSE'
    - **description**: Optional description
    - **transaction_date**: Date of transaction (YYYY-MM-DD)
    - **category_id**: ID of the category
    """
    return crud.create_transaction(db=db, transaction=transaction)


@app.get(
    "/transactions/",
    response_model=List[schemas.Transaction],
    tags=["Transactions"]
)
def get_transactions(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    type: Optional[str] = Query(None, description="Filter by type (INCOME/EXPENSE)"),
    db: Session = Depends(get_db)
):
    """Retrieve transactions with optional filters and pagination"""
    return crud.get_transactions(
        db=db,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        transaction_type=type
    )


@app.get(
    "/transactions/{transaction_id}",
    response_model=schemas.Transaction,
    tags=["Transactions"]
)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific transaction by ID"""
    transaction = crud.get_transaction(db=db, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found"
        )
    return transaction


@app.put(
    "/transactions/{transaction_id}",
    response_model=schemas.Transaction,
    tags=["Transactions"]
)
def update_transaction(
    transaction_id: int,
    transaction_update: schemas.TransactionUpdate,
    db: Session = Depends(get_db)
):
    """Update transaction details (partial update supported)"""
    return crud.update_transaction(
        db=db,
        transaction_id=transaction_id,
        transaction_update=transaction_update
    )


@app.delete(
    "/transactions/{transaction_id}",
    response_model=schemas.MessageResponse,
    tags=["Transactions"]
)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Delete a transaction"""
    crud.delete_transaction(db=db, transaction_id=transaction_id)
    return {
        "message": f"Transaction with ID {transaction_id} successfully deleted",
        "detail": {"transaction_id": transaction_id}
    }


# ==================== BUDGET ENDPOINTS ====================

@app.post(
    "/budgets/",
    response_model=schemas.Budget,
    status_code=status.HTTP_201_CREATED,
    tags=["Budgets"]
)
def create_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db)):
    """
    Create or update a budget for a category
    
    - **category_id**: ID of expense category
    - **amount**: Budget limit (must be > 0)
    - **period**: Budget period (default: MONTHLY)
    """
    return crud.create_or_update_budget(db=db, budget=budget)


@app.get(
    "/budgets/",
    response_model=List[schemas.BudgetStatus],
    tags=["Budgets"]
)
def get_budgets(
    start_date: Optional[date] = Query(None, description="Filter from date (default: current month start)"),
    end_date: Optional[date] = Query(None, description="Filter to date (default: current month end)"),
    db: Session = Depends(get_db)
):
    """Retrieve all budgets with spending status for given date range"""
    return crud.get_budgets_with_status(db=db, start_date=start_date, end_date=end_date)


# ==================== ANALYTICS ENDPOINTS ====================

@app.get(
    "/analytics/summary",
    response_model=schemas.SummaryResponse,
    tags=["Analytics"]
)
def get_summary(
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db)
):
    """Get income vs expense summary for a period"""
    return crud.get_summary(db=db, start_date=start_date, end_date=end_date)


@app.get(
    "/analytics/by-category",
    response_model=List[schemas.CategoryBreakdown],
    tags=["Analytics"]
)
def get_category_breakdown(
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    type: Optional[str] = Query(None, description="Filter by type (INCOME/EXPENSE)"),
    db: Session = Depends(get_db)
):
    """Get spending/income breakdown by category"""
    return crud.get_category_breakdown(
        db=db,
        start_date=start_date,
        end_date=end_date,
        transaction_type=type
    )


@app.get(
    "/analytics/monthly-trend",
    response_model=List[schemas.MonthlyTrend],
    tags=["Analytics"]
)
def get_monthly_trend(
    months: int = Query(6, ge=1, le=24, description="Number of months"),
    db: Session = Depends(get_db)
):
    """Get monthly income vs expense trend"""
    return crud.get_monthly_trend(db=db, months=months)


@app.get(
    "/analytics/balance",
    response_model=schemas.BalanceResponse,
    tags=["Analytics"]
)
def get_balance(db: Session = Depends(get_db)):
    """Get current balance (all-time)"""
    return crud.get_balance(db=db)
