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


from src.streamlit.data_input import streamlit_data_input
from src.streamlit.page_interaction import manage_constraints, input_current_user_stats
from src.nutrition.formulas import calculate_nutrient_goals
from src.nutrition.optimization import optimize_diet, visualize_optimization_results
from src.visualization.dashboard import visualize_optimization_result_nutrient_breakdown


def initialize_session_state(rdi_dict):
    for nutrient in rdi_dict["Macronutrient"]:
        if nutrient in ["Sugars, added [G]", "Saturated Fat [G]", "Fiber [G]"]:
            continue
        lower_key = f"{nutrient}_lower"
        upper_key = f"{nutrient}_upper"
        if lower_key not in st.session_state:
            st.session_state[lower_key] = rdi_dict["Macronutrient"][nutrient].get(
                "lower_bound", 0
            )
        if upper_key not in st.session_state:
            st.session_state[upper_key] = rdi_dict["Macronutrient"][nutrient].get(
                "upper_bound", 0
            )

    for nutrient in ["Saturated Fat [G]", "Sugars, added [G]", "Fiber [G]"]:
        lower_key = f"{nutrient}_lower"
        upper_key = f"{nutrient}_upper"
        if lower_key not in st.session_state:
            st.session_state[lower_key] = (
                rdi_dict["Macronutrient"].get(nutrient, {}).get("lower_bound", 0)
            )
        if upper_key not in st.session_state:
            st.session_state[upper_key] = (
                rdi_dict["Macronutrient"].get(nutrient, {}).get("upper_bound", 0)
            )


data_path = "data/processed/merged_rewe_fdc_data.csv"
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

df = streamlit_data_input(default_data_path=data_path)


# Personal stats input
st.markdown("### 1. Your Situation")
with st.expander("Situation"):
    # Function to display image and checkbox
    def display_body_type(image_path, label, column):
        with column:
            checkbox = st.checkbox(label)
            image = Image.open(image_path)
            st.image(image, caption=label, use_column_width=True)
        return checkbox

    # Define the path to the images
    image_dir = os.path.join(os.path.dirname(__file__), "..", "images/body_shapes")

    # Step 1: Ask for the user's body type
    st.write("Estimate your body type:")
    col1, col2, col3 = st.columns(3)

    ectomorph_selected = display_body_type(
        os.path.join(image_dir, "ectomorph_sad.png"), "Skinny", col1
    )
    mesomorph_selected = display_body_type(
        os.path.join(image_dir, "skinnyfat_sad.png"), "Skinnyfat", col2
    )
    endomorph_selected = display_body_type(
        os.path.join(image_dir, "overweight_sad.png"), "Overweight", col3
    )

    selected_body_type = None
    if ectomorph_selected:
        selected_body_type = "Ectomorph"
    elif mesomorph_selected:
        selected_body_type = "Mesomorph"
    elif endomorph_selected:
        selected_body_type = "Endomorph"

    if selected_body_type is None:
        st.error("Please select a body type.")

    # Step 2: Provide a slider for weight gain/loss goal
    left_col, mid_col, right_col = st.columns([1, 2, 1])
    with right_col:
        st.image(os.path.join(image_dir, "athletic_happy.png"), caption="Weight Loss")

    with left_col:
        current_weight = st.slider("Current Weight (kg)", 0, 150, 88)

        goal_weight = st.slider("Goal Weight (kg)?", 0, 150, 85)

        # Step 3: Calculate recommended timeframe and daily calorie change based on body type
        calories_per_kg = 7700
        if selected_body_type == "Ectomorph":
            surplus = 500  # Ectomorphs may need a higher surplus to gain muscle
            deficit = -400  # Moderate deficit to preserve muscle
        elif selected_body_type == "Mesomorph":
            surplus = 300  # Mesomorphs typically need a moderate surplus
            deficit = -500  # Standard deficit for fat loss
        else:  # Endomorph
            surplus = (
                200  # Endomorphs should use a smaller surplus to minimize fat gain
            )
            deficit = -600  # Higher deficit as they tend to lose fat slower

        weight_change_goal = goal_weight - current_weight
        daily_calorie_change = surplus if weight_change_goal > 0 else deficit

        recommended_weeks = abs(
            weight_change_goal * calories_per_kg / daily_calorie_change / 7
        )
        recommended_weeks = int(recommended_weeks) if recommended_weeks > 0 else 1

        left_col, mid_col, right_col = st.columns([1, 2, 1])

        timeframe = st.slider("Timeframe (weeks)", 1, 52, value=recommended_weeks)

    daily_calories = (weight_change_goal * calories_per_kg) / (timeframe * 7)
    st.write(f"Required Calorie Change: {daily_calories:.0f} kcal.")

    # References
    st.markdown(
        """
    ### References
    - [Calorie Surplus for Muscle Gain](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6019055/)
    - [Calorie Deficit for Weight Loss](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6086580/)
    """
    )

    body_composition_goal = st.radio(
        "Select Mode",
        ("Minimize Cost, given Food Quality", "Maximize Food Quality, given cost"),
        key="optimization_mode",
    )

    if body_composition_goal == "Maximize Food Quality, given cost":
        st.slider(
            "Daily Food Budget [EUR]",
            min_value=0,
            max_value=50,
            step=1,
            key="daily_food_budget_slider",
        )


