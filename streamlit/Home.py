import streamlit as st

st.set_page_config( initial_sidebar_state="collapsed")
# Inject CSS to hide sidebar navigation

left, middle, right = st.columns(3)
if left.button("Book Sitter", icon=":material/ink_pen:", width="stretch"):
    st.switch_page("pages/1_BookSitter.py")
if middle.button("Ask Me about Pets", icon=":material/question_mark:", width="stretch"):
    st.switch_page("pages/2_AskMe.py")
if right.button("View Bookings", icon=":material/mood:", width="stretch"):
    st.switch_page("pages/3_ViewBookings.py")