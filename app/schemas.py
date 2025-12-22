"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime, date
from typing import Optional, Literal, List


# ==================== AUTH SCHEMAS ====================

class UserCreate(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class UserResponse(BaseModel):
    """Schema for user response"""
    user_id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Schema for token payload"""
    username: Optional[str] = None


# ==================== CATEGORY SCHEMAS ====================

class CategoryBase(BaseModel):
    """Base schema for category data"""
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    type: Literal['INCOME', 'EXPENSE'] = Field(..., description="Category type")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""
    pass


class Category(CategoryBase):
    """Schema for category response"""
    category_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== TRANSACTION SCHEMAS ====================

class TransactionBase(BaseModel):
    """Base schema for transaction data"""
    amount: float = Field(..., gt=0, description="Transaction amount (must be positive)")
    type: Literal['INCOME', 'EXPENSE'] = Field(..., description="Transaction type")
    description: Optional[str] = Field(None, max_length=255, description="Transaction description")
    transaction_date: date = Field(..., description="Date of transaction")
    category_id: int = Field(..., description="Category ID")


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction"""
    pass


class TransactionUpdate(BaseModel):
    """Schema for updating transaction (all fields optional)"""
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[Literal['INCOME', 'EXPENSE']] = None
    description: Optional[str] = Field(None, max_length=255)
    transaction_date: Optional[date] = None
    category_id: Optional[int] = None


class Transaction(TransactionBase):
    """Schema for transaction response"""
    transaction_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionWithCategory(Transaction):
    """Schema for transaction with category details"""
    category: Category


# ==================== BUDGET SCHEMAS ====================

class BudgetBase(BaseModel):
    """Base schema for budget data"""
    category_id: int = Field(..., description="Category ID")
    amount: float = Field(..., gt=0, description="Budget amount")
    period: str = Field(default='MONTHLY', description="Budget period")


class BudgetCreate(BudgetBase):
    """Schema for creating a new budget"""
    pass


class Budget(BudgetBase):
    """Schema for budget response"""
    budget_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BudgetStatus(BaseModel):
    """Schema for budget status with spending info"""
    budget_id: int
    category_id: int
    category_name: str
    budget_amount: float
    spent_amount: float
    remaining: float
    percentage_used: float
    is_over_budget: bool


# ==================== ANALYTICS SCHEMAS ====================

class SummaryResponse(BaseModel):
    """Schema for income/expense summary"""
    total_income: float
    total_expenses: float
    balance: float
    transaction_count: int


class CategoryBreakdown(BaseModel):
    """Schema for category breakdown item"""
    category_id: int
    category_name: str
    type: str
    total_amount: float
    transaction_count: int


class MonthlyTrend(BaseModel):
    """Schema for monthly trend item"""
    month: str
    year: int
    income: float
    expenses: float
    balance: float


class BalanceResponse(BaseModel):
    """Schema for balance response"""
    balance: float
    total_income: float
    total_expenses: float


# ==================== COMMON SCHEMAS ====================

class MessageResponse(BaseModel):
    """Standard message response"""
    message: str
    detail: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None
