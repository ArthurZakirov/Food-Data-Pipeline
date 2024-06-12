import streamlit as st
import os
import pandas as pd
from PIL import Image


def initialize_macro_rdi_session_state(rdi_dict):
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


def user_input_body_type(image_dir):
    # Function to display image and checkbox
    def display_body_type(image_path, label, column):
        with column:
            checkbox = st.checkbox(label)
            image = Image.open(image_path)
            st.image(image, caption=label, use_column_width=True)
        return checkbox

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

    return selected_body_type


def determine_daily_calorie_change(current_weight, goal_weight, selected_body_type):
    KCAL_PER_KG = 7700
    DAYS_PER_WEEK = 7
    RECOMMENDED_SURPLUS = 300
    RECOMMENDED_DEFICIT = 500

    weight_change_goal = goal_weight - current_weight

    daily_calorie_change = (
        RECOMMENDED_SURPLUS if weight_change_goal > 0 else RECOMMENDED_DEFICIT
    )

    recommended_weeks = abs(
        weight_change_goal * KCAL_PER_KG / daily_calorie_change / DAYS_PER_WEEK
    )
    recommended_weeks = int(recommended_weeks) if recommended_weeks > 0 else 1

    timeframe = st.slider("Timeframe (weeks)", 1, 52, value=recommended_weeks)

    daily_calorie_change = (weight_change_goal * KCAL_PER_KG) / (
        timeframe * DAYS_PER_WEEK
    )
    return daily_calorie_change


def input_current_user_stats():
    col1, col2 = st.columns([1, 3])  # Adjust the ratio as needed

    with col1:
        gender = st.radio("Select your gender:", ("male", "female"), key="gender")
        age = st.number_input(
            "Enter your age", min_value=0, max_value=100, step=1, value=24, key="age"
        )

        height = st.number_input(
            "Enter your height in cm",
            min_value=140,
            max_value=250,
            step=1,
            value=180,
            key="height",
        )

        weight = st.number_input(
            "Current weight in kg",
            min_value=40,
            max_value=200,
            step=1,
            value=88,
            key="weight",
        )

        goal_weight = st.number_input(
            "Goal weight in kg",
            min_value=40,
            max_value=200,
            step=1,
            value=85,
            key="goal_weight",
        )

        activity_scale = st.slider(
            "Activity",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            key="activity_scale",
        )

    return gender, age, height, weight, goal_weight, activity_scale


def user_input_energy(rdi_dict):
    energy_range = rdi_dict["Energy"]["Energy [KCAL]"]
    energy_intake = st.slider(
        "Energy [KCAL]",
        min_value=energy_range["lower_bound"] - 500,
        max_value=energy_range["upper_bound"] + 500,
        value=(energy_range["lower_bound"], energy_range["upper_bound"]),
        step=10,
        key="energy_intake_slider",
    )

    constant_kcal = st.radio(
        "Select Mode", ("Constant Kcal", "Dynamic Kcal"), key="mode_radio"
    )
    return energy_intake, constant_kcal


def update_macros(changed_nutrient, lower_value, upper_value, constant_kcal=True):
    KCAL_PER_GRAM_FAT = 9
    KCAL_PER_GRAM_CARBS = 4

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
    if constant_kcal == "Constant Kcal":
        if changed_nutrient == "Total Fat [G]":
            delta = (upper_value - fat_upper_before) * KCAL_PER_GRAM_FAT
            st.session_state["Carbohydrate [G]_upper"] = (
                carb_upper_before + delta // KCAL_PER_GRAM_CARBS
            )
            st.write(f"Adjusted Carbs: {st.session_state['Carbohydrate [G]_upper']}")
        elif changed_nutrient == "Carbohydrate [G]":
            delta = (upper_value - carb_upper_before) * KCAL_PER_GRAM_CARBS
            st.session_state["Total Fat [G]_upper"] = (
                fat_upper_before + delta // KCAL_PER_GRAM_FAT
            )
            st.write(f"Adjusted Fat: {st.session_state['Total Fat [G]_upper']}")

        elif changed_nutrient == "Protein [G]":
            delta = (upper_value - protein_upper_before) * KCAL_PER_GRAM_CARBS
            st.session_state["Carbohydrate [G]_upper"] = (
                carb_upper_before + delta // KCAL_PER_GRAM_CARBS
            )
            st.write(f"Adjusted Carbs: {st.session_state['Carbohydrate [G]_upper']}")

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


