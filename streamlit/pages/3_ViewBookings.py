import streamlit as st
import os
import pandas as pd
import json
from util import LOGIN_URL, BOOKINGS_URL 
import streamlit as st
import requests

st.page_link("Home.py", label="<- Home")

st.set_page_config( initial_sidebar_state="collapsed")
# Session state to track user login and user_id
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "login_error" not in st.session_state:
    st.session_state.login_error = None

# Function to log in via POST
def login_user(email: str, password: str):
    url = LOGIN_URL
    payload = {
        "email": email,
        "password": password
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("user", {}).get("id")
  # Adjust key as per your backend's response
    except requests.exceptions.RequestException as e:
        st.session_state.login_error = f"Login failed: {e}"
        return None

# UI for login
if not st.session_state.user_id:
    st.subheader("🔐 Login to continue")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_id = login_user(email, password)
        if user_id:
            st.session_state.user_id = user_id
        else:
            st.error(st.session_state.login_error or "Invalid credentials")

# After login
if st.session_state.user_id:
    st.success(f"Logged in as user: {st.session_state.user_id}")

    # Fetch bookings
    if st.button("View My Bookings"):
        bookings_url = BOOKINGS_URL
        params = {"user_id": st.session_state.user_id}
        try:
            response = requests.get(bookings_url, params=params)
            response.raise_for_status()
            data = response.json()

            bookings = data.get("data", [])
            
            st.title("📋 Your Bookings")

            if not bookings:
                st.info("No bookings found.")
            else:
                for booking in bookings:
                    sitter = booking.get("sitter_profiles", {})
                    st.markdown("----")
                    st.subheader(f"🐾 Sitter: {sitter.get('name', 'N/A')}")

                    st.write(f"📍 **Location:** {sitter.get('location', 'N/A')}")
                    st.write(f"📞 **Contact:** {sitter.get('phone_number', 'Not Provided')}")
                    st.write(f"💼 **Service Type:** {booking.get('service_type', 'N/A')}")
                    st.write(f"📅 **From:** {booking.get('start_date')} to {booking.get('end_date')}")
                    st.write(f"🐕 **Pet:** {booking.get('pet_name')} ({booking.get('pet_breed')})")
                    st.write(f"💰 **Base Price (Subtotal):** ₹{booking.get('subtotal')}")
                    st.write(f"➕ **Service Fee:** ₹{booking.get('service_fee')}")
                    st.write(f"💳 **Total Amount:** ₹{booking.get('total_amount')}")
                    st.write(f"🚦 **Status:** `{booking.get('status').capitalize()}`")

                    # Optional: Show service add-ons
                    st.markdown("**🔧 Add-on Services**")
                    st.write(f"- Daily Photos: {'✅' if booking.get('daily_photos') else '❌'}")
                    st.write(f"- GPS Tracking: {'✅' if booking.get('gps_tracking') else '❌'}")
                    st.write(f"- Basic Grooming: {'✅' if booking.get('basic_grooming') else '❌'}")

                    st.markdown(f"📓 **Special Instructions:** _{booking.get('special_instructions', '')}_")
                    st.markdown(f"📒 **Booking Notes:** _{booking.get('booking_notes', '')}_")
                    st.markdown("----")
        except Exception as e:
            st.error(f"Error fetching bookings: {e}")


#     # Simulate receiving a JSON response from an API
# api_response_json_string = """
#     [
#         {"Product": "Laptop", "Price": 1200, "Quantity": 5},
#         {"Product": "Mouse", "Price": 25, "Quantity": 50},
#         {"Product": "Keyboard", "Price": 75, "Quantity": 20}
#     ]
#     """

#     # Parse JSON and create DataFrame
# data = json.loads(api_response_json_string)
# df = pd.DataFrame(data)

#     # Display in the chat window
# st.write("Here is the requested data:")
# st.write(df)