import streamlit as st
import requests
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Aadhaar Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Helper Functions
@st.cache_data(ttl=60)
def fetch_summary(dataset_type="enrolment", state=None, district=None):
    """Fetch summary statistics from API"""
    try:
        params = {"dataset_type": dataset_type}
        if state:
            params["state"] = state
        if district:
            params["district"] = district
            
        response = requests.get(f"{API_BASE_URL}/summary", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch summary: {e}")
        return None

@st.cache_data(ttl=60)
def fetch_trends_state(state=None, dataset_type="enrolment"):
    """Fetch state trends from API"""
    try:
        url = f"{API_BASE_URL}/trends/state"
        params = {"dataset_type": dataset_type}
        if state:
            params["state"] = state
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch state trends: {e}")
        return []

@st.cache_data(ttl=60)
def fetch_trends_district(district=None, dataset_type="enrolment"):
    """Fetch district trends from API"""
    try:
        url = f"{API_BASE_URL}/trends/district"
        params = {"dataset_type": dataset_type}
        if district:
            params["district"] = district
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch district trends: {e}")
        return []

@st.cache_data(ttl=60)
def fetch_age_comparison(dataset_type="enrolment", state=None, district=None):
    """Fetch age comparison data from API"""
    try:
        params = {"dataset_type": dataset_type}
        if state:
            params["state"] = state
        if district:
            params["district"] = district
            
        response = requests.get(f"{API_BASE_URL}/age-comparison", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch age comparison: {e}")
        return None

@st.cache_data(ttl=60)
def fetch_anomalies(dataset_type="enrolment", state=None, district=None):
    """Fetch anomalies from API"""
    try:
        params = {"dataset_type": dataset_type}
        if state:
            params["state"] = state
        if district:
            params["district"] = district
            
        response = requests.get(f"{API_BASE_URL}/anomalies", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch anomalies: {e}")
        return []

@st.cache_data(ttl=60)
def fetch_state_options(dataset_type="enrolment"):
    """Fetch unique states from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/options/states", params={"dataset_type": dataset_type})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return []

@st.cache_data(ttl=60)
def fetch_district_options(state=None, dataset_type="enrolment"):
    """Fetch unique districts from API"""
    try:
        url = f"{API_BASE_URL}/options/districts"
        params = {"dataset_type": dataset_type}
        if state:
            params["state"] = state
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return []

def sync_api_data(limit, state=None, district=None, fetch_all=False, dataset_type="enrolment"):
    """Trigger API sync"""
    try:
        params = {"limit": limit, "fetch_all": fetch_all, "dataset_type": dataset_type}
        if state:
            params["state"] = state
        if district:
            params["district"] = district
        
        response = requests.post(f"{API_BASE_URL}/sync-api", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Sync failed: {e}")
        return None

def sync_local_data(dataset_type="enrolment"):
    """Trigger Local sync"""
    try:
        response = requests.post(f"{API_BASE_URL}/sync-local", params={"dataset_type": dataset_type})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Local sync failed: {e}")
        return None

def upload_csv_file(uploaded_file, dataset_type="enrolment"):
    """Upload CSV file to backend"""
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
        response = requests.post(f"{API_BASE_URL}/upload", files=files, params={"dataset_type": dataset_type})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Upload failed: {e}")
        return None

def clear_database(dataset_type="enrolment"):
    """Clear all data from database"""
    try:
        response = requests.delete(f"{API_BASE_URL}/clear-data", params={"dataset_type": dataset_type})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Clear failed: {e}")
        return None

# Sidebar - Filters
st.sidebar.header("🔍 Filters & Controls")

# --- DATASET SELECTION ---
st.sidebar.subheader("📂 Active Dataset")
dataset_map = {
    "Aadhaar Enrolment": "enrolment",
    "Aadhaar Demographic Update": "demographic",
    "Aadhaar Biometric Update": "biometric"
}
selected_display_name = st.sidebar.selectbox(
    "Select Dataset", 
    options=list(dataset_map.keys()),
    index=0
)
active_dataset = dataset_map[selected_display_name]

# Main Dashboard Title
st.markdown(f'<h1 class="main-header">📊 {selected_display_name} Analytics</h1>', unsafe_allow_html=True)

# Session State Initialization
if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True
    # Auto-clear DB on first load (default enrolment)
    with st.spinner("Initializing dashboard..."):
        # clear_database("enrolment") # Maybe don't clear everything on every reload now
        pass

st.sidebar.markdown("---")
st.sidebar.subheader("🗺️ Geographic Filters")

# Filter Mode Toggle
filter_mode = st.sidebar.radio("Filter Selection Mode", ["Dropdown", "Manual"], horizontal=True)

if filter_mode == "Dropdown":
    # Fetch available options
    state_options = fetch_state_options(active_dataset)
    state_options = ["All"] + state_options if state_options else ["All"]

    filter_state = st.sidebar.selectbox("Filter by State", options=state_options)

    # Filter districts based on selected state
    if filter_state != "All":
        district_options = fetch_district_options(filter_state, active_dataset)
    else:
        district_options = fetch_district_options(dataset_type=active_dataset)
        
    district_options = ["All"] + district_options if district_options else ["All"]
    filter_district = st.sidebar.selectbox("Filter by District", options=district_options)

    # Map "All" to None for API logic
    selected_state = filter_state if filter_state != "All" else None
    selected_district = filter_district if filter_district != "All" else None
else:
    # Manual Input Mode
    selected_state = st.sidebar.text_input("Enter State Name", placeholder="e.g. Gujarat")
    selected_district = st.sidebar.text_input("Enter District Name", placeholder="e.g. Surat")
    
    # Clean up empty strings to None
    selected_state = selected_state.strip() if selected_state else None
    selected_district = selected_district.strip() if selected_district else None
    
    # For display in info messages
    filter_state = selected_state if selected_state else "All"
    filter_district = selected_district if selected_district else "All"

st.sidebar.markdown("---")

# Local Sync Section
with st.sidebar.expander("📁 Local Data Sync", expanded=True):
    st.info(f"Sync all local CSVs for {selected_display_name}")
    clear_before_local = st.checkbox("Clear existing data before sync", value=False, key="clear_local")
    if st.button("📥 Sync Local Files", type="primary"):
        with st.spinner("Syncing local data..."):
            if clear_before_local:
                clear_database(active_dataset)
            result = sync_local_data(active_dataset)
            if result:
                st.success(result.get("message", "Local sync completed!"))
                st.cache_data.clear()
                st.rerun()

st.sidebar.markdown("---")

# CSV Upload Section
with st.sidebar.expander("📤 Upload CSV File", expanded=False):
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    clear_before_upload = st.checkbox("Clear existing data before upload", value=False, key="clear_upload")
    
    if uploaded_file is not None:
        if st.button("📁 Upload & Process", type="primary", key="upload_btn"):
            with st.spinner("Processing..."):
                if clear_before_upload:
                    clear_database(active_dataset)
                
                result = upload_csv_file(uploaded_file, active_dataset)
                if result:
                    st.success(result.get("message", "Upload completed!"))
                    st.cache_data.clear()
                    st.rerun()

st.sidebar.markdown("---")

# Data Sync Section (Only for Enrolment)
if active_dataset == "enrolment":
    with st.sidebar.expander("🔄 Sync Data from API", expanded=False):
        st.info(f"Syncing data for: {filter_state} / {filter_district}")
        fetch_all = st.checkbox("Fetch All Records (ignores limit)", value=False)
        sync_limit = st.number_input("Records to fetch", min_value=10, max_value=1000, value=100, step=10, disabled=fetch_all)
        
        clear_before_sync = st.checkbox("Clear existing data before sync", value=False, key="clear_sync")
        
        if st.button("🚀 Sync Now", type="primary"):
            with st.spinner("Syncing data..."):
                if clear_before_sync:
                    clear_database(active_dataset)
                    
                # Use selected_state and selected_district from Global Filters
                result = sync_api_data(sync_limit, selected_state, selected_district, fetch_all=fetch_all, dataset_type=active_dataset)
                if result:
                    st.success(result.get("message", "Sync completed!"))
                    st.cache_data.clear()  # Clear cache to refresh data
                    st.rerun()
    st.sidebar.markdown("---")

# Clear Database Section
st.sidebar.subheader("🗑️ Data Management")
if st.sidebar.button(f"🗑️ Clear {selected_display_name} Data", type="secondary"):
    if st.sidebar.checkbox("⚠️ Confirm deletion"):
        with st.spinner("Clearing database..."):
            result = clear_database(active_dataset)
            if result:
                st.sidebar.success(result.get("message", "Database cleared!"))
                st.cache_data.clear()
                st.rerun()

if st.sidebar.button("🔄 Refresh View"):
    st.cache_data.clear()
    st.rerun()

# Main Content
# KPI Cards
kpi_title = "Enrolments" if active_dataset == "enrolment" else "Updates"
st.subheader(f"📈 {selected_display_name} KPIs")
summary = fetch_summary(active_dataset, selected_state, selected_district)

if summary:
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(f"Total {kpi_title}", f"{summary.get('total_enrolments', 0):,}")
    with col2:
        st.metric("Age 0-5", f"{summary.get('total_0_5', 0):,}")
    with col3:
        st.metric("Age 5-17", f"{summary.get('total_5_17', 0):,}")
    with col4:
        st.metric("Age 17+", f"{summary.get('total_17_plus', 0):,}")
    with col5:
        # Dynamically label top location based on filter context
        # API now returns 'top_location' and 'location_label'
        # Fallback to 'top_state' if older API response (safety)
        label = summary.get('location_label', 'Top State')
        value = summary.get('top_location', summary.get('top_state', 'N/A'))
        st.metric(label, value)

st.markdown("---")

# Charts Section
col_left, col_right = st.columns(2)

# Time-series Chart
# Time-series Chart
with col_left:
    if selected_district:
        st.subheader(f"📊 {kpi_title} Trends in {selected_district}")
        # Assuming fetch_trends_district is defined (it was in the file earlier)
        trends_data = fetch_trends_district(selected_district, active_dataset)
        color_col = 'district'
    else:
        st.subheader(f"📊 {kpi_title} Trends Over Time")
        trends_data = fetch_trends_state(selected_state, active_dataset)
        color_col = 'state'
    
    if trends_data:
        df_trends = pd.DataFrame(trends_data)
        df_trends['date'] = pd.to_datetime(df_trends['date'])
        
        # Ensure the color column exists (for safety)
        color_arg = color_col if color_col in df_trends.columns else None
        
        fig_trends = px.line(
            df_trends, 
            x='date', 
            y='enrolments',
            color=color_arg,
            title=f"Daily {kpi_title}",
            labels={'enrolments': f'Number of {kpi_title}', 'date': 'Date'}
        )
        fig_trends.update_layout(height=400)
        st.plotly_chart(fig_trends, use_container_width=True)
    else:
        st.info("No data available for the selected filters. Use the sidebar to sync data.")

# Age Group Pie Chart
with col_right:
    st.subheader("👥 Age Group Distribution")
    age_data = fetch_age_comparison(active_dataset, selected_state, selected_district)
    
    if age_data:
        age_items = []
        if age_data.get('age_0_5', 0) > 0:
            age_items.append({"Age Group": "0-5", "Count": age_data.get('age_0_5', 0)})
        age_items.append({"Age Group": "5-17", "Count": age_data.get('age_5_17', 0)})
        age_items.append({"Age Group": "17+", "Count": age_data.get('age_17_plus', 0)})
        
        age_df = pd.DataFrame(age_items)
        
        fig_age = px.pie(
            age_df,
            values='Count',
            names='Age Group',
            title=f"{kpi_title} by Age Group",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_age.update_layout(height=400)
        st.plotly_chart(fig_age, use_container_width=True)
    else:
        st.info("No age comparison data available.")

# State-wise Bar Chart
st.subheader(f"🗺️ Top States by {kpi_title}")
state_trends = fetch_trends_state(selected_state, active_dataset)

if state_trends:
    df_states = pd.DataFrame(state_trends)
    if 'state' in df_states.columns:
        state_summary = df_states.groupby('state')['enrolments'].sum().reset_index()
        state_summary = state_summary.sort_values('enrolments', ascending=False).head(10)
        
        chart_title = f"Top 10 States" if not selected_state else f"{kpi_title} for {selected_state}"
        
        fig_states = px.bar(
            state_summary,
            x='state',
            y='enrolments',
            title=chart_title,
            labels={'enrolments': f'Total {kpi_title}', 'state': 'State'},
            color='enrolments',
            color_continuous_scale='Blues'
        )
        fig_states.update_layout(
            height=400,
            xaxis={'categoryorder': 'total descending'}
        )
        st.plotly_chart(fig_states, use_container_width=True)
    else:
        st.info("No state-level data available.")

# Anomalies Table
st.subheader(f"⚠️ Activity Alerts (Low {kpi_title} Days)")
anomalies = fetch_anomalies(active_dataset, selected_state, selected_district)

if anomalies:
    df_anomalies = pd.DataFrame(anomalies)
    df_anomalies['date'] = pd.to_datetime(df_anomalies['date']).dt.date
    st.dataframe(
        df_anomalies[['date', 'district', 'total_enrolment', 'type']].head(20),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No anomalies detected.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
    <p>Aadhaar Analytics Dashboard | Unified Multi-Dataset Platform</p>
    </div>
    """,
    unsafe_allow_html=True
)
