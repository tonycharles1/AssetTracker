"""
Google Sheets Integration Module
"""
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from config import CREDENTIALS_FILE, SCOPES, SHEETS
from datetime import datetime
import streamlit as st

class GoogleSheetsDB:
    def __init__(self, spreadsheet_id=None):
        """Initialize Google Sheets connection"""
        try:
            creds = Credentials.from_service_account_file(
                CREDENTIALS_FILE,
                scopes=SCOPES
            )
            self.client = gspread.authorize(creds)
            self.spreadsheet_id = spreadsheet_id
            if spreadsheet_id:
                self.spreadsheet = self.client.open_by_key(spreadsheet_id)
            else:
                # Try to open by title if ID not provided
                self.spreadsheet = None
        except Exception as e:
            st.error(f"Error connecting to Google Sheets: {str(e)}")
            self.client = None
            self.spreadsheet = None
    
    def set_spreadsheet(self, spreadsheet_id_or_title):
        """Set the spreadsheet by ID or title"""
        try:
            if len(spreadsheet_id_or_title) > 30:  # Likely an ID
                self.spreadsheet = self.client.open_by_key(spreadsheet_id_or_title)
            else:  # Likely a title
                self.spreadsheet = self.client.open(spreadsheet_id_or_title)
            self.spreadsheet_id = self.spreadsheet.id
            return True
        except Exception as e:
            st.error(f"Error opening spreadsheet: {str(e)}")
            return False
    
    def get_worksheet(self, sheet_name):
        """Get a worksheet by name, create if doesn't exist"""
        if not self.spreadsheet:
            return None
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            # Create worksheet if it doesn't exist
            worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            return worksheet
    
    def read_data(self, sheet_name):
        """Read all data from a sheet as DataFrame"""
        worksheet = self.get_worksheet(sheet_name)
        if not worksheet:
            return pd.DataFrame()
        try:
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error reading data from {sheet_name}: {str(e)}")
            return pd.DataFrame()
    
    def write_data(self, sheet_name, data):
        """Write data to a sheet (data can be list of dicts or DataFrame)"""
        worksheet = self.get_worksheet(sheet_name)
        if not worksheet:
            return False
        try:
            # Clear existing data
            worksheet.clear()
            
            # Handle DataFrame
            if isinstance(data, pd.DataFrame):
                if not data.empty:
                    # Write headers
                    worksheet.append_row(data.columns.tolist())
                    # Write data rows
                    for _, row in data.iterrows():
                        worksheet.append_row(row.tolist())
            # Handle list of dicts
            elif isinstance(data, list) and len(data) > 0:
                headers = list(data[0].keys())
                worksheet.append_row(headers)
                # Write data rows
                for row in data:
                    worksheet.append_row([row.get(h, '') for h in headers])
            return True
        except Exception as e:
            st.error(f"Error writing data to {sheet_name}: {str(e)}")
            return False
    
    def append_row(self, sheet_name, row_data):
        """Append a single row to a sheet"""
        worksheet = self.get_worksheet(sheet_name)
        if not worksheet:
            return False
        try:
            # Get headers if sheet is empty
            existing_data = worksheet.get_all_values()
            if len(existing_data) == 0:
                headers = list(row_data.keys())
                worksheet.append_row(headers)
            
            # Get current headers
            headers = worksheet.row_values(1)
            if not headers:
                headers = list(row_data.keys())
                worksheet.append_row(headers)
            
            # Ensure all headers exist in row_data
            row_values = []
            for h in headers:
                if h in row_data:
                    value = row_data[h]
                    # Convert None to empty string
                    if value is None:
                        value = ''
                    row_values.append(str(value))
                else:
                    row_values.append('')
            
            worksheet.append_row(row_values)
            return True
        except Exception as e:
            st.error(f"Error appending row to {sheet_name}: {str(e)}")
            return False
    
    def update_row(self, sheet_name, row_index, row_data):
        """Update a row in a sheet"""
        worksheet = self.get_worksheet(sheet_name)
        if not worksheet:
            return False
        try:
            headers = worksheet.row_values(1)
            row_values = [row_data.get(h, '') for h in headers]
            worksheet.update(f'A{row_index+1}', [row_values])
            return True
        except Exception as e:
            st.error(f"Error updating row in {sheet_name}: {str(e)}")
            return False
    
    def delete_row(self, sheet_name, row_index):
        """Delete a row from a sheet"""
        worksheet = self.get_worksheet(sheet_name)
        if not worksheet:
            return False
        try:
            worksheet.delete_rows(row_index + 1)
            return True
        except Exception as e:
            st.error(f"Error deleting row from {sheet_name}: {str(e)}")
            return False
    
    def find_row(self, sheet_name, column_name, value):
        """Find row index by column value"""
        worksheet = self.get_worksheet(sheet_name)
        if not worksheet:
            return -1
        try:
            data = worksheet.get_all_records()
            for idx, row in enumerate(data):
                if str(row.get(column_name, '')).lower() == str(value).lower():
                    return idx + 1  # +1 because row 1 is header
            return -1
        except Exception as e:
            st.error(f"Error finding row in {sheet_name}: {str(e)}")
            return -1

