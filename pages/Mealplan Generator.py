import streamlit as st
import pandas as pd
import os
import json
import datetime
import argparse
import plotly.express as px
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import streamlit as st
from PIL import Image


from src.streamlit.page_config import set_page_config
from src.streamlit.data_input import streamlit_dataset_upload
from src.streamlit.references import display_calorie_change_studies
from src.streamlit.page_interaction import (
    user_input_energy,
    user_input_macronutrients,
    user_input_micronutrients,
    show_micronutrient_health_outcomes,
    user_input_optimization_settings,
    user_input_body_type,
    initialize_macro_rdi_session_state,
    determine_daily_calorie_change,
    manage_constraints,
    input_current_user_stats,
)
from src.streamlit.mealplan_output import (
    display_mealplan_in_streamlit,
    create_meaplan_from_optimizer_results,
)
from src.nutrition.formulas import calculate_nutrient_goals
from src.nutrition.optimization import save_optimization_results
from src.nutrition.optimization import (
    optimize_diet,
    create_optimization_results_summary,
)
from src.visualization.dashboard import visualize_optimization_result_nutrient_breakdown

css = set_page_config()

df = st.session_state["data"]

image_dir = os.path.join(os.path.dirname(__file__), "..", "images/body_shapes")

st.markdown("### 1. Your Situation")
with st.expander("Situation"):
    selected_body_type = user_input_body_type(image_dir)
    gender, age, height, weight, goal_weight, activity_scale = (
        input_current_user_stats()
    )
    daily_calorie_change = determine_daily_calorie_change(
        weight, goal_weight, selected_body_type
    )

    st.write(f"Required Calorie Change: {daily_calorie_change:.0f} kcal.")

    display_calorie_change_studies()

    rdi_dict = calculate_nutrient_goals(
        weight=weight,
        height=height,
        age=age,
        calorie_adjustment=daily_calorie_change,
        activity_scale=activity_scale,
        gender=gender,
    )

    initialize_macro_rdi_session_state(rdi_dict)

st.markdown("### 2. Energy & Macros")
with st.expander("Energy Intake"):

    energy_intake, constant_kcal = user_input_energy(rdi_dict)

with st.expander("Macronutrients Ratio"):
    col1, col2 = st.columns([1, 1])

    with col1:
        NUTRIENTS = ["Total Fat [G]", "Carbohydrate [G]", "Protein [G]"]
        macro_ranges = {}
        macro_ranges = user_input_macronutrients(
            macro_ranges, NUTRIENTS, slider_range=(0, 600), constant_kcal=constant_kcal
        )

with st.expander("Macronutrients Health Threats"):
    col1, col2 = st.columns([1, 1])

    with col1:
        NUTRIENTS = ["Sugars, added [G]", "Saturated Fat [G]"]
        macro_ranges = user_input_macronutrients(
            macro_ranges, NUTRIENTS, slider_range=(0, 100), constant_kcal=constant_kcal
        )


st.markdown("### 3. Fiber Intake")
with st.expander("Fiber Intake"):
    col1, col2 = st.columns([1, 1])

    with col1:
        NUTRIENTS = ["Fiber [G]"]
        macro_ranges = user_input_macronutrients(
            macro_ranges, NUTRIENTS, slider_range=(0, 100), constant_kcal=constant_kcal
        )


st.markdown("### 4. Micronutrients")
with st.expander("Micronutrients"):

    micro_ranges = {}
    col1, col2 = st.columns([1, 1])

    with col1:
        micro_ranges = user_input_micronutrients(rdi_dict, micro_ranges)

    with col2:
        show_micronutrient_health_outcomes(
            rdi_dict, path="data/processed/nutrient_health_outcomes.csv"
        )


st.markdown("### 5. Optimization Settings")
with st.expander("Optimization Settings"):
    col_1, col_2 = st.columns([1, 1])
    with col_1:
        (
            cost_factor,
            time_factor,
            insulin_factor,
            fullness_factor,
            daily_food_budget,
            optimization_unit_size,
            micro_tolerance,
        ) = user_input_optimization_settings()

        manage_constraints()

if st.button("Optimize Diet"):
    relative_df, food_vars = optimize_diet(
        daily_food_budget=daily_food_budget,
        cost_factor=cost_factor,
        time_factor=time_factor,
        insulin_factor=insulin_factor,
        fullness_factor=fullness_factor,
        df=df,
        rdi_dict=rdi_dict,
        food_constraints=st.session_state.food_constraints,
        optimization_unit_size=optimization_unit_size,
        macro_tolerance=0,
        micro_tolerance=micro_tolerance,
    )

    results_df, summary_df, total_df = create_optimization_results_summary(
        relative_df, rdi_dict, food_vars
    )

    output_path = "data/processed/optimized_diet.csv"
    flat_column_result_df = save_optimization_results(output_path, results_df)

    st.markdown("### Optimization Results")
    with st.expander("Optimization Results"):

        fig_1, fig_2 = visualize_optimization_result_nutrient_breakdown(total_df)
        st.plotly_chart(fig_1)
        st.plotly_chart(fig_2)

        merged_df = create_meaplan_from_optimizer_results(
            df, flat_column_result_df, optimization_unit_size
        )
        # display_mealplan_in_streamlit(merged_df)
