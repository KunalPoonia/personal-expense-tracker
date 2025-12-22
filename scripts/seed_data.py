"""
Script to seed the database with sample data
Generates 50+ transactions over 90 days
"""
import sys
import os
from datetime import datetime, timedelta, date
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import Category, Transaction, Budget
from app import crud

# Sample data for transactions
INCOME_DESCRIPTIONS = {
    "Salary": ["Monthly salary", "Salary payment", "Paycheck deposit"],
    "Freelance": ["Web development project", "Design work", "Consulting fee", "Contract work"],
    "Investment": ["Dividend payment", "Stock sale", "Interest income", "Mutual fund returns"],
    "Gift": ["Birthday gift", "Holiday bonus", "Cash gift"],
    "Other Income": ["Refund received", "Cashback", "Lottery win", "Side hustle"],
}

EXPENSE_DESCRIPTIONS = {
    "Food & Dining": ["Grocery shopping", "Restaurant dinner", "Coffee shop", "Fast food", "Food delivery"],
    "Transportation": ["Fuel", "Bus fare", "Metro ticket", "Uber ride", "Car maintenance"],
    "Utilities": ["Electricity bill", "Water bill", "Internet bill", "Phone bill", "Gas bill"],
    "Rent": ["Monthly rent", "Rent payment"],
    "Entertainment": ["Movie tickets", "Netflix subscription", "Concert tickets", "Gaming"],
    "Shopping": ["Clothes shopping", "Electronics", "Home decor", "Amazon purchase"],
    "Healthcare": ["Doctor visit", "Medicine", "Health checkup", "Pharmacy"],
    "Education": ["Online course", "Books", "Tuition fee", "Workshop"],
    "Travel": ["Flight tickets", "Hotel booking", "Vacation expenses"],
    "Other Expense": ["Miscellaneous", "ATM withdrawal", "Bank fees"],
}

# Realistic amount ranges
INCOME_RANGES = {
    "Salary": (30000, 80000),
    "Freelance": (5000, 25000),
    "Investment": (1000, 10000),
    "Gift": (500, 5000),
    "Other Income": (100, 3000),
}

EXPENSE_RANGES = {
    "Food & Dining": (100, 3000),
    "Transportation": (200, 2000),
    "Utilities": (500, 3000),
    "Rent": (8000, 25000),
    "Entertainment": (200, 2000),
    "Shopping": (500, 5000),
    "Healthcare": (200, 5000),
    "Education": (500, 10000),
    "Travel": (2000, 20000),
    "Other Expense": (100, 1000),
}


def create_sample_transactions(db: Session, num_transactions: int = 60):
    """Create sample transactions"""
    categories = db.query(Category).all()
    income_cats = [c for c in categories if c.type == 'INCOME']
    expense_cats = [c for c in categories if c.type == 'EXPENSE']
    
    transactions = []
    start_date = datetime.now() - timedelta(days=90)
    
    # Create salary transactions (monthly)
    salary_cat = next((c for c in income_cats if c.name == "Salary"), income_cats[0])
    for month_offset in range(3):
        salary_date = start_date + timedelta(days=month_offset * 30 + 1)
        amount = random.uniform(*INCOME_RANGES["Salary"])
        transactions.append(Transaction(
            amount=round(amount, 2),
            type="INCOME",
            description="Monthly salary",
            transaction_date=salary_date.date(),
            category_id=salary_cat.category_id
        ))
    
    # Create rent transactions (monthly)
    rent_cat = next((c for c in expense_cats if c.name == "Rent"), expense_cats[0])
    for month_offset in range(3):
        rent_date = start_date + timedelta(days=month_offset * 30 + 5)
        amount = random.uniform(*EXPENSE_RANGES["Rent"])
        transactions.append(Transaction(
            amount=round(amount, 2),
            type="EXPENSE",
            description="Monthly rent",
            transaction_date=rent_date.date(),
            category_id=rent_cat.category_id
        ))
    
    # Create random transactions
    remaining = num_transactions - len(transactions)
    for _ in range(remaining):
        # 30% income, 70% expense
        if random.random() < 0.3:
            category = random.choice(income_cats)
            trans_type = "INCOME"
            descriptions = INCOME_DESCRIPTIONS.get(category.name, ["Income"])
            amount_range = INCOME_RANGES.get(category.name, (1000, 10000))
        else:
            category = random.choice(expense_cats)
            trans_type = "EXPENSE"
            descriptions = EXPENSE_DESCRIPTIONS.get(category.name, ["Expense"])
            amount_range = EXPENSE_RANGES.get(category.name, (100, 1000))
        
        days_offset = random.randint(0, 90)
        trans_date = start_date + timedelta(days=days_offset)
        amount = random.uniform(*amount_range)
        
        transactions.append(Transaction(
            amount=round(amount, 2),
            type=trans_type,
            description=random.choice(descriptions),
            transaction_date=trans_date.date(),
            category_id=category.category_id
        ))
    
    db.add_all(transactions)
    db.commit()
    print(f"✓ Created {len(transactions)} sample transactions")
    return transactions


