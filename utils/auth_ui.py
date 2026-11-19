"""Streamlit account gate and session helpers."""

import time

import streamlit as st

from services.auth_service import authenticate_user, register_user

SESSION_TIMEOUT_SECONDS = 30 * 60
SESSION_USER_KEY = "authenticated_user"
SESSION_ACTIVITY_KEY = "auth_last_activity"


def current_user() -> dict | None:
    user = st.session_state.get(SESSION_USER_KEY)
    if not isinstance(user, dict) or not isinstance(user.get("id"), int):
        return None
    last_activity = st.session_state.get(SESSION_ACTIVITY_KEY, time.monotonic())
    if time.monotonic() - last_activity > SESSION_TIMEOUT_SECONDS:
        logout_user()
        return None
    st.session_state[SESSION_ACTIVITY_KEY] = time.monotonic()
    return user


def logout_user() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def show_login() -> None:
    st.title("🌱 AgroMind AI")
    st.subheader("Sign in to your farm workspace")
    st.caption("Your reports are stored locally and are visible only to your account.")
    sign_in_tab, register_tab = st.tabs(["Sign in", "Create account"])

    with sign_in_tab:
        with st.form("sign_in_form"):
            email = st.text_input("Email", autocomplete="email")
            password = st.text_input("Password", type="password", autocomplete="current-password")
            submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
        if submitted:
            try:
                user, error = authenticate_user(email, password)
                if user:
                    st.session_state[SESSION_USER_KEY] = user
                    st.session_state[SESSION_ACTIVITY_KEY] = time.monotonic()
                    st.rerun()
                st.error(error or "Could not sign in.")
            except ValueError as exc:
                st.error(str(exc))

    with register_tab:
        st.info("Use a passphrase of at least 12 characters. Avoid reusing a password from another site.")
        with st.form("register_form"):
            email = st.text_input("Email address", autocomplete="email", key="register_email")
            password = st.text_input("Password", type="password", autocomplete="new-password")
            confirm = st.text_input("Confirm password", type="password", autocomplete="new-password")
            submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)
        if submitted:
            if password != confirm:
                st.error("The passwords do not match.")
            else:
                try:
                    st.session_state[SESSION_USER_KEY] = register_user(email, password)
                    st.session_state[SESSION_ACTIVITY_KEY] = time.monotonic()
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))

