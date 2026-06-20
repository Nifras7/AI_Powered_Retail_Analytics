import streamlit as st

def show_dashboard(df):

    st.subheader("Analytics Dashboard")

    st.dataframe(df)