st.markdown("### 1. Enter Personal Stats")
with st.expander("Personal Stats"):
    gender, age, height, weight, goal_weight = input_current_user_stats()

weight_change_goal = goal_weight - current_weight
daily_calorie_change = surplus if weight_change_goal > 0 else deficit

rdi_dict = calculate_nutrient_goals(
    weight=weight,
    height=height,
    age=age,
    calorie_adjustment=daily_calorie_change,
    activity_scale=0.5,
    gender=gender,
)

initialize_session_state(rdi_dict)

# Energy intake adjustment
st.markdown("### 2. Energy & Macros")
with st.expander("Energy Intake"):
    energy_range = rdi_dict["Energy"]["Energy [KCAL]"]
    energy_intake = st.slider(
        "Energy [KCAL]",
        min_value=energy_range["lower_bound"] - 500,
        max_value=energy_range["upper_bound"] + 500,
        value=(energy_range["lower_bound"], energy_range["upper_bound"]),
        step=10,
        key="energy_intake_slider",
    )

    mode = st.radio("Select Mode", ("Constant Kcal", "Dynamic Kcal"), key="mode_radio")

with st.expander("Macronutrients Ratio"):
    macro_ranges = {}

    def update_macros(changed_nutrient, lower_value, upper_value):
        st.write(f"Triggered update_macros for {changed_nutrient}")

        # Capture initial values
        protein_upper_before = st.session_state["Protein [G]_upper"]
        fat_upper_before = st.session_state["Total Fat [G]_upper"]
        carb_upper_before = st.session_state["Carbohydrate [G]_upper"]

        protein_lower_before = st.session_state["Protein [G]_lower"]
        fat_lower_before = st.session_state["Total Fat [G]_lower"]
        carb_lower_before = st.session_state["Carbohydrate [G]_lower"]

        st.write(
            f"Before adjustment: Protein=({protein_lower_before}, {protein_upper_before}), Fat=({fat_lower_before}, {fat_upper_before}), Carbs=({carb_lower_before}, {carb_upper_before})"
        )

        # Adjust values based on changed nutrient
        if mode == "Constant Kcal":
            if changed_nutrient == "Total Fat [G]":
                delta = (upper_value - fat_upper_before) * 9
                st.session_state["Carbohydrate [G]_upper"] = (
                    carb_upper_before + delta // 4
                )
                st.write(
                    f"Adjusted Carbs: {st.session_state['Carbohydrate [G]_upper']}"
                )
            elif changed_nutrient == "Carbohydrate [G]":
                delta = (upper_value - carb_upper_before) * 4
                st.session_state["Total Fat [G]_upper"] = fat_upper_before + delta // 9
                st.write(f"Adjusted Fat: {st.session_state['Total Fat [G]_upper']}")

            elif changed_nutrient == "Protein [G]":
                delta = (upper_value - protein_upper_before) * 4
                st.session_state["Carbohydrate [G]_upper"] = (
                    carb_upper_before + delta // 4
                )
                st.write(
                    f"Adjusted Carbs: {st.session_state['Carbohydrate [G]_upper']}"
                )

        # Log updated values
        protein_upper_after = st.session_state["Protein [G]_upper"]
        fat_upper_after = st.session_state["Total Fat [G]_upper"]
        carb_upper_after = st.session_state["Carbohydrate [G]_upper"]

        protein_lower_after = st.session_state["Protein [G]_lower"]
        fat_lower_after = st.session_state["Total Fat [G]_lower"]
        carb_lower_after = st.session_state["Carbohydrate [G]_lower"]

        st.write(
            f"After adjustment: Protein=({protein_lower_after}, {protein_upper_after}), Fat=({fat_lower_after}, {fat_upper_after}), Carbs=({carb_lower_after}, {carb_upper_after})"
        )

    # Adjusting the column widths
    col1, col2 = st.columns([1, 1])

    with col1:
        # Total Fat
        st.markdown("Total Fat [G]")
        nutrient = "Total Fat [G]"
        lower_key = f"{nutrient}_lower"
        upper_key = f"{nutrient}_upper"
        lower_bound = st.session_state[lower_key]
        upper_bound = st.session_state[upper_key]
        if lower_bound is None:
            lower_bound = 0
        if upper_bound is None:
            upper_bound = 0

        slider_value = st.slider(
            "",
            min_value=0,
            max_value=600,
            value=(lower_bound, upper_bound),
            step=1,
            key=f"{nutrient}_slider",
        )

        if slider_value != (lower_bound, upper_bound):
            # Update session state with new slider values
            st.session_state[lower_key], st.session_state[upper_key] = slider_value

            # Call update_macros with initial and new values
            update_macros(nutrient, lower_bound, upper_bound)

        macro_ranges[nutrient] = (lower_bound, upper_bound)

        # Carbohydrate
        st.markdown("Carbohydrate [G]")
        nutrient = "Carbohydrate [G]"
        lower_key = f"{nutrient}_lower"
        upper_key = f"{nutrient}_upper"
        lower_bound = st.session_state[lower_key]
        upper_bound = st.session_state[upper_key]
        if lower_bound is None:
            lower_bound = 0
        if upper_bound is None:
            upper_bound = 0

        slider_value = st.slider(
            "",
            min_value=0,
            max_value=600,
            value=(lower_bound, upper_bound),
            step=1,
            key=f"{nutrient}_slider",
        )

        if slider_value != (lower_bound, upper_bound):
            # Update session state with new slider values
            st.session_state[lower_key], st.session_state[upper_key] = slider_value

            # Call update_macros with initial and new values
            update_macros(nutrient, lower_bound, upper_bound)

        macro_ranges[nutrient] = (lower_bound, upper_bound)

        # Protein
        st.markdown("Protein [G]")
        nutrient = "Protein [G]"
        lower_key = f"{nutrient}_lower"
        upper_key = f"{nutrient}_upper"
        lower_bound = st.session_state[lower_key]
        upper_bound = st.session_state[upper_key]
        if lower_bound is None:
            lower_bound = 0
        if upper_bound is None:
            upper_bound = 0

        slider_value = st.slider(
            "",
            min_value=0,
            max_value=600,
            value=(lower_bound, upper_bound),
            step=1,
            key=f"{nutrient}_slider",
        )

        if slider_value != (lower_bound, upper_bound):
            # Update session state with new slider values
            st.session_state[lower_key], st.session_state[upper_key] = slider_value

            # Call update_macros with initial and new values
            update_macros(nutrient, lower_bound, upper_bound)

        macro_ranges[nutrient] = (lower_bound, upper_bound)

