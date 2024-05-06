def calculate_nutrition(
    weight, height, age, calorie_adjustment, activity_scale, gender="male"
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
    protein = round(weight * 2.2)
    fat_kcal = round(weight * 2.2 * 0.4 * 9)  # Fat has ~9 calories per gram
    protein_kcal = round(protein * 4)
    carb_kcal = round(tdee - fat_kcal - protein_kcal)  # Calculate carb kcal from TDEE

    # Convert kcal of fat and carbs to grams
    fat = round(fat_kcal / 9)
    carbs = round(carb_kcal / 4)

    # Set fiber goals based on age and gender
    if gender == "male":
        fiber = 38 if age <= 50 else 30  # Fiber intake in grams per day
    else:
        fiber = 25 if age <= 50 else 21  # Fiber intake in grams per day

    return {
        "protein": protein,  # in grams
        "fat": fat,  # in grams
        "net_carbs": carbs,  # in grams
        "fiber": fiber,  # in grams, based on general recommendations
        "energy (kcal)": tdee,  # total calories
    }
