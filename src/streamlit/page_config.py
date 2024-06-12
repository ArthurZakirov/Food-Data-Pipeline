import streamlit as st


def set_page_config():
    page_title = "Mealplan Generator"
    page_icon = "🥗"

    css = """
        <style>
            .dataframe-container, .dataframe-container * {
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
            }
        </style>
    """

    # Function to manage food constraints

    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout="wide",
    )
    st.title(f"{page_icon} {page_title}")
    return css
