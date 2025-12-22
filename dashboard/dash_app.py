"""
Enhanced Interactive Dashboard using Plotly Dash
Features: JWT Authentication, CRUD Operations, API Integration
"""
import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context, ALL
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import httpx
import os
from datetime import datetime, date, timedelta
import json

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Initialize Dash app
app = dash.Dash(
    __name__,
    title="Personal Finance Tracker",
    update_title="Updating...",
    suppress_callback_exceptions=True
)

# Color scheme
COLORS = {
    'income': '#2ecc71',
    'expense': '#e74c3c',
    'balance': '#3498db',
    'background': '#f5f7fa',
    'card': '#ffffff',
    'text': '#2c3e50',
    'muted': '#7f8c8d',
    'primary': '#3498db',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c'
}


# ==================== API HELPER FUNCTIONS ====================

def api_request(method: str, endpoint: str, token: str = None, data: dict = None, params: dict = None):
    """Make API request with optional authentication"""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        with httpx.Client(timeout=10.0) as client:
            if method == "GET":
                response = client.get(url, headers=headers, params=params)
            elif method == "POST":
                response = client.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = client.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = client.delete(url, headers=headers)
            else:
                return None, "Invalid method"
            
            if response.status_code in [200, 201]:
                return response.json(), None
            else:
                error_detail = response.json().get("detail", response.text) if response.text else "Unknown error"
                return None, error_detail
    except httpx.RequestError as e:
        return None, f"Connection error: {str(e)}"
    except Exception as e:
        return None, str(e)


def fetch_transactions_api(token: str = None, start_date: str = None, end_date: str = None, category_id: int = None):
    """Fetch transactions from API"""
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    if category_id:
        params["category_id"] = category_id
    params["limit"] = 1000
    
    data, error = api_request("GET", "/transactions/", token, params=params)
    if error:
        return pd.DataFrame()
    return pd.DataFrame(data) if data else pd.DataFrame()


def fetch_categories_api(token: str = None):
    """Fetch categories from API"""
    data, error = api_request("GET", "/categories/", token)
    if error:
        return pd.DataFrame()
    return pd.DataFrame(data) if data else pd.DataFrame()


def fetch_budgets_api(token: str = None, start_date: str = None, end_date: str = None):
    """Fetch budgets with status from API"""
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    data, error = api_request("GET", "/budgets/", token, params=params)
    if error:
        return pd.DataFrame()
    return pd.DataFrame(data) if data else pd.DataFrame()


def fetch_summary_api(token: str = None, start_date: str = None, end_date: str = None):
    """Fetch summary analytics from API"""
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    
    data, error = api_request("GET", "/analytics/summary", token, params=params)
    return data if data else {"total_income": 0, "total_expenses": 0, "balance": 0, "transaction_count": 0}


# ==================== LAYOUT COMPONENTS ====================

