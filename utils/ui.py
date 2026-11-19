"""Reusable Streamlit UI helpers."""

import streamlit as st


def show_page_heading(title: str, description: str) -> None:
    st.title(title)
    st.caption(description)


def save_and_show_error(error: Exception, context: str) -> None:
    st.error(f"{context}: {error}")
