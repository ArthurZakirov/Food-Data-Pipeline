import pandas as pd
import pulp as pl


def optimize_diet(df, goals, minimum_amount_per_category=1, tolerance=10):
    # Create the optimization model
    model = pl.LpProblem("Diet_Optimization", pl.LpMinimize)

    # Decision variables: Amounts of each food item to consume
    food_vars = pl.LpVariable.dicts("Food", df.index, lowBound=0, cat="Continuous")

    # Objective function and constraints setup
    deviations = []

    for nutrient in df.columns.difference(["Name", "Category", "Price (EUR/ 100g)"]):
        model += (
            pl.lpSum([df.loc[i, nutrient] * food_vars[i] for i in df.index])
            >= goals[nutrient] - tolerance,
            f"{nutrient}_min",
        )
        model += (
            pl.lpSum([df.loc[i, nutrient] * food_vars[i] for i in df.index])
            <= goals[nutrient] + tolerance,
            f"{nutrient}_max",
        )
        deviations.append(
            pl.lpSum([df.loc[i, nutrient] * food_vars[i] for i in df.index])
            - goals[nutrient]
        )

    # Add category constraints to ensure at least one food item per category is chosen
    categories = df["Category"].unique()
    for category in categories:
        category_items = df[df["Category"] == category].index
        model += (
            pl.lpSum([food_vars[i] for i in category_items])
            >= minimum_amount_per_category,
            f"Category_{category}_min",
        )

    # Dummy objective to have a proper LP format
    model += pl.lpSum(deviations)

    # Solve the model
    model_status = model.solve()

    # Extract the solution into a DataFrame
    results = []
    for i in df.index:
        quantity = pl.value(food_vars[i])
        if (
            quantity is not None and quantity > 0
        ):  # Only consider food items with a non-zero quantity
            results.append(
                {
                    "Name": df.loc[i, "Name"],
                    "Category": df.loc[i, "Category"],
                    "Amount": quantity,
                    **{
                        nutrient: df.loc[i, nutrient]
                        for nutrient in df.columns
                        if nutrient not in ["Name", "Category"]
                    },
                }
            )

    # Create DataFrame from results
    result_df = pd.DataFrame(results)

    # Calculate total nutritional intake from selected items
    totals = {
        "Name": "Total",
        "Category": "Total",
        **{
            nutrient: sum(result_df[nutrient] * result_df["Amount"])
            for nutrient in df.columns
            if nutrient not in ["Name", "Category"]
        },
    }

    # Create DataFrame for the total and goal rows
    totals_df = pd.DataFrame([totals])
    goals["Name"] = "Goal"
    goals_df = pd.DataFrame([goals])

    # Concatenate all together with 'Name' as a regular column
    result_df = pd.concat([result_df, totals_df, goals_df], ignore_index=True)

    return result_df
