LOGIN_URL = "http://localhost:3000/login"
BOOKINGS_URL = "http://localhost:3000/getBookingsByUser"


# utils.py
import streamlit as st

def hide_sidebar_and_header():

    st.set_page_config( initial_sidebar_state="collapsed")
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none !important;
            }

            section[data-testid="stSidebarNav"] {
                display: none !important;
            }

            header[data-testid="stHeader"] {
                display: none !important;
            }

            [data-testid="stAppViewContainer"] > .main {
                margin-left: 0rem;
            }
        </style>
    """, unsafe_allow_html=True)