with st.expander("Macronutrients Health Threats"):
    col3, col4 = st.columns([1, 1])
    with col3:
        # Saturated Fat
        st.markdown("Saturated Fat [G]")
        nutrient = "Saturated Fat [G]"
        lower_key = f"{nutrient}_lower"
        upper_key = f"{nutrient}_upper"
        lower_bound = st.session_state[lower_key]
        upper_bound = st.session_state[upper_key]
        if lower_bound is None:
            lower_bound = 0
        if upper_bound is None:
            upper_bound = 0

        slider_value = st.slider(
            "",
            min_value=0,
            max_value=100,
            value=(lower_bound, upper_bound),
            step=1,
            key=f"{nutrient}_slider_secondary",
            help="Saturated Fat",
            format="%d",
        )

        if slider_value != (lower_bound, upper_bound):
            st.session_state[lower_key], st.session_state[upper_key] = slider_value
            st.write(f"Saturated Fat values updated to: {slider_value}")

        # Added Sugar
        st.markdown("Sugars, added [G]")
        nutrient = "Sugars, added [G]"
        lower_key = f"{nutrient}_lower"
        upper_key = f"{nutrient}_upper"
        lower_bound = st.session_state[lower_key]
        upper_bound = st.session_state[upper_key]
        if lower_bound is None:
            lower_bound = 0
        if upper_bound is None:
            upper_bound = 0

        slider_value = st.slider(
            "",
            min_value=0,
            max_value=100,
            value=(lower_bound, upper_bound),
            step=1,
            key=f"{nutrient}_slider_secondary",
            help="Sugars, added",
            format="%d",
        )

        if slider_value != (lower_bound, upper_bound):
            st.session_state[lower_key], st.session_state[upper_key] = slider_value
            st.write(f"Added Sugar values updated to: {slider_value}")


