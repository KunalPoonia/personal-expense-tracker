"""
SQLAlchemy ORM models for database tables
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, CheckConstraint, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """
    User model for authentication
    """
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.user_id}, username='{self.username}')>"


class Category(Base):
    """
    Category model for organizing transactions
    """
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    type = Column(String(20), nullable=False)  # 'INCOME' or 'EXPENSE'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="category", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("type IN ('INCOME', 'EXPENSE')", name='check_category_type'),
    )

    def __repr__(self):
        return f"<Category(id={self.category_id}, name='{self.name}', type='{self.type}')>"


class Transaction(Base):
    """
    Transaction model for income and expense records
    """
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    type = Column(String(20), nullable=False)  # 'INCOME' or 'EXPENSE'
    description = Column(String(255))
    transaction_date = Column(Date, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    category = relationship("Category", back_populates="transactions")

    __table_args__ = (
        CheckConstraint('amount > 0', name='check_amount_positive'),
        CheckConstraint("type IN ('INCOME', 'EXPENSE')", name='check_transaction_type'),
    )

    def __repr__(self):
        return f"<Transaction(id={self.transaction_id}, amount={self.amount}, type='{self.type}')>"


class Budget(Base):
    """
    Budget model for setting spending limits per category
    """
    __tablename__ = "budgets"

    budget_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    period = Column(String(20), default='MONTHLY')  # 'MONTHLY', 'WEEKLY', 'YEARLY'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    category = relationship("Category", back_populates="budgets")

    __table_args__ = (
        CheckConstraint('amount > 0', name='check_budget_positive'),
    )

    def __repr__(self):
        return f"<Budget(id={self.budget_id}, category_id={self.category_id}, amount={self.amount})>"
