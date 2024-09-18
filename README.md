# Meal Plan Generator

## Overview

This project generates personalized meal plans based on a user's caloric needs and body composition goals. Users can customize macronutrient and micronutrient targets, or use default recommendations based on the daily recommended intake for adults. Additionally, the meal plan generator offers optimizations for specific dietary goals such as weight loss, health improvement, or affordability.

## Features

- Generate meal plans tailored to user-specific caloric needs and goals.
- Customize macronutrient values (protein, fats, carbs) and micronutrient values (fiber, vitamins, minerals, etc.).
- Default nutrient values based on recommended daily intake.
- Optimize meal plans for:
  - **Fullness Factor**: To prioritize feeling full while maintaining weight loss.
  - **Insulin Index**: For better insulin management and health benefits.
- Option to set a budget for affordability.

## Prerequisites

- Python 3.x
- Required Python libraries (listed in `requirements.txt`)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/meal-plan-generator.git

2. Navigate to the project directory:
   ```bash
    cd meal-plan-generator

3. Install the dependencies
   ```bash
   pip install -r requirements.txt

## Dataset 1: REWE 
### 1. Download & Extract
Download and setup following instructions [here](https://learn.microsoft.com/en-us/microsoft-edge/webdriver-chromium/?tabs=python&form=MA13LH)

### 2. Start Edge Browser With Debugging Port
Run the following command in a new Terminal
```bash
start msedge --remote-debugging-port=9222 --user-data-dir=<path\to\your\user\data>
```

| Argument | Example | Description |
|----------|-------------|---------|
| `--remote-debugging-port` | `9222` | Debugging Port |
| `--user-data-dir` | `"C:\Users\arthu\Documents\EdgeUserData"` | Where you store the edge browsing data |

### Run
Run the following command in a new Terminal
```bash
python scrape_rewe_run.py --output_path=<path/to/your/data> --remote-debugging-port=<port> --edge_driver_path=<path/to/your/driver> --url=<url>
```
| Argument | Example | Description |
|----------|-------------|---------|
| ```--output_path``` | ```"data/rewe_dataset.csv"``` | Where to store your scraped dataset |
| ```--remote-debugging-port``` | ```9222``` | Debugging Port |
| ```--edge_driver_path``` | ```"C:\\Users\\arthu\\Tools\\WebDriver\\edgedriver_win64\\msedgedriver.exe"``` | Path to msedgedriver.exe |
| ```--url``` | ```"https://shop.rewe.de/"``` | URL to the Rewe Website |

## Dataset 2: FoodData_Central
Legacy Food
```bash
FoodData_Central_sr_legacy_food_csv_2018-04
```
Foundation Food
```bash
FoodData_Central_foundation_food_csv_2024-04-18
```

Also download the Kaggle satiety dataset

Also use chatgpt to extract insulin index from online website into csv file

Download these two and put them into
```bash
data/raw
```

