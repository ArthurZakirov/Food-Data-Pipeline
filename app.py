import streamlit as st
import pandas as pd
import os
import argparse
import json
from src.streamlit.data_input import streamlit_dataset_upload
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# data_path = "data/processed/fdc_data.h5"

data_path = "data/processed/merged_rewe_fdc_insulin_time.csv"

page_title = "Nutrition Optimization Dashboard"
page_icon = ":food:"


st.set_page_config(
    page_title=page_title,
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)


st.title(f"{page_icon} Welcome To: {page_title}")
streamlit_dataset_upload(default_data_path=data_path)

df = st.session_state["data"]


data = {
    "General": {
        "Energy": [28.0, "kcal", "1%"],
        "Alcohol": [0.0, "g", "N/T"],
        "Caffeine": [0.0, "mg", "N/T"],
        "Water": [90.7, "g", "2%"],
    },
    "Carbohydrates": {
        "Carbs": [5.4, "g", "2%"],
        "Fiber": [3.0, "g", "8%"],
        "Starch": [0.7, "g", "N/T"],
        "Sugars": [1.5, "g", "N/T"],
        "Added Sugars": [0.0, "g", "N/T"],
        "Net Carbs": [2.3, "g", "1%"],
    },
    "Vitamins": {
        "B1 (Thiamine)": [0.1, "mg", "5%"],
        "B2 (Riboflavin)": [0.1, "mg", "6%"],
        "B3 (Niacin)": [0.5, "mg", "3%"],
        "B5 (Pantothenic Acid)": [0.3, "mg", "5%"],
        "B6 (Pyridoxine)": [0.1, "mg", "10%"],
        "B12 (Cobalamin)": [0.0, "µg", "0%"],
        "Folate": [56.0, "µg", "14%"],
        "Vitamin A": [50.6, "µg", "6%"],
        "Vitamin C": [40.1, "mg", "45%"],
        "Vitamin D": [0.0, "IU", "0%"],
        "Vitamin E": [1.1, "mg", "8%"],
        "Vitamin K": [88.1, "µg", "73%"],
    },
}


# Function to convert percentage strings to float values
def convert_percentage(percent_str):
    try:
        return float(percent_str.strip("%"))
    except ValueError:
        return 0


# Function to create the bar text as a simple string for now
def create_bar_text(percentage):
    bar_length = int(percentage * 10 / 100)  # Normalize to 10 characters max
    return "█" * bar_length


# Create the figure
fig = make_subplots(
    rows=1,
    cols=3,
    subplot_titles=("General", "Carbohydrates", "Vitamins"),
    specs=[[{"type": "table"}, {"type": "table"}, {"type": "table"}]],
)


# Function to add a table with bars to the subplot
def add_table_with_bars(fig, data, row, col, title):
    header = dict(
        values=[
            "<b>Nutrient</b>",
            "<b>Amount</b>",
            "<b>Unit</b>",
            "<b>% Daily Value</b>",
        ],
        fill_color="lightgray",
        align="left",
        font=dict(color="black"),
    )

    nutrients = list(data.keys())
    amounts = [str(val[0]) for val in data.values()]
    units = [val[1] for val in data.values()]
    percentages = [convert_percentage(val[2]) for val in data.values()]
    bars = [create_bar_text(p) for p in percentages]
    cells_values = [nutrients, amounts, units, bars]

    cells = dict(
        values=cells_values,
        fill_color="white",
        align="left",
        line_color="gray",
        font=dict(color="black"),
    )

    # Add the table
    fig.add_trace(go.Table(header=header, cells=cells), row=row, col=col)


# Add tables for each category
add_table_with_bars(fig, data["General"], 1, 1, "General")
add_table_with_bars(fig, data["Carbohydrates"], 1, 2, "Carbohydrates")
add_table_with_bars(fig, data["Vitamins"], 1, 3, "Vitamins")

# Update layout
fig.update_layout(
    height=600, width=1200, title_text="Nutritional Information with Percentage Bars"
)

# Show the plot in Streamlit
st.plotly_chart(fig)
