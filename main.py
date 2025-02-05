import streamlit as st
import pandas as pd
from datetime import datetime, time
from data_handler import DataHandler
from visualizations import create_activity_distribution

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

# Main header with current status and duration
current_status, duration = data_handler.get_current_status()
hours = int(duration.total_seconds() // 3600)
minutes = int((duration.total_seconds() % 3600) // 60)
st.markdown(f'<h1 class="main-header">Vasig is {current_status} right now</h1>', unsafe_allow_html=True)
if current_status != "unavailable":
    st.markdown(f'<h2 class="status-header">for {hours} hours {minutes} minutes</h2>', unsafe_allow_html=True)

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
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Recent Activities List
st.subheader("Recent Activities")
activities = data_handler.get_recent_activities()
if not activities.empty:
    st.markdown('<div class="activity-list">', unsafe_allow_html=True)

    for _, row in activities.iterrows():
        cols = st.columns([2, 2, 2, 2, 1])
        with cols[0]:
            st.write(row['timestamp'])
        with cols[1]:
            st.write(row['activity'])
        with cols[2]:
            st.write(row['category'])
        with cols[3]:
            st.write(row['duration'])
        if is_admin:
            with cols[4]:
                if st.button("🗑️", key=f"delete_{row['id']}"):
                    data_handler.delete_entry(row['id'])
                    st.success("Entry deleted!")
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No activities logged yet")

# Activity Distribution
st.subheader("Time Distribution")
activity_stats = data_handler.get_activity_stats()
if not activity_stats.empty:
    distribution_chart = create_activity_distribution(activity_stats)
    st.plotly_chart(distribution_chart, use_container_width=True)
else:
    st.info("No data available for activity distribution")