# Separate toggle for Fiber
st.markdown("### Fiber Intake")
with st.expander("Fiber Intake"):
    col5, col6 = st.columns([1, 1])

    with col5:
        nutrient = "Fiber [G]"
        lower_key = f"{nutrient}_lower"
        upper_key = f"{nutrient}_upper"
        lower_bound = st.session_state[lower_key]
        upper_bound = st.session_state[upper_key]
        if lower_bound is None:
            lower_bound = 0
        if upper_bound is None:
            upper_bound = 0

        slider_value = st.slider(
            nutrient,
            min_value=0,
            max_value=100,
            value=(lower_bound, upper_bound),
            step=1,
            key=f"{nutrient}_slider_fiber",
        )

        if slider_value != (lower_bound, upper_bound):
            st.session_state[lower_key], st.session_state[upper_key] = slider_value

            # Update the fiber values
            st.write(f"Fiber values updated to: {slider_value}")


st.markdown("### Micronutrients")
with st.expander("Micronutrients"):

    micro_ranges = {}
    col1, col2 = st.columns([1, 1])

    with col1:
        for nutrient, bounds in rdi_dict["Micronutrient"].items():
            if bounds["lower_bound"] is None:
                lb = 0.0
            else:
                lb = bounds["lower_bound"]

            if bounds["upper_bound"] is None:
                value = (float(lb), 5 * float(lb))
            else:
                value = (float(lb), float(bounds["upper_bound"]))

            range = st.slider(
                nutrient,
                min_value=0.0,
                value=value,
                step=1.0,
            )
            micro_ranges[nutrient] = range

    with col2:
        micro_health_df = pd.read_csv("data/processed/nutrient_health_outcomes.csv")
        for nutrient, _ in rdi_dict["Micronutrient"].items():
            try:
                health_outcomes = (
                    micro_health_df.groupby("Nutrient")
                    .get_group(nutrient)["Health Outcome"]
                    .to_list()
                )
                st.write(f"{health_outcomes}")
            except:
                pass


# st.write("Your ideal macros:", rdi_dict)

