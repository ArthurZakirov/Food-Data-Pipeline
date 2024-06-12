import streamlit as st


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
    return gender, age, height, weight, goal_weight


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