def create_login_layout():
    """Create login/register layout"""
    return html.Div([
        html.Div([
            html.H1("💰 Personal Finance Tracker", style={'textAlign': 'center', 'color': COLORS['text']}),
            html.P("Please login or register to continue", style={'textAlign': 'center', 'color': COLORS['muted']}),
            
            # Login Form
            html.Div([
                html.H3("Login", style={'marginBottom': '20px', 'color': COLORS['text']}),
                
                dcc.Input(
                    id='login-username',
                    type='text',
                    placeholder='Username',
                    style={'width': '100%', 'padding': '12px', 'marginBottom': '15px', 
                           'border': '1px solid #ddd', 'borderRadius': '4px', 'fontSize': '14px'}
                ),
                dcc.Input(
                    id='login-password',
                    type='password',
                    placeholder='Password',
                    style={'width': '100%', 'padding': '12px', 'marginBottom': '15px',
                           'border': '1px solid #ddd', 'borderRadius': '4px', 'fontSize': '14px'}
                ),
                html.Button(
                    'Login',
                    id='login-button',
                    style={'width': '100%', 'padding': '12px', 'backgroundColor': COLORS['primary'],
                           'color': 'white', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer',
                           'fontSize': '16px', 'fontWeight': 'bold'}
                ),
                html.Div(id='login-error', style={'color': COLORS['danger'], 'marginTop': '10px', 'textAlign': 'center'})
            ], style={'marginBottom': '30px'}),
            
            html.Hr(style={'margin': '20px 0'}),
            
            # Register Form
            html.Div([
                html.H3("Register New Account", style={'marginBottom': '20px', 'color': COLORS['text']}),
                
                dcc.Input(
                    id='register-username',
                    type='text',
                    placeholder='Username',
                    style={'width': '100%', 'padding': '12px', 'marginBottom': '15px',
                           'border': '1px solid #ddd', 'borderRadius': '4px', 'fontSize': '14px'}
                ),
                dcc.Input(
                    id='register-email',
                    type='email',
                    placeholder='Email',
                    style={'width': '100%', 'padding': '12px', 'marginBottom': '15px',
                           'border': '1px solid #ddd', 'borderRadius': '4px', 'fontSize': '14px'}
                ),
                dcc.Input(
                    id='register-fullname',
                    type='text',
                    placeholder='Full Name (optional)',
                    style={'width': '100%', 'padding': '12px', 'marginBottom': '15px',
                           'border': '1px solid #ddd', 'borderRadius': '4px', 'fontSize': '14px'}
                ),
                dcc.Input(
                    id='register-password',
                    type='password',
                    placeholder='Password (min 6 characters)',
                    style={'width': '100%', 'padding': '12px', 'marginBottom': '15px',
                           'border': '1px solid #ddd', 'borderRadius': '4px', 'fontSize': '14px'}
                ),
                html.Button(
                    'Register',
                    id='register-button',
                    style={'width': '100%', 'padding': '12px', 'backgroundColor': COLORS['success'],
                           'color': 'white', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer',
                           'fontSize': '16px', 'fontWeight': 'bold'}
                ),
                html.Div(id='register-error', style={'color': COLORS['danger'], 'marginTop': '10px', 'textAlign': 'center'}),
                html.Div(id='register-success', style={'color': COLORS['success'], 'marginTop': '10px', 'textAlign': 'center'})
            ])
        ], style={'maxWidth': '400px', 'margin': '50px auto', 'padding': '40px',
                  'backgroundColor': COLORS['card'], 'borderRadius': '8px',
                  'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
    ], style={'backgroundColor': COLORS['background'], 'minHeight': '100vh', 'padding': '20px'})


def create_dashboard_layout():
    """Create main dashboard layout"""
    return html.Div([
        # Header with user info and logout
        html.Div([
            html.Div([
                html.H1("💰 Personal Finance Tracker",
                        style={'display': 'inline-block', 'color': COLORS['text'], 'margin': 0}),
            ], style={'display': 'inline-block'}),
            html.Div([
                html.Span(id='user-display', style={'marginRight': '15px', 'color': COLORS['text']}),
                html.Button('Logout', id='logout-button',
                           style={'padding': '8px 20px', 'backgroundColor': COLORS['danger'],
                                  'color': 'white', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'})
            ], style={'display': 'inline-block', 'float': 'right', 'marginTop': '10px'})
        ], style={'backgroundColor': COLORS['card'], 'padding': '20px', 'marginBottom': '20px',
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        # Tab Navigation
        dcc.Tabs(id='main-tabs', value='dashboard', children=[
            dcc.Tab(label='📊 Dashboard', value='dashboard'),
            dcc.Tab(label='💳 Transactions', value='transactions'),
            dcc.Tab(label='📁 Categories', value='categories'),
            dcc.Tab(label='💰 Budgets', value='budgets'),
        ], style={'marginBottom': '20px'}),
        
        # Tab Content
        html.Div(id='tab-content'),
        
        # Hidden stores for data
        dcc.Store(id='refresh-trigger', data=0),
        
        # Auto-refresh interval (10 seconds)
        dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0)
        
    ], style={'backgroundColor': COLORS['background'], 'minHeight': '100vh',
              'fontFamily': 'Arial, sans-serif', 'paddingBottom': '20px'})


def create_dashboard_tab():
    """Create dashboard tab content"""
    return html.Div([
        # Filters Row
        html.Div([
            html.Div([
                html.Label("Date Range:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                dcc.DatePickerRange(
                    id='date-range',
                    start_date=date.today() - timedelta(days=90),
                    end_date=date.today(),
                    display_format='DD/MM/YYYY'
                ),
            ], style={'display': 'inline-block', 'marginRight': '30px'}),
            html.Div([
                html.Label("Category:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                dcc.Dropdown(
                    id='category-filter',
                    placeholder="All Categories",
                    style={'width': '200px'}
                ),
            ], style={'display': 'inline-block'}),
        ], style={'padding': '15px 20px', 'backgroundColor': COLORS['card'],
                  'marginBottom': '20px', 'borderRadius': '8px',
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        # Summary Cards
        html.Div([
            html.Div([
                html.H4("Total Income", style={'color': COLORS['muted'], 'margin': 0, 'fontSize': 14}),
                html.H2(id='total-income', children='₹0',
                       style={'color': COLORS['income'], 'margin': '10px 0 0 0'})
            ], style={'flex': 1, 'padding': '20px', 'textAlign': 'center',
                      'backgroundColor': COLORS['card'], 'borderRadius': '8px',
                      'margin': '0 10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                      'borderLeft': f'4px solid {COLORS["income"]}'}),
            
            html.Div([
                html.H4("Total Expenses", style={'color': COLORS['muted'], 'margin': 0, 'fontSize': 14}),
                html.H2(id='total-expenses', children='₹0',
                       style={'color': COLORS['expense'], 'margin': '10px 0 0 0'})
            ], style={'flex': 1, 'padding': '20px', 'textAlign': 'center',
                      'backgroundColor': COLORS['card'], 'borderRadius': '8px',
                      'margin': '0 10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                      'borderLeft': f'4px solid {COLORS["expense"]}'}),
            
            html.Div([
                html.H4("Balance", style={'color': COLORS['muted'], 'margin': 0, 'fontSize': 14}),
                html.H2(id='balance', children='₹0',
                       style={'color': COLORS['balance'], 'margin': '10px 0 0 0'})
            ], style={'flex': 1, 'padding': '20px', 'textAlign': 'center',
                      'backgroundColor': COLORS['card'], 'borderRadius': '8px',
                      'margin': '0 10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                      'borderLeft': f'4px solid {COLORS["balance"]}'}),
            
            html.Div([
                html.H4("Transactions", style={'color': COLORS['muted'], 'margin': 0, 'fontSize': 14}),
                html.H2(id='transaction-count', children='0',
                       style={'color': COLORS['text'], 'margin': '10px 0 0 0'})
            ], style={'flex': 1, 'padding': '20px', 'textAlign': 'center',
                      'backgroundColor': COLORS['card'], 'borderRadius': '8px',
                      'margin': '0 10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                      'borderLeft': f'4px solid {COLORS["text"]}'}),
        ], style={'display': 'flex', 'marginBottom': '20px', 'padding': '0 10px'}),
        
        # Selected Category Info Card
        html.Div(id='selected-category-info', style={'padding': '0 20px', 'marginBottom': '20px'}),
        
        # Charts Row 1
        html.Div([
            html.Div([dcc.Graph(id='expense-pie-chart')], style={'flex': 1, 'padding': '0 10px'}),
            html.Div([dcc.Graph(id='monthly-bar-chart')], style={'flex': 1, 'padding': '0 10px'}),
        ], style={'display': 'flex', 'marginBottom': '20px'}),
        
        # Charts Row 2
        html.Div([dcc.Graph(id='balance-line-chart')], style={'padding': '0 20px', 'marginBottom': '20px'}),
        
        # Budget Status
        html.Div([
            html.H3("📊 Budget Status", style={'color': COLORS['text'], 'marginBottom': '15px'}),
            html.Div(id='budget-status')
        ], style={'padding': '20px', 'backgroundColor': COLORS['card'], 'borderRadius': '8px',
                  'margin': '0 20px 20px 20px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        # Recent Transactions
        html.Div([
            html.H3("📝 Recent Transactions", style={'color': COLORS['text'], 'marginBottom': '15px'}),
            html.Div(id='recent-transactions-table')
        ], style={'padding': '20px', 'backgroundColor': COLORS['card'], 'borderRadius': '8px',
                  'margin': '0 20px 20px 20px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        # Footer
        html.Div([
            html.P(id='last-updated', style={'textAlign': 'center', 'color': COLORS['muted'], 'fontSize': 12})
        ])
    ])


def create_transactions_tab():
    """Create transactions CRUD tab"""
    return html.Div([
        # Add Transaction Form
        html.Div([
            html.H3("➕ Add New Transaction", style={'color': COLORS['text'], 'marginBottom': '20px'}),
            
            html.Div([
                html.Div([
                    html.Label("Amount (₹)", style={'fontWeight': 'bold'}),
                    dcc.Input(id='trans-amount', type='number', placeholder='Enter amount', min=0.01, step=0.01,
                             style={'width': '100%', 'padding': '10px', 'marginTop': '5px', 'borderRadius': '4px', 'border': '1px solid #ddd'})
                ], style={'flex': 1, 'marginRight': '15px'}),
                
                html.Div([
                    html.Label("Type", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(id='trans-type', options=[
                        {'label': '💰 Income', 'value': 'INCOME'},
                        {'label': '💸 Expense', 'value': 'EXPENSE'}
                    ], placeholder='Select type', style={'marginTop': '5px'})
                ], style={'flex': 1, 'marginRight': '15px'}),
                
                html.Div([
                    html.Label("Category", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(id='trans-category', placeholder='Select category', style={'marginTop': '5px'})
                ], style={'flex': 1, 'marginRight': '15px'}),
                
                html.Div([
                    html.Label("Date", style={'fontWeight': 'bold'}),
                    dcc.DatePickerSingle(id='trans-date', date=date.today(), display_format='DD/MM/YYYY',
                                        style={'marginTop': '5px'})
                ], style={'flex': 1}),
            ], style={'display': 'flex', 'marginBottom': '15px'}),
            
            html.Div([
                html.Label("Description", style={'fontWeight': 'bold'}),
                dcc.Input(id='trans-description', type='text', placeholder='Enter description (optional)',
                         style={'width': '100%', 'padding': '10px', 'marginTop': '5px', 'borderRadius': '4px', 'border': '1px solid #ddd'})
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Button('Add Transaction', id='add-trans-button',
                           style={'padding': '12px 30px', 'backgroundColor': COLORS['success'],
                                  'color': 'white', 'border': 'none', 'borderRadius': '4px',
                                  'cursor': 'pointer', 'fontSize': '14px', 'fontWeight': 'bold'}),
                html.Span(id='trans-message', style={'marginLeft': '15px'})
            ])
        ], style={'padding': '20px', 'backgroundColor': COLORS['card'], 'borderRadius': '8px',
                  'margin': '0 20px 20px 20px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        # Transactions List
        html.Div([
            html.H3("📋 All Transactions", style={'color': COLORS['text'], 'marginBottom': '20px'}),
            html.Div(id='transactions-list')
        ], style={'padding': '20px', 'backgroundColor': COLORS['card'], 'borderRadius': '8px',
                  'margin': '0 20px 20px 20px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
    ])


def create_categories_tab():
    """Create categories CRUD tab"""
    return html.Div([
        # Add Category Form
        html.Div([
            html.H3("➕ Add New Category", style={'color': COLORS['text'], 'marginBottom': '20px'}),
            
            html.Div([
                html.Div([
                    html.Label("Category Name", style={'fontWeight': 'bold'}),
                    dcc.Input(id='cat-name', type='text', placeholder='Enter category name',
                             style={'width': '100%', 'padding': '10px', 'marginTop': '5px', 'borderRadius': '4px', 'border': '1px solid #ddd'})
                ], style={'flex': 2, 'marginRight': '15px'}),
                
                html.Div([
                    html.Label("Type", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(id='cat-type', options=[
                        {'label': '💰 Income', 'value': 'INCOME'},
                        {'label': '💸 Expense', 'value': 'EXPENSE'}
                    ], placeholder='Select type', style={'marginTop': '5px'})
                ], style={'flex': 1, 'marginRight': '15px'}),
                
                html.Div([
                    html.Button('Add Category', id='add-cat-button',
                               style={'padding': '12px 30px', 'backgroundColor': COLORS['success'],
                                      'color': 'white', 'border': 'none', 'borderRadius': '4px',
                                      'cursor': 'pointer', 'fontSize': '14px', 'fontWeight': 'bold', 'marginTop': '25px'})
                ], style={'flex': 1}),
            ], style={'display': 'flex', 'alignItems': 'flex-end'}),
            
            html.Div(id='cat-message', style={'marginTop': '10px'})
        ], style={'padding': '20px', 'backgroundColor': COLORS['card'], 'borderRadius': '8px',
                  'margin': '0 20px 20px 20px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        # Categories List
        html.Div([
            html.H3("📁 All Categories", style={'color': COLORS['text'], 'marginBottom': '20px'}),
            html.Div(id='categories-list')
        ], style={'padding': '20px', 'backgroundColor': COLORS['card'], 'borderRadius': '8px',
                  'margin': '0 20px 20px 20px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
    ])


def create_budgets_tab():
    """Create budgets CRUD tab"""
    return html.Div([
        # Add/Update Budget Form
        html.Div([
            html.H3("💰 Set Budget", style={'color': COLORS['text'], 'marginBottom': '20px'}),
            
            html.Div([
                html.Div([
                    html.Label("Category (Expense only)", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(id='budget-category', placeholder='Select expense category', style={'marginTop': '5px'})
                ], style={'flex': 1, 'marginRight': '15px'}),
                
                html.Div([
                    html.Label("Budget Amount (₹)", style={'fontWeight': 'bold'}),
                    dcc.Input(id='budget-amount', type='number', placeholder='Enter amount', min=1, step=1,
                             style={'width': '100%', 'padding': '10px', 'marginTop': '5px', 'borderRadius': '4px', 'border': '1px solid #ddd'})
                ], style={'flex': 1, 'marginRight': '15px'}),
                
                html.Div([
                    html.Label("Period", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(id='budget-period', options=[
                        {'label': 'Monthly', 'value': 'MONTHLY'},
                        {'label': 'Weekly', 'value': 'WEEKLY'},
                        {'label': 'Yearly', 'value': 'YEARLY'}
                    ], value='MONTHLY', style={'marginTop': '5px'})
                ], style={'flex': 1, 'marginRight': '15px'}),
                
                html.Div([
                    html.Button('Set Budget', id='add-budget-button',
                               style={'padding': '12px 30px', 'backgroundColor': COLORS['success'],
                                      'color': 'white', 'border': 'none', 'borderRadius': '4px',
                                      'cursor': 'pointer', 'fontSize': '14px', 'fontWeight': 'bold', 'marginTop': '25px'})
                ], style={'flex': 1}),
            ], style={'display': 'flex', 'alignItems': 'flex-end'}),
            
            html.Div(id='budget-message', style={'marginTop': '10px'})
        ], style={'padding': '20px', 'backgroundColor': COLORS['card'], 'borderRadius': '8px',
                  'margin': '0 20px 20px 20px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        # Budget Status List
        html.Div([
            html.H3("📊 Budget Status", style={'color': COLORS['text'], 'marginBottom': '20px'}),
            html.Div(id='budgets-list')
        ], style={'padding': '20px', 'backgroundColor': COLORS['card'], 'borderRadius': '8px',
                  'margin': '0 20px 20px 20px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
    ])


# ==================== MAIN LAYOUT ====================

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='auth-token', storage_type='session'),
    dcc.Store(id='user-info', storage_type='session'),
    html.Div(id='page-content')
])


# ==================== CALLBACKS ====================

# Page routing based on auth
@app.callback(
    Output('page-content', 'children'),
    Input('auth-token', 'data')
)
def display_page(token):
    if token:
        return create_dashboard_layout()
    return create_login_layout()


# Login callback
@app.callback(
    [Output('auth-token', 'data', allow_duplicate=True),
     Output('user-info', 'data', allow_duplicate=True),
     Output('login-error', 'children')],
    Input('login-button', 'n_clicks'),
    [State('login-username', 'value'),
     State('login-password', 'value')],
    prevent_initial_call=True
)
def login(n_clicks, username, password):
    if not n_clicks:
        raise PreventUpdate
    
    if not username or not password:
        return None, None, "Please enter username and password"
    
    data, error = api_request("POST", "/auth/login/json", data={"username": username, "password": password})
    
    if error:
        return None, None, f"Login failed: {error}"
    
    return data.get('access_token'), data.get('user'), ""


# Register callback
@app.callback(
    [Output('auth-token', 'data', allow_duplicate=True),
     Output('user-info', 'data', allow_duplicate=True),
     Output('register-error', 'children'),
     Output('register-success', 'children')],
    Input('register-button', 'n_clicks'),
    [State('register-username', 'value'),
     State('register-email', 'value'),
     State('register-fullname', 'value'),
     State('register-password', 'value')],
    prevent_initial_call=True
)
def register(n_clicks, username, email, fullname, password):
    if not n_clicks:
        raise PreventUpdate
    
    if not username or not email or not password:
        return None, None, "Please fill in all required fields", ""
    
    if len(password) < 6:
        return None, None, "Password must be at least 6 characters", ""
    
    data, error = api_request("POST", "/auth/register", data={
        "username": username,
        "email": email,
        "password": password,
        "full_name": fullname
    })
    
    if error:
        return None, None, f"Registration failed: {error}", ""
    
    return data.get('access_token'), data.get('user'), "", "Registration successful! You are now logged in."


# Logout callback
@app.callback(
    [Output('auth-token', 'data', allow_duplicate=True),
     Output('user-info', 'data', allow_duplicate=True)],
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def logout(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    return None, None


# Display username
@app.callback(
    Output('user-display', 'children'),
    Input('user-info', 'data')
)
def display_user(user_info):
    if user_info:
        return f"👤 Welcome, {user_info.get('full_name') or user_info.get('username', 'User')}!"
    return ""


# Tab content rendering
@app.callback(
    Output('tab-content', 'children'),
    Input('main-tabs', 'value')
)
def render_tab(tab):
    if tab == 'dashboard':
        return create_dashboard_tab()
    elif tab == 'transactions':
        return create_transactions_tab()
    elif tab == 'categories':
        return create_categories_tab()
    elif tab == 'budgets':
        return create_budgets_tab()
    return create_dashboard_tab()


# Update category dropdown in filters
@app.callback(
    Output('category-filter', 'options'),
    [Input('interval-component', 'n_intervals'),
     Input('auth-token', 'data')]
)
def update_category_dropdown(n, token):
    df = fetch_categories_api(token)
    if df.empty:
        return []
    return [{'label': f"{row['name']} ({row['type']})", 'value': row['category_id']}
            for _, row in df.iterrows()]


# Update transaction category dropdown
@app.callback(
    Output('trans-category', 'options'),
    [Input('trans-type', 'value'),
     Input('auth-token', 'data'),
     Input('refresh-trigger', 'data')]
)
def update_trans_category_dropdown(trans_type, token, refresh):
    df = fetch_categories_api(token)
    if df.empty:
        return []
    if trans_type:
        df = df[df['type'] == trans_type]
    return [{'label': row['name'], 'value': row['category_id']} for _, row in df.iterrows()]


# Update budget category dropdown (expense only)
@app.callback(
    Output('budget-category', 'options'),
    [Input('auth-token', 'data'),
     Input('refresh-trigger', 'data')]
)
def update_budget_category_dropdown(token, refresh):
    df = fetch_categories_api(token)
    if df.empty:
        return []
    df = df[df['type'] == 'EXPENSE']
    return [{'label': row['name'], 'value': row['category_id']} for _, row in df.iterrows()]


# Selected Category Info callback
@app.callback(
    Output('selected-category-info', 'children'),
    [Input('category-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('auth-token', 'data')]
)
def update_selected_category_info(category_id, start_date, end_date, token):
    if not category_id:
        return html.Div()  # Return empty if no category selected
    
    # Fetch category details
    cat_df = fetch_categories_api(token)
    if cat_df.empty:
        return html.Div()
    
    category = cat_df[cat_df['category_id'] == category_id]
    if category.empty:
        return html.Div()
    
    cat_name = category.iloc[0]['name']
    cat_type = category.iloc[0]['type']
    
    # Fetch transactions for this category
    trans_df = fetch_transactions_api(token, start_date, end_date, category_id)
    
    if trans_df.empty:
        total_amount = 0
        trans_count = 0
    else:
        total_amount = trans_df['amount'].sum()
        trans_count = len(trans_df)
    
    # Style based on type
    if cat_type == 'INCOME':
        bg_color = '#d4edda'
        border_color = '#28a745'
        icon = '💰'
        type_label = 'Income'
    else:
        bg_color = '#f8d7da'
        border_color = '#dc3545'
        icon = '💸'
        type_label = 'Expense'
    
    return html.Div([
        html.Div([
            html.H4(f"{icon} {cat_name}", style={'margin': '0', 'color': '#333'}),
            html.Span(type_label, style={
                'backgroundColor': border_color,
                'color': 'white',
                'padding': '2px 10px',
                'borderRadius': '12px',
                'fontSize': '12px',
                'marginLeft': '10px'
            })
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
        html.Div([
            html.Span(f"Total: ", style={'fontWeight': 'bold', 'color': '#666'}),
            html.Span(f"₹{total_amount:,.2f}", style={
                'fontSize': '24px',
                'fontWeight': 'bold',
                'color': border_color
            }),
            html.Span(f" ({trans_count} transactions)", style={
                'color': '#888',
                'marginLeft': '10px',
                'fontSize': '14px'
            })
        ])
    ], style={
        'backgroundColor': bg_color,
        'border': f'2px solid {border_color}',
        'borderRadius': '10px',
        'padding': '15px 20px',
        'marginBottom': '20px'
    })


# Dashboard update callback
@app.callback(
    [Output('total-income', 'children'),
     Output('total-expenses', 'children'),
     Output('balance', 'children'),
     Output('transaction-count', 'children'),
     Output('expense-pie-chart', 'figure'),
     Output('monthly-bar-chart', 'figure'),
     Output('balance-line-chart', 'figure'),
     Output('budget-status', 'children'),
     Output('recent-transactions-table', 'children'),
     Output('last-updated', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('category-filter', 'value'),
     Input('refresh-trigger', 'data'),
     Input('auth-token', 'data')]
)
def update_dashboard(n, start_date, end_date, category_id, refresh, token):
    try:
        # Fetch summary
        summary = fetch_summary_api(token, start_date, end_date)
        
        # Fetch transactions
        trans_df = fetch_transactions_api(token, start_date, end_date, category_id)
        
        if trans_df.empty:
            empty_fig = go.Figure()
            empty_fig.add_annotation(text="No data available", x=0.5, y=0.5,
                                    xref="paper", yref="paper", showarrow=False)
            empty_fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
            return ('₹0', '₹0', '₹0', '0', empty_fig, empty_fig, empty_fig,
                   html.P("No budgets set"), html.P("No transactions"),
                   f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get categories for names
        cat_df = fetch_categories_api(token)
        cat_map = dict(zip(cat_df['category_id'], cat_df['name'])) if not cat_df.empty else {}
        trans_df['category_name'] = trans_df['category_id'].map(cat_map)
        trans_df['transaction_date'] = pd.to_datetime(trans_df['transaction_date'])
        
        total_income = summary['total_income']
        total_expenses = summary['total_expenses']
        balance = summary['balance']
        trans_count = summary['transaction_count']
        
        # Expense Pie Chart
        expense_df = trans_df[trans_df['type'] == 'EXPENSE']
        if not expense_df.empty:
            expense_by_cat = expense_df.groupby('category_name')['amount'].sum().reset_index()
            pie_fig = px.pie(expense_by_cat, values='amount', names='category_name',
                            title='💸 Expense Distribution', hole=0.4,
                            color_discrete_sequence=px.colors.qualitative.Set3)
            pie_fig.update_layout(paper_bgcolor='white', showlegend=True,
                                 legend=dict(orientation="h", yanchor="bottom", y=-0.3))
        else:
            pie_fig = go.Figure()
            pie_fig.add_annotation(text="No expenses", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
            pie_fig.update_layout(title='💸 Expense Distribution', plot_bgcolor='white', paper_bgcolor='white')
        
        # Monthly Bar Chart
        monthly_df = trans_df.copy()
        monthly_df['month'] = monthly_df['transaction_date'].dt.to_period('M').astype(str)
        monthly_summary = monthly_df.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0)
        
        if not monthly_summary.empty:
            bar_fig = go.Figure()
            if 'INCOME' in monthly_summary.columns:
                bar_fig.add_trace(go.Bar(name='Income', x=monthly_summary.index,
                                        y=monthly_summary['INCOME'], marker_color=COLORS['income'],
                                        hovertemplate='%{x}<br>Income: ₹%{y:,.2f}<extra></extra>'))
            if 'EXPENSE' in monthly_summary.columns:
                bar_fig.add_trace(go.Bar(name='Expenses', x=monthly_summary.index,
                                        y=monthly_summary['EXPENSE'], marker_color=COLORS['expense'],
                                        hovertemplate='%{x}<br>Expenses: ₹%{y:,.2f}<extra></extra>'))
            bar_fig.update_layout(title='📊 Monthly Income vs Expenses', barmode='group',
                                 plot_bgcolor='white', paper_bgcolor='white',
                                 yaxis=dict(tickformat=',.0f', tickprefix='₹'))
        else:
            bar_fig = go.Figure()
            bar_fig.update_layout(title='📊 Monthly Income vs Expenses', plot_bgcolor='white', paper_bgcolor='white')
        
        # Balance Line Chart
        daily_df = trans_df.sort_values('transaction_date')
        daily_df['signed_amount'] = daily_df.apply(
            lambda x: x['amount'] if x['type'] == 'INCOME' else -x['amount'], axis=1)
        daily_df['cumulative_balance'] = daily_df['signed_amount'].cumsum()
        
        if not daily_df.empty:
            line_fig = px.line(daily_df, x='transaction_date', y='cumulative_balance',
                              title='📈 Balance Trend', markers=True)
            line_fig.update_traces(line_color=COLORS['balance'],
                                   hovertemplate='%{x|%Y-%m-%d}<br>Balance: ₹%{y:,.2f}<extra></extra>')
            line_fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                                   yaxis=dict(tickformat=',.0f', tickprefix='₹'))
            line_fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        else:
            line_fig = go.Figure()
            line_fig.update_layout(title='📈 Balance Trend', plot_bgcolor='white', paper_bgcolor='white')
        
        # Budget Status (pass date range to show spending for selected period)
        budgets_df = fetch_budgets_api(token, start_date, end_date)
        if not budgets_df.empty:
            budget_cards = []
            for _, budget in budgets_df.iterrows():
                percentage = budget['percentage_used']
                is_over = budget['is_over_budget']
                color = COLORS['expense'] if is_over else (COLORS['warning'] if percentage > 80 else COLORS['income'])
                
                budget_cards.append(html.Div([
                    html.Div([
                        html.Span(budget['category_name'], style={'fontWeight': 'bold', 'fontSize': 14}),
                        html.Span(f" ₹{budget['spent_amount']:,.0f} / ₹{budget['budget_amount']:,.0f}",
                                 style={'color': COLORS['muted'], 'fontSize': 12})
                    ]),
                    html.Div([
                        html.Div(style={'width': f'{min(percentage, 100)}%', 'height': '8px',
                                       'backgroundColor': color, 'borderRadius': '4px'})
                    ], style={'width': '100%', 'height': '8px', 'backgroundColor': '#ecf0f1',
                             'borderRadius': '4px', 'marginTop': '5px'}),
                    html.Span('⚠️ Over budget!' if is_over else f"₹{budget['remaining']:,.0f} remaining",
                             style={'fontSize': 11, 'color': color if is_over else COLORS['muted']})
                ], style={'marginBottom': '15px'}))
            budget_status = html.Div(budget_cards)
        else:
            budget_status = html.P("No budgets set. Go to Budgets tab to create one.",
                                  style={'color': COLORS['muted']})
        
        # Recent Transactions Table
        recent_trans = trans_df.head(10).copy()
        if not recent_trans.empty:
            recent_trans['date_str'] = recent_trans['transaction_date'].dt.strftime('%Y-%m-%d')
            recent_trans['amount_display'] = recent_trans.apply(
                lambda x: f"{'+ ' if x['type'] == 'INCOME' else '- '}₹{x['amount']:,.2f}", axis=1)
            
            trans_table = dash_table.DataTable(
                data=recent_trans[['date_str', 'category_name', 'description', 'amount_display', 'type']].to_dict('records'),
                columns=[
                    {'name': 'Date', 'id': 'date_str'},
                    {'name': 'Category', 'id': 'category_name'},
                    {'name': 'Description', 'id': 'description'},
                    {'name': 'Amount', 'id': 'amount_display'},
                    {'name': 'Type', 'id': 'type'}
                ],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '10px', 'fontSize': 13},
                style_header={'backgroundColor': COLORS['text'], 'color': 'white', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9f9f9'},
                    {'if': {'filter_query': '{type} = INCOME'}, 'color': COLORS['income'], 'fontWeight': 'bold'},
                    {'if': {'filter_query': '{type} = EXPENSE'}, 'color': COLORS['expense']}
                ]
            )
        else:
            trans_table = html.P("No transactions", style={'color': COLORS['muted']})
        
        timestamp = f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return (f"₹{total_income:,.2f}", f"₹{total_expenses:,.2f}", f"₹{balance:,.2f}",
                str(trans_count), pie_fig, bar_fig, line_fig, budget_status, trans_table, timestamp)
    
    except Exception as e:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
        empty_fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        return ('₹0', '₹0', '₹0', '0', empty_fig, empty_fig, empty_fig,
               html.P(f"Error: {e}"), html.P(f"Error: {e}"),
               f"Error: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# Add Transaction callback
@app.callback(
    [Output('trans-message', 'children'),
     Output('refresh-trigger', 'data', allow_duplicate=True),
     Output('trans-amount', 'value'),
     Output('trans-description', 'value')],
    Input('add-trans-button', 'n_clicks'),
    [State('trans-amount', 'value'),
     State('trans-type', 'value'),
     State('trans-category', 'value'),
     State('trans-date', 'date'),
     State('trans-description', 'value'),
     State('auth-token', 'data'),
     State('refresh-trigger', 'data')],
    prevent_initial_call=True
)
def add_transaction(n_clicks, amount, trans_type, category_id, trans_date, description, token, refresh):
    if not n_clicks:
        raise PreventUpdate
    
    if not all([amount, trans_type, category_id, trans_date]):
        return html.Span("Please fill all required fields", style={'color': COLORS['danger']}), refresh, amount, description
    
    data, error = api_request("POST", "/transactions/", token, data={
        "amount": float(amount),
        "type": trans_type,
        "category_id": category_id,
        "transaction_date": trans_date,
        "description": description or ""
    })
    
    if error:
        return html.Span(f"Error: {error}", style={'color': COLORS['danger']}), refresh, amount, description
    
    return html.Span("✅ Transaction added successfully!", style={'color': COLORS['success']}), refresh + 1, None, None


# Add Category callback
@app.callback(
    [Output('cat-message', 'children'),
     Output('refresh-trigger', 'data', allow_duplicate=True),
     Output('cat-name', 'value')],
    Input('add-cat-button', 'n_clicks'),
    [State('cat-name', 'value'),
     State('cat-type', 'value'),
     State('auth-token', 'data'),
     State('refresh-trigger', 'data')],
    prevent_initial_call=True
)
def add_category(n_clicks, name, cat_type, token, refresh):
    if not n_clicks:
        raise PreventUpdate
    
    if not name or not cat_type:
        return html.Span("Please fill all fields", style={'color': COLORS['danger']}), refresh, name
    
    data, error = api_request("POST", "/categories/", token, data={
        "name": name,
        "type": cat_type
    })
    
    if error:
        return html.Span(f"Error: {error}", style={'color': COLORS['danger']}), refresh, name
    
    return html.Span("✅ Category added successfully!", style={'color': COLORS['success']}), refresh + 1, None


# Add Budget callback
@app.callback(
    [Output('budget-message', 'children'),
     Output('refresh-trigger', 'data', allow_duplicate=True)],
    Input('add-budget-button', 'n_clicks'),
    [State('budget-category', 'value'),
     State('budget-amount', 'value'),
     State('budget-period', 'value'),
     State('auth-token', 'data'),
     State('refresh-trigger', 'data')],
    prevent_initial_call=True
)
def add_budget(n_clicks, category_id, amount, period, token, refresh):
    if not n_clicks:
        raise PreventUpdate
    
    if not category_id or not amount:
        return html.Span("Please select category and enter amount", style={'color': COLORS['danger']}), refresh
    
    data, error = api_request("POST", "/budgets/", token, data={
        "category_id": category_id,
        "amount": float(amount),
        "period": period
    })
    
    if error:
        return html.Span(f"Error: {error}", style={'color': COLORS['danger']}), refresh
    
    return html.Span("✅ Budget set successfully!", style={'color': COLORS['success']}), refresh + 1


# Transactions list callback
@app.callback(
    Output('transactions-list', 'children'),
    [Input('refresh-trigger', 'data'),
     Input('auth-token', 'data')]
)
def update_transactions_list(refresh, token):
    df = fetch_transactions_api(token)
    if df.empty:
        return html.P("No transactions yet. Add one above!", style={'color': COLORS['muted']})
    
    cat_df = fetch_categories_api(token)
    cat_map = dict(zip(cat_df['category_id'], cat_df['name'])) if not cat_df.empty else {}
    df['category_name'] = df['category_id'].map(cat_map)
    df['transaction_date'] = pd.to_datetime(df['transaction_date']).dt.strftime('%Y-%m-%d')
    df['amount_display'] = df.apply(lambda x: f"{'+ ' if x['type'] == 'INCOME' else '- '}₹{x['amount']:,.2f}", axis=1)
    
    return dash_table.DataTable(
        data=df[['transaction_id', 'transaction_date', 'category_name', 'description', 'amount_display', 'type']].to_dict('records'),
        columns=[
            {'name': 'ID', 'id': 'transaction_id'},
            {'name': 'Date', 'id': 'transaction_date'},
            {'name': 'Category', 'id': 'category_name'},
            {'name': 'Description', 'id': 'description'},
            {'name': 'Amount', 'id': 'amount_display'},
            {'name': 'Type', 'id': 'type'}
        ],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '10px', 'fontSize': 13},
        style_header={'backgroundColor': COLORS['text'], 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9f9f9'},
            {'if': {'filter_query': '{type} = INCOME'}, 'color': COLORS['income']},
            {'if': {'filter_query': '{type} = EXPENSE'}, 'color': COLORS['expense']}
        ],
        page_size=15,
        sort_action='native',
        filter_action='native'
    )


# Categories list callback
@app.callback(
    Output('categories-list', 'children'),
    [Input('refresh-trigger', 'data'),
     Input('auth-token', 'data')]
)
def update_categories_list(refresh, token):
    df = fetch_categories_api(token)
    if df.empty:
        return html.P("No categories. Add one above!", style={'color': COLORS['muted']})
    
    return dash_table.DataTable(
        data=df[['category_id', 'name', 'type']].to_dict('records'),
        columns=[
            {'name': 'ID', 'id': 'category_id'},
            {'name': 'Name', 'id': 'name'},
            {'name': 'Type', 'id': 'type'}
        ],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '10px', 'fontSize': 13},
        style_header={'backgroundColor': COLORS['text'], 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9f9f9'},
            {'if': {'filter_query': '{type} = INCOME'}, 'color': COLORS['income']},
            {'if': {'filter_query': '{type} = EXPENSE'}, 'color': COLORS['expense']}
        ]
    )


# Budgets list callback
@app.callback(
    Output('budgets-list', 'children'),
    [Input('refresh-trigger', 'data'),
     Input('auth-token', 'data')]
)
def update_budgets_list(refresh, token):
    df = fetch_budgets_api(token)
    if df.empty:
        return html.P("No budgets set. Create one above!", style={'color': COLORS['muted']})
    
    budget_cards = []
    for _, row in df.iterrows():
        percentage = row['percentage_used']
        is_over = row['is_over_budget']
        color = COLORS['expense'] if is_over else (COLORS['warning'] if percentage > 80 else COLORS['income'])
        
        budget_cards.append(html.Div([
            html.Div([
                html.H4(row['category_name'], style={'margin': 0, 'color': COLORS['text']}),
                html.P(f"Budget: ₹{row['budget_amount']:,.0f}", style={'margin': '5px 0', 'color': COLORS['muted']})
            ], style={'flex': 1}),
            html.Div([
                html.Div([
                    html.Span(f"Spent: ₹{row['spent_amount']:,.0f}", style={'fontWeight': 'bold'}),
                    html.Span(f" ({percentage:.1f}%)", style={'color': color})
                ]),
                html.Div([
                    html.Div(style={'width': f'{min(percentage, 100)}%', 'height': '12px',
                                   'backgroundColor': color, 'borderRadius': '6px', 'transition': 'width 0.3s'})
                ], style={'width': '200px', 'height': '12px', 'backgroundColor': '#ecf0f1',
                         'borderRadius': '6px', 'marginTop': '5px'}),
                html.Span('⚠️ OVER BUDGET!' if is_over else f"Remaining: ₹{row['remaining']:,.0f}",
                         style={'fontSize': 12, 'color': color if is_over else COLORS['muted']})
            ], style={'flex': 2})
        ], style={'display': 'flex', 'padding': '15px', 'marginBottom': '10px',
                  'backgroundColor': '#f9f9f9', 'borderRadius': '8px',
                  'borderLeft': f'4px solid {color}'}))
    
    return html.Div(budget_cards)


if __name__ == '__main__':
    print("=" * 60)
    print("Starting Personal Finance Tracker Dashboard v2.0...")
    print("Dashboard: http://127.0.0.1:8050")
    print(f"API: {API_BASE_URL}")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=8050)
