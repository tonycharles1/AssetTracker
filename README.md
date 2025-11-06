# Asset Tracker Application

A comprehensive web-based Asset Tracking System built with Streamlit and Google Sheets.

## Features

- 🔐 **User Authentication**: Register and login with role-based access (Users/Admin)
- 📊 **Dashboard**: Visual analytics with graphs and statistics
- 📦 **Asset Management**: Complete CRUD operations for assets
- 🏷️ **Master Data Management**: 
  - Locations
  - Categories
  - Subcategories
  - Asset Types
  - Brands
- 🔍 **Search & Scanner**: Barcode scanner and search functionality
- 🖨️ **Barcode Printing**: Generate and print barcodes for multiple assets
- 🚚 **Asset Movements**: Track asset movements between locations

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Sheets Setup

1. Create a Google Cloud Project and enable Google Sheets API
2. Create a Service Account and download the credentials JSON file
3. Place the `credentials.json` file in the project root directory
4. Create a Google Spreadsheet with the following sheets:
   - Users
   - Locations
   - Categories
   - Subcategories
   - AssetTypes
   - Brands
   - Assets
   - AssetMovements

### 3. Share Spreadsheet with Service Account

1. Open your Google Spreadsheet
2. Click "Share" button
3. Add the service account email (found in credentials.json) with "Editor" permissions

### 4. Run the Application

```bash
streamlit run app.py
```

## Usage

1. **First Time Setup**:
   - Register a new user account
   - Login with your credentials

2. **Connect to Spreadsheet**:
   - Enter your Google Spreadsheet ID or Title in the sidebar
   - Click "Connect"

3. **Add Master Data**:
   - Start by adding Locations, Categories, Subcategories, Asset Types, and Brands
   - These will be used as dropdown options when creating assets

4. **Add Assets**:
   - Navigate to Assets section
   - Fill in the asset form
   - Asset Code (barcode) is generated automatically
   - Upload images and documents if needed

5. **Search & Scan**:
   - Use the Search Assets page to find assets
   - Use Barcode Scanner to scan and find assets by code

6. **Print Barcodes**:
   - Select multiple assets
   - View and print barcode labels

7. **Track Movements**:
   - Use Asset Movements to move assets between locations
   - All movements are recorded with timestamps

## Asset Fields

- Item Name (Required)
- Asset Category (Required)
- Asset Subcategory
- Brand
- Asset Description
- Amount
- Location (Required)
- Date of Purchase
- Warranty
- Department
- Ownership
- Asset Status (Active, Inactive, Under Maintenance, Disposed, Lost)
- Image Attachment
- Document Attachment
- Asset Code (Auto-generated barcode, Primary Key)

## Dashboard Features

- Total Assets count
- Active Assets count
- Total Asset Value
- Assets by Status (Pie Chart)
- Assets by Location (Bar Chart)
- Assets by Category (Bar Chart)
- Assets Value by Department (Bar Chart)
- Recent Asset Movements

## Notes

- Asset Codes are automatically generated as barcodes
- All data is stored in Google Sheets
- User passwords are hashed using SHA256
- Barcode format: Code128
- Supports image and document attachments (metadata stored, files can be enhanced with Google Drive integration)

## Troubleshooting

- **Connection Issues**: Ensure credentials.json is in the correct location and spreadsheet is shared with service account
- **Empty Sheets**: Make sure all required sheets exist in your Google Spreadsheet
- **Barcode Generation**: Ensure barcode library is properly installed

## Future Enhancements

- Google Drive integration for file storage
- Advanced reporting and exports
- Email notifications for asset movements
- Multi-user collaboration features
- Mobile app integration
