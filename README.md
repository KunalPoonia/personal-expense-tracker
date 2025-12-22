# 💰 Personal Finance Tracker

A full-stack Personal Finance Tracker application built with FastAPI, PostgreSQL/SQLite, and Plotly Dash. Track your income, expenses, set budgets, and visualize your financial data through an interactive real-time dashboard.

---

## ✨ Features

### Backend (FastAPI)
- ✅ RESTful API endpoints for complete CRUD operations
- ✅ Transaction management (Income/Expense tracking)
- ✅ Category management with default categories
- ✅ Budget management with spending alerts
- ✅ Analytics endpoints for financial insights
- ✅ Automatic API documentation with Swagger UI
- ✅ Comprehensive error handling with proper HTTP status codes
- ✅ Input validation using Pydantic schemas

### Database (PostgreSQL/SQLite)
- ✅ Normalized relational schema design
- ✅ Three main tables: `categories`, `transactions`, `budgets`
- ✅ Foreign key constraints for referential integrity
- ✅ Check constraints for data validation
- ✅ Automatic timestamp tracking
- ✅ 60+ pre-populated sample records

### Dashboard (Plotly Dash)
- ✅ Interactive analytics dashboard
- ✅ Real-time data visualization (auto-refresh every 5 seconds)
- ✅ Four visualization types:
  - Pie Chart: Expense distribution by category
  - Bar Chart: Monthly income vs expenses
  - Line Chart: Balance trend over time
  - Data Table: Recent transactions
- ✅ Date range and category filters
- ✅ Budget status with progress bars
- ✅ Summary cards (Income, Expenses, Balance, Count)

---

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend Framework** | FastAPI | 0.109.0 |
| **Database** | PostgreSQL / SQLite | 12+ / 3 |
| **ORM** | SQLAlchemy | 2.0.25 |
| **Dashboard** | Plotly Dash | 2.14.2 |
| **Data Visualization** | Plotly | 5.18.0 |
| **Data Processing** | Pandas | 2.1.4 |
| **Validation** | Pydantic | 2.5.3 |
| **ASGI Server** | Uvicorn | 0.27.0 |
| **Language** | Python | 3.8+ |

---

## 📁 Project Structure

```
personal-finance-tracker/
│
├── app/                          # Backend application
│   ├── __init__.py
│   ├── main.py                   # FastAPI application & endpoints
│   ├── database.py               # Database configuration
│   ├── models.py                 # SQLAlchemy ORM models
│   ├── schemas.py                # Pydantic validation schemas
│   └── crud.py                   # Database operations
│
├── dashboard/                    # Analytics dashboard
│   ├── __init__.py
│   └── dash_app.py              # Plotly Dash application
│
├── scripts/                      # Utility scripts
│   ├── __init__.py
│   └── seed_data.py             # Database seeder
│
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
└── README.md                     # Project documentation
```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- PostgreSQL 12+ (optional, SQLite works by default)

### 1. Navigate to Project Directory
```bash
cd personal-finance-tracker
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment (Optional)
```bash
# Copy the example environment file
copy .env.example .env

# Edit .env for PostgreSQL (optional):
# DATABASE_URL=postgresql://username:password@localhost:5432/finance_db
```

### 5. Seed Sample Data
```bash
python scripts/seed_data.py
```

This will:
- Create all database tables
- Insert 15 default categories
- Generate 60+ sample transactions
- Create budgets for expense categories

---

## 🎯 Running the Application

### Start the Backend API

**Terminal 1:**
```bash
cd personal-finance-tracker
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API will be available at:**
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Start the Dashboard

**Terminal 2:**
```bash
cd personal-finance-tracker
python dashboard/dash_app.py
```

**Dashboard will be available at:**
- Dashboard: http://127.0.0.1:8050

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### **Categories**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/categories/` | Create a new category |
| GET | `/categories/` | List all categories |

#### **Transactions**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/transactions/` | Create a new transaction |
| GET | `/transactions/` | List transactions (with filters) |
| GET | `/transactions/{id}` | Get transaction by ID |
| PUT | `/transactions/{id}` | Update transaction |
| DELETE | `/transactions/{id}` | Delete transaction |

#### **Budgets**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/budgets/` | Create/update budget |
| GET | `/budgets/` | List budgets with status |

#### **Analytics**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/summary` | Income vs expense totals |
| GET | `/analytics/by-category` | Category breakdown |
| GET | `/analytics/monthly-trend` | Monthly trends |
| GET | `/analytics/balance` | Current balance |

