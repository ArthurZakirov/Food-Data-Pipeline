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


import pandas as pd
import pulp as pl


from src.nutrition.formulas import calculate_nutrient_goals
from src.nutrition.optimization import calculate_relative_nutrient_df
from src.visualization.dashboard import nutrition_scatter_plot


rdi_dict = calculate_nutrient_goals(
    weight=89,
    height=180,
    age=24,
    calorie_adjustment=0,
    activity_scale=0.5,
    gender="male",
)
df = st.session_state["data"]

relative_df, _, _ = calculate_relative_nutrient_df(
    df, rdi_dict, optimization_unit_size=100, goal=100
)

df[("Additional Metrics", "Nutrivore")] = relative_df["Micronutrient"].mean(axis=1)
df[("Additional Metrics", "Protein / Energy [G / KCAL]")] = (
    df[("Macronutrient", "Protein [G]")] / df[("Energy", "Energy [KCAL]")]
)


title = "Protein Density vs Protein"

x_col = ("Additional Metrics", "Protein / Energy [G / KCAL]")
y_col = ("Additional Metrics", "Nutrivore")
z_col = ("Energy", "Energy [KCAL]")

fig = nutrition_scatter_plot(df, x_col, y_col, z_col, title, delimiter=", ")
fig.show()

st.plotly_chart(fig)
