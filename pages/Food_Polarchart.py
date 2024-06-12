import streamlit as st
import pandas as pd
import os
import json
import datetime
import argparse
import plotly.express as px
import streamlit as st
import pandas as pd

from src.streamlit.data_input import streamlit_dataset_upload
from src.streamlit.page_interaction import manage_constraints, streamlit_user_input
from src.nutrition.formulas import calculate_nutrient_goals
from src.nutrition.optimization import (
    optimize_diet,
    create_optimization_results_summary,
)
from src.visualization.dashboard import (
    visualize_optimization_result_nutrient_breakdown,
    visualize_polar_chart,
    visualize_micronutrient_polar_chart,
)
from src.nutrition.formulas import calculate_nutrient_goals
from src.nutrition.optimization import calculate_relative_nutrient_df

data_path = "data/processed/merged_rewe_fdc_data.csv"
page_title = "Food Polarchart"
page_icon = ":food:"


st.set_page_config(
    page_title=page_title,
    page_icon=page_icon,
    layout="wide",
)
st.title(f"{page_icon} {page_title}")

if "names" not in st.session_state:
    st.session_state["names"] = []


# Define a function to add a new name to the list
def add_name():
    # Check if the current input is not empty and not already in the list
    if (
        st.session_state.food_name
        and st.session_state.food_name not in st.session_state["names"]
    ):
        st.session_state["names"].append(st.session_state.food_name)
        # Optionally, clear the input box after adding
        st.session_state.food_name = ""


# Create a text input for food name
name = st.text_input("Food Name", key="food_name")

# Create a button to add the current name to the list
st.button("Add another", on_click=add_name)

names = st.session_state["names"]
df = st.session_state["data"]


macro_fig = visualize_polar_chart(df=df, names=names)
st.plotly_chart(macro_fig)

rdi_dict = calculate_nutrient_goals(
    weight=89,
    height=180,
    age=24,
    calorie_adjustment=0,
    activity_scale=0.5,
    gender="male",
)
relative_df, _, _ = calculate_relative_nutrient_df(
    df, rdi_dict, amount_unit=100, goal=100
)

micro_fig = visualize_micronutrient_polar_chart(relative_df, names)
st.plotly_chart(micro_fig)
