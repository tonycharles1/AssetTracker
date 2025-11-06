"""
Configuration file for Asset Tracker Application
"""
import os

# Google Sheets Configuration
CREDENTIALS_FILE = "credentials.json"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# Sheet Names
SHEETS = {
    'users': 'Users',
    'locations': 'Locations',
    'categories': 'Categories',
    'subcategories': 'Subcategories',
    'asset_types': 'AssetTypes',
    'brands': 'Brands',
    'assets': 'Assets',
    'asset_movements': 'AssetMovements'
}

# Asset Status Options
ASSET_STATUS_OPTIONS = ['Active', 'Inactive', 'Under Maintenance', 'Disposed', 'Lost']

# Ownership Options
OWNERSHIP_OPTIONS = ['Company', 'Leased', 'Rented']

# Session State Keys
SESSION_KEYS = {
    'authenticated': 'authenticated',
    'username': 'username',
    'user_role': 'user_role',
    'user_id': 'user_id'
}