def create_sample_budgets(db: Session):
    """Create sample budgets for expense categories"""
    expense_cats = db.query(Category).filter(Category.type == 'EXPENSE').all()
    
    budgets = []
    budget_amounts = {
        "Food & Dining": 8000,
        "Transportation": 3000,
        "Utilities": 5000,
        "Rent": 25000,
        "Entertainment": 3000,
        "Shopping": 5000,
        "Healthcare": 3000,
        "Education": 5000,
        "Travel": 10000,
        "Other Expense": 2000,
    }
    
    for cat in expense_cats:
        amount = budget_amounts.get(cat.name, 5000)
        budget = Budget(
            category_id=cat.category_id,
            amount=amount,
            period='MONTHLY'
        )
        budgets.append(budget)
    
    db.add_all(budgets)
    db.commit()
    print(f"✓ Created {len(budgets)} sample budgets")


def seed_database():
    """Main function to seed the database"""
    print("=" * 60)
    print("Personal Finance Tracker - Database Seeder")
    print("=" * 60)
    
    # Initialize database
    print("\n1. Initializing database...")
    init_db()
    print("✓ Database initialized")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing = db.query(Transaction).count()
        if existing > 0:
            response = input(f"\nDatabase has {existing} transactions. Clear and reseed? (yes/no): ")
            if response.lower() != 'yes':
                print("Seeding cancelled.")
                return
            
            print("\n2. Clearing existing data...")
            db.query(Budget).delete()
            db.query(Transaction).delete()
            db.query(Category).delete()
            db.commit()
            print("✓ Existing data cleared")
        
        # Create default categories
        print("\n3. Creating default categories...")
        crud.create_default_categories(db)
        categories = db.query(Category).all()
        print(f"✓ Created {len(categories)} categories")
        
        # Create sample transactions
        print("\n4. Creating sample transactions...")
        transactions = create_sample_transactions(db, num_transactions=60)
        
        # Create sample budgets
        print("\n5. Creating sample budgets...")
        create_sample_budgets(db)
        
        # Display summary
        print("\n" + "=" * 60)
        print("DATABASE SEEDING COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        total_trans = db.query(Transaction).count()
        income_count = db.query(Transaction).filter(Transaction.type == 'INCOME').count()
        expense_count = db.query(Transaction).filter(Transaction.type == 'EXPENSE').count()
        
        from sqlalchemy import func
        total_income = db.query(func.sum(Transaction.amount)).filter(
            Transaction.type == 'INCOME'
        ).scalar() or 0
        total_expense = db.query(func.sum(Transaction.amount)).filter(
            Transaction.type == 'EXPENSE'
        ).scalar() or 0
        
        print(f"\n📊 Summary:")
        print(f"   Total Transactions: {total_trans}")
        print(f"   Income Transactions: {income_count}")
        print(f"   Expense Transactions: {expense_count}")
        print(f"   Total Income: ₹{total_income:,.2f}")
        print(f"   Total Expenses: ₹{total_expense:,.2f}")
        print(f"   Balance: ₹{total_income - total_expense:,.2f}")
        
        print("\n📁 Categories:")
        for cat in categories:
            count = db.query(Transaction).filter(
                Transaction.category_id == cat.category_id
            ).count()
            print(f"   • {cat.name} ({cat.type}): {count} transactions")
        
        print("\n" + "=" * 60)
        print("You can now start the API and Dashboard!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