st.markdown("### Optimization Settings")
with st.expander("Optimization Settings"):
    col_1, col_2 = st.columns([1, 1])
    with col_1:
        amount_unit = st.number_input(
            "Enter the amount unit for the foods (e.g. 1g, 10g, 100g)",
            min_value=1,
            max_value=100,
            step=1,
            value=1,
            key="amount_unit",
        )

        micro_tolerance = st.number_input(
            "Enter the percentage below the RDI for micronutrients to be tolerated in the optimization process",
            min_value=0,
            max_value=100,
            step=1,
            value=0,
            key="micro_tolerance",
        )

        manage_constraints()

if st.button("Optimize Diet"):
    relative_df, food_vars = optimize_diet(
        df,
        rdi_dict,
        food_constraints=st.session_state.food_constraints,
        amount_unit=amount_unit,
        macro_tolerance=0,
        micro_tolerance=micro_tolerance,
    )

    results_df, summary_df = visualize_optimization_results(
        relative_df, rdi_dict, food_vars
    )
    total_df = pd.concat([summary_df, results_df], axis=0)
    save_df = results_df.copy()
    save_df.columns = [f"{col[0]}.{col[1]}" for col in save_df.columns]
    save_df.to_csv("data/processed/optimized_diet.csv", index=False)

    def convert_to_int(x):
        try:
            return int(x) if pd.notnull(x) else x
        except:
            return x

    # Apply the conversion across the DataFrame
    results_df = results_df.applymap(convert_to_int)

    st.markdown("### Optimization Results")
    with st.expander("Optimization Results"):
        # Display the DataFrame
        st.markdown(css, unsafe_allow_html=True)  # Allow HTML to set custom CSS
        st.dataframe(total_df)

        fig_1, fig_2 = visualize_optimization_result_nutrient_breakdown(total_df)
        st.plotly_chart(fig_1)
        st.plotly_chart(fig_2)

        df.columns = [".".join(map(str, col)).strip() for col in df.columns.values]

        merged_df = pd.merge(
            save_df,
            df,
            left_on="Non Nutrient Data.FDC Name",
            right_on="Non Nutrient Data.FDC Name",
            how="left",
        )
        merged_df = merged_df[
            [
                "Non Nutrient Data.Image URL",
                "Non Nutrient Data.Regulated Name",
                "Non Nutrient Data.Amount_x",
                "Non Nutrient Data.Price per 100g",
            ]
        ]
        merged_df.columns = [
            col.replace("Non Nutrient Data.", "") for col in merged_df.columns
        ]

        merged_df["Amount_x"] = amount_unit * merged_df["Amount_x"]
        merged_df["Price"] = merged_df["Price per 100g"] / 100 * merged_df["Amount_x"]

        # Assuming 'merged_df' is your DataFrame that has already been loaded elsewhere in your script

        def load_image(url):
            try:
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                return img
            except Exception as e:
                return None  # Returns None if there's an issue loading the image

        # Convert Image URLs to actual images
        merged_df["Image"] = merged_df["Image URL"].apply(load_image)

        # Setup the Streamlit app
        st.title("Product Table with Images")

        # Create a function to display images within the Streamlit table
        def display_image_column(dataframe):
            col1, col2, col3, col4 = st.columns([2, 6, 2, 2])
            with col1:
                st.write("**Image**")  # Title for the image column
            with col2:
                st.write("**Product Name**")  # Title for the product name column
            with col3:
                st.write("**Amount**")
            with col4:
                st.write("**Price**")

            for idx, row in dataframe.iterrows():
                columns = st.columns([2, 6, 2, 2])  # Adjust column widths as necessary
                with columns[0]:
                    if row["Image"]:
                        st.image(
                            row["Image"], width=150
                        )  # Adjust width to fit the layout
                    else:
                        st.write("No image available")
                with columns[1]:
                    st.write(row["Regulated Name"])
                with columns[2]:
                    st.write(row["Amount_x"])
                with columns[3]:
                    st.write(row["Price"])

        # Use the function to display the table
        display_image_column(merged_df)
