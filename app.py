"""
Main Asset Tracker Application
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from google_sheets import GoogleSheetsDB
from auth import authenticate_user, register_user, check_authentication, get_current_user, logout
from dashboard import show_dashboard
from barcode_utils import generate_barcode, generate_asset_code, create_barcode_label
from config import SHEETS, ASSET_STATUS_OPTIONS, OWNERSHIP_OPTIONS
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="Asset Tracker",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = None
if 'spreadsheet_id' not in st.session_state:
    st.session_state.spreadsheet_id = None

def init_db():
    """Initialize database connection"""
    if st.session_state.db is None:
        st.session_state.db = GoogleSheetsDB()
    return st.session_state.db

def login_page():
    """Login page"""
    st.title("🔐 Asset Tracker Login")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                db = init_db()
                if st.session_state.spreadsheet_id:
                    db.set_spreadsheet(st.session_state.spreadsheet_id)
                
                user = authenticate_user(db, username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.username = user['username']
                    st.session_state.user_role = user['role']
                    st.session_state.user_id = user['user_id']
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            role = st.selectbox("Role", ["User", "Admin"])
            submit_reg = st.form_submit_button("Register")
            
            if submit_reg:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 4:
                    st.error("Password must be at least 4 characters")
                else:
                    db = init_db()
                    if st.session_state.spreadsheet_id:
                        db.set_spreadsheet(st.session_state.spreadsheet_id)
                    
                    success, message = register_user(db, new_username, new_password, role)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

def main_app():
    """Main application after login"""
    db = init_db()
    
    # Sidebar navigation
    st.sidebar.title("📦 Asset Tracker")
    st.sidebar.write(f"Welcome, **{st.session_state.username}**")
    st.sidebar.write(f"Role: **{st.session_state.user_role}**")
    
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()
    
    st.sidebar.divider()
    
    # Spreadsheet ID input
    if not st.session_state.spreadsheet_id:
        spreadsheet_input = st.sidebar.text_input("Google Spreadsheet ID or Title")
        if st.sidebar.button("Connect"):
            if spreadsheet_input:
                if db.set_spreadsheet(spreadsheet_input):
                    st.session_state.spreadsheet_id = db.spreadsheet_id
                    st.sidebar.success("Connected!")
                    st.rerun()
                else:
                    st.sidebar.error("Failed to connect")
    else:
        st.sidebar.success(f"Connected to spreadsheet")
        if st.sidebar.button("Disconnect"):
            st.session_state.spreadsheet_id = None
            st.rerun()
    
    if not st.session_state.spreadsheet_id:
        st.warning("Please connect to your Google Spreadsheet first.")
        return
    
    db.set_spreadsheet(st.session_state.spreadsheet_id)
    
    # Navigation menu
    menu = st.sidebar.selectbox(
        "Navigation",
        [
            "Dashboard",
            "Locations",
            "Categories",
            "Subcategories",
            "Asset Types",
            "Brands",
            "Assets",
            "Search Assets",
            "Barcode Scanner",
            "Print Barcodes",
            "Asset Movements"
        ]
    )
    
    # Route to appropriate page
    if menu == "Dashboard":
        show_dashboard(db)
    elif menu == "Locations":
        manage_locations(db)
    elif menu == "Categories":
        manage_categories(db)
    elif menu == "Subcategories":
        manage_subcategories(db)
    elif menu == "Asset Types":
        manage_asset_types(db)
    elif menu == "Brands":
        manage_brands(db)
    elif menu == "Assets":
        manage_assets(db)
    elif menu == "Search Assets":
        search_assets(db)
    elif menu == "Barcode Scanner":
        barcode_scanner(db)
    elif menu == "Print Barcodes":
        print_barcodes(db)
    elif menu == "Asset Movements":
        manage_asset_movements(db)

def manage_locations(db):
    """Manage Locations"""
    st.title("📍 Locations Management")
    
    tab1, tab2 = st.tabs(["View Locations", "Add/Edit Location"])
    
    with tab1:
        locations_df = db.read_data(SHEETS['locations'])
        if not locations_df.empty:
            st.dataframe(locations_df, use_container_width=True)
            
            # Delete option
            if len(locations_df) > 0:
                st.subheader("Delete Location")
                location_to_delete = st.selectbox("Select Location to Delete", locations_df['Location Name'].tolist() if 'Location Name' in locations_df.columns else [])
                if st.button("Delete Location"):
                    idx = locations_df[locations_df['Location Name'] == location_to_delete].index[0]
                    if db.delete_row(SHEETS['locations'], idx + 1):
                        st.success("Location deleted!")
                        st.rerun()
        else:
            st.info("No locations found")
    
    with tab2:
        with st.form("location_form"):
            location_name = st.text_input("Location Name *")
            location_address = st.text_area("Address")
            location_description = st.text_area("Description")
            submit = st.form_submit_button("Save Location")
            
            if submit:
                if location_name:
                    location_data = {
                        'Location Name': location_name,
                        'Address': location_address,
                        'Description': location_description
                    }
                    if db.append_row(SHEETS['locations'], location_data):
                        st.success("Location saved!")
                        st.rerun()
                else:
                    st.error("Location Name is required")

def manage_categories(db):
    """Manage Categories"""
    st.title("📂 Categories Management")
    
    tab1, tab2 = st.tabs(["View Categories", "Add/Edit Category"])
    
    with tab1:
        categories_df = db.read_data(SHEETS['categories'])
        if not categories_df.empty:
            st.dataframe(categories_df, use_container_width=True)
            
            if len(categories_df) > 0:
                st.subheader("Delete Category")
                category_to_delete = st.selectbox("Select Category to Delete", categories_df['Category Name'].tolist() if 'Category Name' in categories_df.columns else [])
                if st.button("Delete Category"):
                    idx = categories_df[categories_df['Category Name'] == category_to_delete].index[0]
                    if db.delete_row(SHEETS['categories'], idx + 1):
                        st.success("Category deleted!")
                        st.rerun()
        else:
            st.info("No categories found")
    
    with tab2:
        with st.form("category_form"):
            category_name = st.text_input("Category Name *")
            category_code = st.text_input("Category Code")
            category_description = st.text_area("Description")
            submit = st.form_submit_button("Save Category")
            
            if submit:
                if category_name:
                    category_data = {
                        'Category Name': category_name,
                        'Category Code': category_code or category_name[:3].upper(),
                        'Description': category_description
                    }
                    if db.append_row(SHEETS['categories'], category_data):
                        st.success("Category saved!")
                        st.rerun()
                else:
                    st.error("Category Name is required")

def manage_subcategories(db):
    """Manage Subcategories"""
    st.title("📁 Subcategories Management")
    
    tab1, tab2 = st.tabs(["View Subcategories", "Add/Edit Subcategory"])
    
    with tab1:
        subcategories_df = db.read_data(SHEETS['subcategories'])
        categories_df = db.read_data(SHEETS['categories'])
        
        if not subcategories_df.empty:
            st.dataframe(subcategories_df, use_container_width=True)
            
            if len(subcategories_df) > 0:
                st.subheader("Delete Subcategory")
                subcategory_to_delete = st.selectbox("Select Subcategory to Delete", subcategories_df['Subcategory Name'].tolist() if 'Subcategory Name' in subcategories_df.columns else [])
                if st.button("Delete Subcategory"):
                    idx = subcategories_df[subcategories_df['Subcategory Name'] == subcategory_to_delete].index[0]
                    if db.delete_row(SHEETS['subcategories'], idx + 1):
                        st.success("Subcategory deleted!")
                        st.rerun()
        else:
            st.info("No subcategories found")
    
    with tab2:
        categories_df = db.read_data(SHEETS['categories'])
        with st.form("subcategory_form"):
            category_name = st.selectbox("Category *", categories_df['Category Name'].tolist() if not categories_df.empty and 'Category Name' in categories_df.columns else [])
            subcategory_name = st.text_input("Subcategory Name *")
            subcategory_code = st.text_input("Subcategory Code")
            subcategory_description = st.text_area("Description")
            submit = st.form_submit_button("Save Subcategory")
            
            if submit:
                if subcategory_name and category_name:
                    subcategory_data = {
                        'Category': category_name,
                        'Subcategory Name': subcategory_name,
                        'Subcategory Code': subcategory_code or subcategory_name[:3].upper(),
                        'Description': subcategory_description
                    }
                    if db.append_row(SHEETS['subcategories'], subcategory_data):
                        st.success("Subcategory saved!")
                        st.rerun()
                else:
                    st.error("Category and Subcategory Name are required")

def manage_asset_types(db):
    """Manage Asset Types"""
    st.title("🏷️ Asset Types Management")
    
    tab1, tab2 = st.tabs(["View Asset Types", "Add/Edit Asset Type"])
    
    with tab1:
        asset_types_df = db.read_data(SHEETS['asset_types'])
        if not asset_types_df.empty:
            st.dataframe(asset_types_df, use_container_width=True)
            
            if len(asset_types_df) > 0:
                st.subheader("Delete Asset Type")
                asset_type_to_delete = st.selectbox("Select Asset Type to Delete", asset_types_df['Asset Type'].tolist() if 'Asset Type' in asset_types_df.columns else [])
                if st.button("Delete Asset Type"):
                    idx = asset_types_df[asset_types_df['Asset Type'] == asset_type_to_delete].index[0]
                    if db.delete_row(SHEETS['asset_types'], idx + 1):
                        st.success("Asset Type deleted!")
                        st.rerun()
        else:
            st.info("No asset types found")
    
    with tab2:
        with st.form("asset_type_form"):
            asset_type = st.text_input("Asset Type *")
            asset_type_description = st.text_area("Description")
            submit = st.form_submit_button("Save Asset Type")
            
            if submit:
                if asset_type:
                    asset_type_data = {
                        'Asset Type': asset_type,
                        'Description': asset_type_description
                    }
                    if db.append_row(SHEETS['asset_types'], asset_type_data):
                        st.success("Asset Type saved!")
                        st.rerun()
                else:
                    st.error("Asset Type is required")

def manage_brands(db):
    """Manage Brands"""
    st.title("🏢 Brands Management")
    
    tab1, tab2 = st.tabs(["View Brands", "Add/Edit Brand"])
    
    with tab1:
        brands_df = db.read_data(SHEETS['brands'])
        if not brands_df.empty:
            st.dataframe(brands_df, use_container_width=True)
            
            if len(brands_df) > 0:
                st.subheader("Delete Brand")
                brand_to_delete = st.selectbox("Select Brand to Delete", brands_df['Brand Name'].tolist() if 'Brand Name' in brands_df.columns else [])
                if st.button("Delete Brand"):
                    idx = brands_df[brands_df['Brand Name'] == brand_to_delete].index[0]
                    if db.delete_row(SHEETS['brands'], idx + 1):
                        st.success("Brand deleted!")
                        st.rerun()
        else:
            st.info("No brands found")
    
    with tab2:
        with st.form("brand_form"):
            brand_name = st.text_input("Brand Name *")
            brand_description = st.text_area("Description")
            submit = st.form_submit_button("Save Brand")
            
            if submit:
                if brand_name:
                    brand_data = {
                        'Brand Name': brand_name,
                        'Description': brand_description
                    }
                    if db.append_row(SHEETS['brands'], brand_data):
                        st.success("Brand saved!")
                        st.rerun()
                else:
                    st.error("Brand Name is required")

def manage_assets(db):
    """Manage Assets"""
    st.title("📦 Assets Management")
    
    tab1, tab2, tab3 = st.tabs(["View Assets", "Add Asset", "Edit Asset"])
    
    with tab1:
        assets_df = db.read_data(SHEETS['assets'])
        if not assets_df.empty:
            st.dataframe(assets_df, use_container_width=True)
            
            if len(assets_df) > 0:
                st.subheader("Delete Asset")
                asset_to_delete = st.selectbox("Select Asset to Delete", assets_df['Asset Code'].tolist() if 'Asset Code' in assets_df.columns else [])
                if st.button("Delete Asset"):
                    idx = assets_df[assets_df['Asset Code'] == asset_to_delete].index[0]
                    if db.delete_row(SHEETS['assets'], idx + 1):
                        st.success("Asset deleted!")
                        st.rerun()
        else:
            st.info("No assets found")
    
    with tab2:
        # Get dropdown options
        categories_df = db.read_data(SHEETS['categories'])
        subcategories_df = db.read_data(SHEETS['subcategories'])
        brands_df = db.read_data(SHEETS['brands'])
        locations_df = db.read_data(SHEETS['locations'])
        
        with st.form("asset_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                item_name = st.text_input("Item Name *")
                asset_category = st.selectbox("Asset Category *", categories_df['Category Name'].tolist() if not categories_df.empty and 'Category Name' in categories_df.columns else [])
                asset_subcategory = st.selectbox("Asset Subcategory", subcategories_df[subcategories_df.get('Category', '') == asset_category]['Subcategory Name'].tolist() if not subcategories_df.empty and asset_category else [])
                brand = st.selectbox("Brand", [''] + brands_df['Brand Name'].tolist() if not brands_df.empty and 'Brand Name' in brands_df.columns else [])
                asset_description = st.text_area("Asset Description")
                amount = st.number_input("Amount", min_value=0.0, value=0.0)
            
            with col2:
                location = st.selectbox("Location *", locations_df['Location Name'].tolist() if not locations_df.empty and 'Location Name' in locations_df.columns else [])
                date_of_purchase = st.date_input("Date of Purchase")
                warranty = st.text_input("Warranty (e.g., 1 Year)")
                department = st.text_input("Department")
                ownership = st.selectbox("Ownership", [''] + OWNERSHIP_OPTIONS)
                asset_status = st.selectbox("Asset Status", ASSET_STATUS_OPTIONS)
                image_file = st.file_uploader("Image Attachment", type=['png', 'jpg', 'jpeg'])
                document_file = st.file_uploader("Document Attachment", type=['pdf', 'doc', 'docx'])
            
            submit = st.form_submit_button("Save Asset")
            
            if submit:
                if item_name and asset_category and location:
                    # Generate asset code
                    category_code = categories_df[categories_df['Category Name'] == asset_category]['Category Code'].iloc[0] if not categories_df.empty and 'Category Code' in categories_df.columns else ''
                    subcategory_code = subcategories_df[(subcategories_df['Category'] == asset_category) & (subcategories_df['Subcategory Name'] == asset_subcategory)]['Subcategory Code'].iloc[0] if asset_subcategory and not subcategories_df.empty and 'Subcategory Code' in subcategories_df.columns else ''
                    
                    # Get existing asset codes to ensure uniqueness
                    existing_assets_df = db.read_data(SHEETS['assets'])
                    existing_codes = existing_assets_df['Asset Code'].tolist() if not existing_assets_df.empty and 'Asset Code' in existing_assets_df.columns else []
                    
                    asset_code = generate_asset_code('AST', category_code, subcategory_code, existing_codes)
                    
                    # Handle file uploads
                    image_data = None
                    document_data = None
                    if image_file:
                        image_data = image_file.read()
                    if document_file:
                        document_data = document_file.read()
                    
                    asset_data = {
                        'Asset Code': asset_code,
                        'Item Name': item_name,
                        'Asset Category': asset_category,
                        'Asset Subcategory': asset_subcategory or '',
                        'Brand': brand or '',
                        'Asset Description': asset_description,
                        'Amount': str(amount),
                        'Location': location,
                        'Date of Purchase': str(date_of_purchase) if date_of_purchase else '',
                        'Warranty': warranty,
                        'Department': department,
                        'Ownership': ownership or '',
                        'Asset Status': asset_status,
                        'Image': 'Yes' if image_data else 'No',
                        'Document': 'Yes' if document_data else 'No',
                        'Created At': str(datetime.now())
                    }
                    
                    if db.append_row(SHEETS['assets'], asset_data):
                        st.success(f"Asset saved! Asset Code: {asset_code}")
                        # Show barcode
                        barcode_img = generate_barcode(asset_code)
                        if barcode_img:
                            st.image(barcode_img, caption=f"Barcode: {asset_code}")
                        st.rerun()
                else:
                    st.error("Item Name, Asset Category, and Location are required")
    
    with tab3:
        assets_df = db.read_data(SHEETS['assets'])
        if not assets_df.empty:
            asset_to_edit = st.selectbox("Select Asset to Edit", assets_df['Asset Code'].tolist() if 'Asset Code' in assets_df.columns else [])
            if asset_to_edit:
                asset_row = assets_df[assets_df['Asset Code'] == asset_to_edit].iloc[0]
                
                categories_df = db.read_data(SHEETS['categories'])
                subcategories_df = db.read_data(SHEETS['subcategories'])
                brands_df = db.read_data(SHEETS['brands'])
                locations_df = db.read_data(SHEETS['locations'])
                
                with st.form("edit_asset_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        item_name = st.text_input("Item Name *", value=asset_row.get('Item Name', ''))
                        asset_category = st.selectbox("Asset Category *", categories_df['Category Name'].tolist() if not categories_df.empty else [], index=categories_df[categories_df['Category Name'] == asset_row.get('Asset Category', '')].index[0] if not categories_df.empty and asset_row.get('Asset Category') in categories_df['Category Name'].values else 0)
                        asset_subcategory = st.selectbox("Asset Subcategory", [''] + subcategories_df[subcategories_df.get('Category', '') == asset_category]['Subcategory Name'].tolist() if not subcategories_df.empty else [], index=0)
                        brand = st.selectbox("Brand", [''] + brands_df['Brand Name'].tolist() if not brands_df.empty else [], index=0)
                        asset_description = st.text_area("Asset Description", value=asset_row.get('Asset Description', ''))
                        amount = st.number_input("Amount", min_value=0.0, value=float(asset_row.get('Amount', 0)) if asset_row.get('Amount') else 0.0)
                    
                    with col2:
                        location = st.selectbox("Location *", locations_df['Location Name'].tolist() if not locations_df.empty else [], index=locations_df[locations_df['Location Name'] == asset_row.get('Location', '')].index[0] if not locations_df.empty and asset_row.get('Location') in locations_df['Location Name'].values else 0)
                        date_of_purchase = st.date_input("Date of Purchase", value=pd.to_datetime(asset_row.get('Date of Purchase', datetime.now())).date() if asset_row.get('Date of Purchase') else datetime.now().date())
                        warranty = st.text_input("Warranty", value=asset_row.get('Warranty', ''))
                        department = st.text_input("Department", value=asset_row.get('Department', ''))
                        ownership = st.selectbox("Ownership", [''] + OWNERSHIP_OPTIONS, index=OWNERSHIP_OPTIONS.index(asset_row.get('Ownership', '')) + 1 if asset_row.get('Ownership') in OWNERSHIP_OPTIONS else 0)
                        asset_status = st.selectbox("Asset Status", ASSET_STATUS_OPTIONS, index=ASSET_STATUS_OPTIONS.index(asset_row.get('Asset Status', 'Active')) if asset_row.get('Asset Status') in ASSET_STATUS_OPTIONS else 0)
                    
                    submit = st.form_submit_button("Update Asset")
                    
                    if submit:
                        if item_name and asset_category and location:
                            asset_data = {
                                'Asset Code': asset_to_edit,
                                'Item Name': item_name,
                                'Asset Category': asset_category,
                                'Asset Subcategory': asset_subcategory or '',
                                'Brand': brand or '',
                                'Asset Description': asset_description,
                                'Amount': str(amount),
                                'Location': location,
                                'Date of Purchase': str(date_of_purchase) if date_of_purchase else '',
                                'Warranty': warranty,
                                'Department': department,
                                'Ownership': ownership or '',
                                'Asset Status': asset_status
                            }
                            
                            idx = assets_df[assets_df['Asset Code'] == asset_to_edit].index[0]
                            if db.update_row(SHEETS['assets'], idx + 1, asset_data):
                                st.success("Asset updated!")
                                st.rerun()
                        else:
                            st.error("Item Name, Asset Category, and Location are required")

def search_assets(db):
    """Search Assets"""
    st.title("🔍 Search Assets")
    
    assets_df = db.read_data(SHEETS['assets'])
    
    if assets_df.empty:
        st.info("No assets found")
        return
    
    search_term = st.text_input("Search by Asset Code, Item Name, or Description")
    
    if search_term:
        filtered = assets_df[
            assets_df['Asset Code'].str.contains(search_term, case=False, na=False) |
            assets_df['Item Name'].str.contains(search_term, case=False, na=False) |
            assets_df.get('Asset Description', '').str.contains(search_term, case=False, na=False)
        ]
        st.dataframe(filtered, use_container_width=True)
        
        if len(filtered) > 0:
            selected_asset = st.selectbox("Select Asset to View", filtered['Asset Code'].tolist())
            if selected_asset:
                asset = filtered[filtered['Asset Code'] == selected_asset].iloc[0]
                st.subheader("Asset Details")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Asset Code:** {asset.get('Asset Code', '')}")
                    st.write(f"**Item Name:** {asset.get('Item Name', '')}")
                    st.write(f"**Category:** {asset.get('Asset Category', '')}")
                    st.write(f"**Subcategory:** {asset.get('Asset Subcategory', '')}")
                    st.write(f"**Brand:** {asset.get('Brand', '')}")
                    st.write(f"**Location:** {asset.get('Location', '')}")
                with col2:
                    st.write(f"**Amount:** ${asset.get('Amount', '0')}")
                    st.write(f"**Status:** {asset.get('Asset Status', '')}")
                    st.write(f"**Department:** {asset.get('Department', '')}")
                    st.write(f"**Ownership:** {asset.get('Ownership', '')}")
                    st.write(f"**Warranty:** {asset.get('Warranty', '')}")
                
                # Show barcode
                barcode_img = generate_barcode(asset.get('Asset Code', ''))
                if barcode_img:
                    st.image(barcode_img, caption=f"Barcode: {asset.get('Asset Code', '')}")
    else:
        st.dataframe(assets_df, use_container_width=True)

def barcode_scanner(db):
    """Barcode Scanner"""
    st.title("📷 Barcode Scanner")
    
    st.info("Enter barcode manually or use camera scanner")
    
    barcode_input = st.text_input("Enter Barcode to Search")
    
    if barcode_input:
        assets_df = db.read_data(SHEETS['assets'])
        if not assets_df.empty:
            asset = assets_df[assets_df['Asset Code'] == barcode_input]
            if not asset.empty:
                asset = asset.iloc[0]
                st.success("Asset Found!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Asset Code:** {asset.get('Asset Code', '')}")
                    st.write(f"**Item Name:** {asset.get('Item Name', '')}")
                    st.write(f"**Category:** {asset.get('Asset Category', '')}")
                    st.write(f"**Location:** {asset.get('Location', '')}")
                    st.write(f"**Status:** {asset.get('Asset Status', '')}")
                
                with col2:
                    barcode_img = generate_barcode(barcode_input)
                    if barcode_img:
                        st.image(barcode_img, caption=f"Barcode: {barcode_input}")
            else:
                st.error("Asset not found")

def print_barcodes(db):
    """Print Barcodes"""
    st.title("🖨️ Print Barcodes")
    
    assets_df = db.read_data(SHEETS['assets'])
    
    if assets_df.empty:
        st.info("No assets found")
        return
    
    selected_assets = st.multiselect("Select Assets to Print", assets_df['Asset Code'].tolist() if 'Asset Code' in assets_df.columns else [])
    
    if selected_assets:
        st.subheader("Selected Assets for Printing")
        for asset_code in selected_assets:
            asset = assets_df[assets_df['Asset Code'] == asset_code].iloc[0]
            label = create_barcode_label(
                asset_code,
                asset.get('Item Name', ''),
                asset.get('Location', '')
            )
            if label:
                st.image(label, caption=f"Asset: {asset.get('Item Name', '')}")
        
        st.info("Print these labels using your browser's print function (Ctrl+P)")

def manage_asset_movements(db):
    """Manage Asset Movements"""
    st.title("🚚 Asset Movements")
    
    tab1, tab2 = st.tabs(["View Movements", "Move Asset"])
    
    with tab1:
        movements_df = db.read_data(SHEETS['asset_movements'])
        if not movements_df.empty:
            st.dataframe(movements_df, use_container_width=True)
        else:
            st.info("No movements recorded")
    
    with tab2:
        assets_df = db.read_data(SHEETS['assets'])
        locations_df = db.read_data(SHEETS['locations'])
        
        if assets_df.empty:
            st.info("No assets available")
        elif locations_df.empty:
            st.info("No locations available")
        else:
            with st.form("movement_form"):
                asset_code = st.selectbox("Select Asset *", assets_df['Asset Code'].tolist() if 'Asset Code' in assets_df.columns else [])
                current_location = assets_df[assets_df['Asset Code'] == asset_code]['Location'].iloc[0] if asset_code else ''
                st.info(f"Current Location: {current_location}")
                
                to_location = st.selectbox("Move To Location *", locations_df['Location Name'].tolist() if 'Location Name' in locations_df.columns else [])
                movement_reason = st.text_area("Reason for Movement")
                movement_date = st.date_input("Movement Date", value=datetime.now().date())
                
                submit = st.form_submit_button("Move Asset")
                
                if submit:
                    if asset_code and to_location:
                        # Record movement
                        movement_data = {
                            'Asset Code': asset_code,
                            'From Location': current_location,
                            'To Location': to_location,
                            'Reason': movement_reason,
                            'Date': str(movement_date),
                            'Moved By': st.session_state.username,
                            'Created At': str(datetime.now())
                        }
                        
                        if db.append_row(SHEETS['asset_movements'], movement_data):
                            # Update asset location
                            idx = assets_df[assets_df['Asset Code'] == asset_code].index[0]
                            asset_row = assets_df.iloc[idx].to_dict()
                            asset_row['Location'] = to_location
                            if db.update_row(SHEETS['assets'], idx + 1, asset_row):
                                st.success("Asset moved successfully!")
                                st.rerun()
                    else:
                        st.error("Asset Code and To Location are required")

# Main execution
if __name__ == "__main__":
    if not check_authentication():
        login_page()
    else:
        main_app()

