import streamlit as st
import pandas as pd
from datetime import datetime, time
from data_handler import DataHandler
from visualizations import create_timeline, create_activity_distribution

# Page configuration
st.set_page_config(
    page_title="Vasig's Life Log",
    page_icon="📝",
    layout="wide"
)

# Load custom CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize data handler
@st.cache_resource
def get_data_handler():
    return DataHandler()

data_handler = get_data_handler()

# Main header with current status
current_status = data_handler.get_current_status()
st.markdown(f'<h1 class="main-header">Vasig is {current_status} right now</h1>', unsafe_allow_html=True)

# Admin login
with st.sidebar:
    st.title("Admin Access")
    password = st.text_input("Enter password", type="password")
    is_admin = password == "admin"  # Simple password protection for demo

# Main content
if is_admin:
    st.sidebar.success("Admin access granted!")

    # Entry form
    st.markdown('<div class="entry-form">', unsafe_allow_html=True)
    st.subheader("Log New Activity")

    col1, col2 = st.columns(2)
    with col1:
        activity = st.text_input("What are you doing?")
    with col2:
        category = st.selectbox("Category", ["Work", "Personal", "Exercise", "Entertainment", "Other"])

    if st.button("Log Activity"):
        if activity:
            data_handler.add_entry(activity, category)
            st.success("Activity logged successfully!")
            # Force refresh to show new status
            st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Search functionality
st.markdown('<div class="search-container">', unsafe_allow_html=True)
st.subheader("Search Historical Activities")
col1, col2 = st.columns(2)
with col1:
    search_date = st.date_input("Select Date", datetime.now())
with col2:
    search_time = st.time_input("Select Time", time(12, 0))

if st.button("Search"):
    result = data_handler.search_activity(search_date, search_time)
    if result is not None:
        st.info(f"At {result['timestamp']}, Vasig was: {result['activity']} ({result['category']})")
    else:
        st.error("No activity found for the selected time.")
st.markdown('</div>', unsafe_allow_html=True)

# Visualizations
st.subheader("Activity Timeline")
activities_df = data_handler.get_all_activities()
timeline = create_timeline(activities_df)
if timeline:
    st.altair_chart(timeline, use_container_width=True)
else:
    st.info("No data available for timeline visualization")

st.subheader("Activity Distribution")
activity_stats = data_handler.get_activity_stats()
if not activity_stats.empty:
    distribution_chart = create_activity_distribution(activity_stats)
    st.plotly_chart(distribution_chart, use_container_width=True)
else:
    st.info("No data available for activity distribution")