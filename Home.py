import streamlit as st
from shared_utils import init_session_state, render_sidebar


def main():
    st.set_page_config(
        page_icon=":student:",
        page_title="Talent Tracing",
        layout="centered",
    )

    init_session_state()
    render_sidebar()

    col1, col2 = st.columns([1, 4])
    col1.image("images/tt-logo.png")
    col2.title("Welcome to Talent Tracing!")

    st.write("""
    This tool will help you discover career paths that match your unique profile.
    We'll have a conversation to understand your:
    - **Abilities**: What you're naturally good at
    - **Interests**: What you enjoy doing
    - **Knowledge**: What you've learned
    - **Skills**: What you've practiced and developed

    Ready to start? Click below to begin your assessment!
    """)

    if st.button("🔥 Start Assessment"):
        st.switch_page("pages/1_Assessment.py")


if __name__ == "__main__":
    main()