---

## 📝 API Request Examples

### 1. Create a Transaction (Income)
```bash
curl -X POST "http://localhost:8000/transactions/" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50000,
    "type": "INCOME",
    "description": "Monthly salary",
    "transaction_date": "2024-12-20",
    "category_id": 1
  }'
```

### 2. Create a Transaction (Expense)
```bash
curl -X POST "http://localhost:8000/transactions/" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1500,
    "type": "EXPENSE",
    "description": "Grocery shopping",
    "transaction_date": "2024-12-20",
    "category_id": 6
  }'
```

### 3. Get All Transactions
```bash
curl -X GET "http://localhost:8000/transactions/"
```

### 4. Get Transactions with Filters
```bash
curl -X GET "http://localhost:8000/transactions/?start_date=2024-12-01&type=EXPENSE"
```

### 5. Update a Transaction
```bash
curl -X PUT "http://localhost:8000/transactions/1" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 55000,
    "description": "Updated salary"
  }'
```

### 6. Delete a Transaction
```bash
curl -X DELETE "http://localhost:8000/transactions/1"
```

### 7. Create a Budget
```bash
curl -X POST "http://localhost:8000/budgets/" \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 6,
    "amount": 10000,
    "period": "MONTHLY"
  }'
```

### 8. Get Analytics Summary
```bash
curl -X GET "http://localhost:8000/analytics/summary"
```

---

## 🎨 Dashboard Features

### Summary Cards
- **Total Income**: Sum of all income transactions
- **Total Expenses**: Sum of all expense transactions
- **Balance**: Income - Expenses
- **Transaction Count**: Number of transactions

### Visualizations

1. **Expense Pie Chart**
   - Shows expense distribution by category
   - Interactive hover for details
   - Donut style with legend

2. **Monthly Bar Chart**
   - Compares income vs expenses by month
   - Grouped bars for easy comparison
   - Color-coded (green=income, red=expense)

3. **Balance Line Chart**
   - Shows cumulative balance over time
   - Markers for each transaction
   - Zero line reference

4. **Budget Status**
   - Progress bars for each budget
   - Color-coded alerts (green/yellow/red)
   - Shows spent vs budget amount

5. **Recent Transactions Table**
   - Last 10 transactions
   - Color-coded by type
   - Sortable columns

### Filters
- **Date Range**: Filter by start and end date
- **Category**: Filter by specific category

---

## 🔍 Database Schema

### Categories Table
```sql
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('INCOME', 'EXPENSE')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    amount FLOAT NOT NULL CHECK (amount > 0),
    type VARCHAR(20) NOT NULL CHECK (type IN ('INCOME', 'EXPENSE')),
    description VARCHAR(255),
    transaction_date DATE NOT NULL,
    category_id INTEGER REFERENCES categories(category_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Budgets Table
```sql
CREATE TABLE budgets (
    budget_id SERIAL PRIMARY KEY,
    category_id INTEGER UNIQUE REFERENCES categories(category_id),
    amount FLOAT NOT NULL CHECK (amount > 0),
    period VARCHAR(20) DEFAULT 'MONTHLY',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🐛 Troubleshooting

### Issue: Module Not Found
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Database Connection Error
- Check DATABASE_URL in .env file
- For SQLite, ensure the path is correct
- For PostgreSQL, verify credentials and database exists

### Issue: Port Already in Use
```bash
# Change API port
uvicorn app.main:app --port 8001

# Change Dashboard port (edit dash_app.py)
app.run_server(port=8051)
```

### Issue: Dashboard Not Updating
- Ensure API server is running
- Check browser console for errors
- Verify database has data (run seed script)

---

## 🔄 Real-Time Update Demo

1. Open dashboard at http://127.0.0.1:8050
2. Open Swagger UI at http://localhost:8000/docs
3. Add a new transaction via API
4. Watch dashboard update automatically within 5 seconds!

---

## 📊 Default Categories

### Income Categories
- Salary, Freelance, Investment, Gift, Other Income

### Expense Categories
- Food & Dining, Transportation, Utilities, Rent
- Entertainment, Shopping, Healthcare, Education
- Travel, Other Expense

---

## 👨‍💻 Author

CA-2 Assignment | CSR210 | Advanced Programming and Database Systems

---

**Happy Tracking! 💰📊**
