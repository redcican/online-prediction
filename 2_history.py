import streamlit as st

st.title("历史数据")

st.dataframe(st.session_state.df)