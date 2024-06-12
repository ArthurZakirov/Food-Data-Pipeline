micro_goals = {
    "Calcium [MG]": {"lower_bound": 1000, "upper_bound": 2500},
    "Choline [MG]": {"lower_bound": 550, "upper_bound": 3500},
    "Copper [MG]": {"lower_bound": 0.9, "upper_bound": 10},
    "Folate [UG]": {"lower_bound": 400, "upper_bound": 1000},
    "Iron [MG]": {"lower_bound": 8, "upper_bound": 45},
    "Magnesium [MG]": {"lower_bound": 420, "upper_bound": None},
    "Niacin [MG]": {"lower_bound": 16, "upper_bound": 35},
    "Phosphorus [MG]": {"lower_bound": 700, "upper_bound": 4000},
    "Potassium [MG]": {"lower_bound": 4700, "upper_bound": None},
    "Riboflavin [MG]": {"lower_bound": 1.3, "upper_bound": None},
    "Selenium [UG]": {"lower_bound": 55, "upper_bound": 400},
    "Sodium [MG]": {"lower_bound": 1500, "upper_bound": 2300},
    "Thiamin [MG]": {"lower_bound": 1.2, "upper_bound": None},
    "Vitamin A [UG]": {"lower_bound": 900, "upper_bound": 3000},
    "Vitamin B-12 [UG]": {"lower_bound": 2.4, "upper_bound": None},
    "Vitamin B-6 [MG]": {"lower_bound": 1.7, "upper_bound": 100},
    "Vitamin C [MG]": {"lower_bound": 90, "upper_bound": 2000},
    "Vitamin D2 [UG]": {"lower_bound": 20, "upper_bound": 100},
    "Vitamin D3 [UG]": {"lower_bound": 20, "upper_bound": 100},
    "Vitamin E [MG]": {"lower_bound": 15, "upper_bound": 1000},
    "Vitamin K [UG]": {"lower_bound": 120, "upper_bound": None},
    "Zinc [MG]": {"lower_bound": 11, "upper_bound": 40},
    "Biotin [UG]": {"lower_bound": 30, "upper_bound": None},
    "Iodine [UG]": {"lower_bound": 150, "upper_bound": 1100},
    "Manganese [MG]": {"lower_bound": 2.3, "upper_bound": 11},
    "Molybdenum [UG]": {"lower_bound": 45, "upper_bound": 2000},
    "Omega 3 (EPA + DHA) [G]": {"lower_bound": 0.5, "upper_bound": 3},
    "Omega 6 [G]": {"lower_bound": 10, "upper_bound": 20},
    "Omega 3 (ALA) [G]": {"lower_bound": 1.6, "upper_bound": None},
}


def calculate_nutrient_goals(
    weight=89,
    height=180,
    age=24,
    calorie_adjustment=0,
    activity_scale=0.5,
    gender="male",
):
    """
    Calculate daily nutrition needs based on weight, height, age, gender, calorie adjustment, and activity scale,
    with results rounded to the nearest integer.

    Parameters:
    - weight (float): Bodyweight in kilograms.
    - height (float): Height in centimeters.
    - age (int): Age in years.
    - gender (str): Gender of the individual ('male' or 'female').
    - calorie_adjustment (float): Caloric surplus or deficit.
    - activity_scale (float): Activity level on a scale from 0 (sedentary) to 1 (extra active).

    Returns:
    - dict: A dictionary containing the calculated values for protein, fat, net carbs, fiber, and total kcal, rounded to integers.
    """

    # Define activity factors from sedentary to extra active
    activity_factors = [1.2, 1.375, 1.55, 1.725, 1.9]

    # Interpolate activity factor based on activity scale
    if activity_scale <= 0:
        activity_factor = activity_factors[0]
    elif activity_scale >= 1:
        activity_factor = activity_factors[-1]
    else:
        # Calculate index position in the activity_factors list
        index = activity_scale * (len(activity_factors) - 1)
        lower_index = int(index)
        upper_index = lower_index + 1
        weight_factor = index - lower_index

        # Interpolate between the two closest activity factors
        activity_factor = (
            activity_factors[lower_index] * (1 - weight_factor)
            + activity_factors[upper_index] * weight_factor
        )

    # Calculate BMR (Basal Metabolic Rate)
    bmr = 66.5 + (13.75 * weight) + (5.003 * height) - (6.75 * age)

    # Calculate total kcal including activity level and adjustment
    tdee = round((bmr * activity_factor) + calorie_adjustment)

    # Calculate macros
    protein_lower = round(weight * 2)  # lower bound at 1.6 grams per pound
    protein_upper = round(weight * 2.2)  # upper bound at 2.2 grams per pound

    # Calories from protein
    protein_kcal_lower = protein_lower * 4
    protein_kcal_upper = protein_upper * 4

    # Lower and upper bounds for fat intake per pound of body weight
    fat_lower = round(weight * 2.2 * 0.3)  # 0.3 grams per pound
    fat_upper = round(weight * 2.2 * 0.5)  # 0.5 grams per pound

    fat_kcal_lower = round(fat_lower * 9)
    fat_kcal_upper = round(fat_upper * 9)

    sat_fat_lower = None  # 7% of total calories from saturated fat
    sat_fat_upper = round((tdee * 0.05) / 9)

    # Calculate carbohydrate intake from remaining calories
    carb_kcal_lower = round(tdee - fat_kcal_upper - protein_kcal_upper)  # Minimum carbs
    carb_kcal_upper = round(tdee - fat_kcal_lower - protein_kcal_lower)  # Maximum carbs

    # Convert kcal of carbs to grams
    carbs_lower = round(carb_kcal_lower / 4)
    carbs_upper = round(carb_kcal_upper / 4)

    added_suggars_upper = 35
    added_suggars_lower = None

    # Set fiber goals based on age and gender, with bounds
    if gender == "male":
        fiber_lower = 30 if age > 50 else 38  # Lower fiber intake in grams per day
        fiber_upper = 50  # Upper fiber intake, constant as per high recommendation
    else:
        fiber_lower = 21 if age > 50 else 25  # Lower fiber intake in grams per day
        fiber_upper = 30  # Upper fiber intake, constant as per high recommendation

    macro_goals = {
        "Protein [G]": {"lower_bound": protein_lower, "upper_bound": protein_upper},
        "Total Fat [G]": {"lower_bound": fat_lower, "upper_bound": fat_upper},
        "Saturated Fat [G]": {
            "lower_bound": sat_fat_lower,
            "upper_bound": sat_fat_upper,
        },
        "Carbohydrate [G]": {"lower_bound": carbs_lower, "upper_bound": carbs_upper},
        "Sugars, added [G]": {
            "lower_bound": added_suggars_lower,
            "upper_bound": added_suggars_upper,
        },
        "Fiber [G]": {"lower_bound": fiber_lower, "upper_bound": fiber_upper},
    }

    energy_goals = {
        "Energy [KCAL]": {"lower_bound": tdee - 50, "upper_bound": tdee + 50},
    }

    total_goals = {
        "Energy": energy_goals,
        "Macronutrient": macro_goals,
        "Micronutrient": micro_goals,
    }
    return total_goals