def user_input_macronutrients(
    macro_ranges, NUTRIENTS, slider_range=(0, 600), constant_kcal=True
):

    for nutrient in NUTRIENTS:
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
            min_value=slider_range[0],
            max_value=slider_range[1],
            value=(lower_bound, upper_bound),
            step=1,
            key=f"{nutrient}_slider",
        )

        if slider_value != (lower_bound, upper_bound):
            # Update session state with new slider values
            st.session_state[lower_key], st.session_state[upper_key] = slider_value

            # Call update_macros with initial and new values
            update_macros(nutrient, lower_bound, upper_bound, constant_kcal)

        macro_ranges[nutrient] = (lower_bound, upper_bound)
    return macro_ranges


def user_input_micronutrients(rdi_dict, micro_ranges):
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
    return micro_ranges


def show_micronutrient_health_outcomes(rdi_dict, path):
    micro_health_df = pd.read_csv(path)
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


def user_input_optimization_settings():
    optimization_mode = st.radio(
        "Select Mode",
        ("Minimize Cost, given Food Quality", "Maximize Food Quality, given cost"),
        key="optimization_mode",
    )

    if optimization_mode == "Maximize Food Quality, given cost":
        daily_food_budget = st.slider(
            "Daily Food Budget [EUR]",
            min_value=0,
            max_value=50,
            step=1,
            key="daily_food_budget_slider",
        )

    else:
        daily_food_budget = None

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

    return optimization_mode, daily_food_budget, amount_unit, micro_tolerance


# Function to manage food constraints
def manage_constraints():
    # Initialize constraints if not in session state
    if "food_constraints" not in st.session_state:
        st.session_state.food_constraints = {
            "Seeds, cottonseed meal, partially defatted (glandless)": [None, 0],
            "Eggs, Grade A, Large, egg whole": [None, 1.2],
            "Soy protein isolate, potassium type": [None, 0],
        }

    # Display existing constraints
    if st.session_state.food_constraints:
        st.write("Current Food Constraints:")
        for food, bounds in list(st.session_state.food_constraints.items()):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.text(f"{food}: {bounds}")
            with col2:
                if st.button("Edit", key=f"edit_{food}"):
                    st.session_state.edit_food = food
                    st.session_state.lower_bound, st.session_state.upper_bound = bounds
            with col3:
                if st.button("Remove", key=f"remove_{food}"):
                    del st.session_state.food_constraints[food]
            with col4:
                st.empty()

    # Form to add or edit food constraints
    with st.form(key="food_form"):
        st.write("Add or Edit Food Constraint:")
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            food_name = st.text_input(
                "Food Name",
                key="food_name",
                value=st.session_state.get("edit_food", ""),
            )
        with col2:
            lower_bound = st.number_input(
                "Lower Bound",
                format="%.2f",
                step=0.01,
                key="lower_bound",
                value=st.session_state.get("lower_bound", 0.0),
            )
        with col3:
            upper_bound = st.number_input(
                "Upper Bound",
                format="%.2f",
                step=0.01,
                key="upper_bound",
                value=st.session_state.get("upper_bound", 0.0),
            )
        with col4:
            submit_button = st.form_submit_button(label="Submit")

        if submit_button:
            if food_name:
                st.session_state.food_constraints[food_name] = [
                    lower_bound if lower_bound else None,
                    upper_bound if upper_bound else None,
                ]
                st.success("Constraint updated")
                # Clear the form
                st.session_state.pop("edit_food", None)
                st.session_state.pop("lower_bound", None)
                st.session_state.pop("upper_bound", None)
