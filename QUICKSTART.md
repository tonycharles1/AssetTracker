# Quick Start Guide

## Step 1: Install Dependencies

Open your terminal/command prompt and run:

```bash
pip install -r requirements.txt
```

## Step 2: Prepare Google Sheets

1. **Create a Google Spreadsheet** with these exact sheet names:
   - Users
   - Locations
   - Categories
   - Subcategories
   - AssetTypes
   - Brands
   - Assets
   - AssetMovements

2. **Share the spreadsheet** with your service account email:
   - Open your spreadsheet
   - Click "Share"
   - Add the email from your `credentials.json` file (it looks like: `xxxxx@xxxxx.iam.gserviceaccount.com`)
   - Give it "Editor" permissions

## Step 3: Get Spreadsheet ID

- Open your Google Spreadsheet
- Look at the URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit`
- Copy the `SPREADSHEET_ID_HERE` part

## Step 4: Run the Application

```bash
streamlit run app.py
```

The app will open in your browser automatically.

## Step 5: First Time Setup

1. **Register**: Click on "Register" tab and create your first admin account
2. **Login**: Use your credentials to login
3. **Connect Spreadsheet**: 
   - In the sidebar, enter your Spreadsheet ID or Title
   - Click "Connect"
4. **Add Master Data** (in order):
   - Add Locations first
   - Add Categories
   - Add Subcategories (linked to Categories)
   - Add Asset Types
   - Add Brands
5. **Add Assets**: Now you can start adding assets!

## Tips

- Asset Codes are automatically generated as barcodes
- Use the Barcode Scanner page to search assets by scanning
- Select multiple assets in "Print Barcodes" to generate labels
- Track all asset movements in the Asset Movements section
- Dashboard shows real-time statistics and graphs

## Troubleshooting

**"Error connecting to Google Sheets"**
- Check that `credentials.json` is in the project folder
- Verify the spreadsheet is shared with the service account email

**"Sheet not found"**
- Make sure all sheet names match exactly (case-sensitive)
- Create empty sheets with the exact names listed above

**"Authentication failed"**
- Make sure you've registered a user first
- Check username/password spelling

**Barcode not generating**
- Ensure `python-barcode` and `Pillow` are installed
- Check that asset code is not empty

## Need Help?

Check the main README.md for detailed documentation.

