"""
Dashboard Module with Graphs
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from google_sheets import GoogleSheetsDB
from config import SHEETS

def show_dashboard(db):
    """Display dashboard with graphs and statistics"""
    st.title("📊 Asset Tracker Dashboard")
    
    # Get data
    assets_df = db.read_data(SHEETS['assets'])
    locations_df = db.read_data(SHEETS['locations'])
    categories_df = db.read_data(SHEETS['categories'])
    movements_df = db.read_data(SHEETS['asset_movements'])
    
    if assets_df.empty:
        st.info("No assets found. Add assets to see dashboard statistics.")
        return
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_assets = len(assets_df)
    active_assets = len(assets_df[assets_df.get('Asset Status', '').str.contains('Active', case=False, na=False)])
    total_value = pd.to_numeric(assets_df.get('Amount', 0), errors='coerce').sum()
    total_locations = len(locations_df) if not locations_df.empty else 0
    
    with col1:
        st.metric("Total Assets", total_assets)
    with col2:
        st.metric("Active Assets", active_assets)
    with col3:
        st.metric("Total Value", f"${total_value:,.2f}" if total_value > 0 else "$0.00")
    with col4:
        st.metric("Locations", total_locations)
    
    st.divider()
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Assets by Status")
        if 'Asset Status' in assets_df.columns:
            status_counts = assets_df['Asset Status'].value_counts()
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Asset Status Distribution"
            )
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("Asset Status data not available")
    
    with col2:
        st.subheader("Assets by Location")
        if 'Location' in assets_df.columns and not assets_df['Location'].isna().all():
            location_counts = assets_df['Location'].value_counts().head(10)
            fig_location = px.bar(
                x=location_counts.index,
                y=location_counts.values,
                title="Top 10 Locations by Asset Count",
                labels={'x': 'Location', 'y': 'Count'}
            )
            st.plotly_chart(fig_location, use_container_width=True)
        else:
            st.info("Location data not available")
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Assets by Category")
        if 'Asset Category' in assets_df.columns:
            category_counts = assets_df['Asset Category'].value_counts().head(10)
            fig_category = px.bar(
                x=category_counts.values,
                y=category_counts.index,
                orientation='h',
                title="Top 10 Categories",
                labels={'x': 'Count', 'y': 'Category'}
            )
            st.plotly_chart(fig_category, use_container_width=True)
        else:
            st.info("Category data not available")
    
    with col2:
        st.subheader("Assets Value by Department")
        if 'Department' in assets_df.columns:
            dept_value = assets_df.groupby('Department').apply(
                lambda x: pd.to_numeric(x.get('Amount', 0), errors='coerce').sum()
            ).sort_values(ascending=False).head(10)
            fig_dept = px.bar(
                x=dept_value.index,
                y=dept_value.values,
                title="Top 10 Departments by Asset Value",
                labels={'x': 'Department', 'y': 'Value ($)'}
            )
            st.plotly_chart(fig_dept, use_container_width=True)
        else:
            st.info("Department data not available")
    
    # Recent Movements
    if not movements_df.empty and len(movements_df) > 0:
        st.divider()
        st.subheader("Recent Asset Movements")
        recent_movements = movements_df.tail(10)
        st.dataframe(recent_movements[['Asset Code', 'From Location', 'To Location', 'Date']] if 'Date' in recent_movements.columns else recent_movements, use_container_width=True)

