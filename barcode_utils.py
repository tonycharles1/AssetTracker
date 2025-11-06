"""
Barcode Utilities Module
"""
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import io
import streamlit as st
from datetime import datetime

def generate_barcode(code, format_type='code128'):
    """Generate barcode image"""
    try:
        if format_type == 'code128':
            code_class = barcode.get_barcode_class('code128')
        elif format_type == 'code39':
            code_class = barcode.get_barcode_class('code39')
        else:
            code_class = barcode.get_barcode_class('code128')
        
        barcode_instance = code_class(code, writer=ImageWriter())
        buffer = io.BytesIO()
        barcode_instance.write(buffer)
        buffer.seek(0)
        return Image.open(buffer)
    except Exception as e:
        st.error(f"Error generating barcode: {str(e)}")
        return None

def generate_asset_code(prefix='AST', category_code='', subcategory_code='', existing_codes=None):
    """Generate unique asset code"""
    import random
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = str(random.randint(1000, 9999))
    
    if category_code and subcategory_code:
        code = f"{prefix}-{category_code}-{subcategory_code}-{timestamp[-6:]}-{random_suffix}"
    else:
        code = f"{prefix}-{timestamp}-{random_suffix}"
    
    # Ensure uniqueness
    if existing_codes and code in existing_codes:
        code = f"{code}-{random.randint(10, 99)}"
    
    return code

def create_barcode_label(asset_code, item_name, location=''):
    """Create a printable barcode label"""
    barcode_img = generate_barcode(asset_code)
    if barcode_img:
        # Create label with text
        label = Image.new('RGB', (400, 200), 'white')
        # Paste barcode
        barcode_img.thumbnail((300, 100))
        label.paste(barcode_img, (50, 20))
        
        # Add text
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(label)
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 130), f"Code: {asset_code}", fill='black', font=font)
        draw.text((50, 150), f"Item: {item_name[:30]}", fill='black', font=font)
        if location:
            draw.text((50, 170), f"Loc: {location[:20]}", fill='black', font=font)
        
        return label
    return None

