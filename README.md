# Hollistic Food Dataset
![Data-Food-Pipeline](images/Food%20Data%20Pipeline.drawio.svg)

## Overview
This project fetches nutrition data from a variety of data sources and merges it into one standardized dataset, which is used for data analysis and mealplan generation in this project [here](https://github.com/ArthurZakirov/Mealplan-App)

I've built pipelines for the following datasources, out of which only some turned out to be useful:
- **FoodData Central** SR Legacy Food (Click [here](https://fdc.nal.usda.gov/download-datasets.html))
- **REWE Online Shop Data**  Click [here](https://shop.rewe.de/)
- **Insulin Index** Click [here](https://www.scribd.com/document/379537249/Bell-KJ-thesis-2-pdf) & [here](https://foodstruct.com/insulin-index-chart-food-list)
- **Fullness Factor** calculated through a formula
- **Preparation Time** estimated by openAi API


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

# Dataset: REWE 
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


# Dataset: FoodData Central** ([here](https://fdc.nal.usda.gov/download-datasets.html))
Latest Downloads > SR Legacy > April 2018 (CSV)
[README](images/readme/FoodDataCentral-Download%20Data.png)

I selected the SR Legacy version over all other datasets by the USDA because it is the only one that satisfies the following 2 properties:
- It has the highest number of micronutrients provided
- It has general food names (instead of branded food names), which makes it more convenient to match with foods from other data sources

1. Download the folder
2. Unzip the folder
3. Move the folder so that the path becomes "data/raw/FoodData_Central_sr_legacy_food_csv_2018-04"  


# Dataset: Insulin Index
### University Of Sydney: Bell KJ Thesis
Upload [this](https://www.scribd.com/document/379537249/Bell-KJ-thesis-2-pdf) pdf to [ChatGPT](https://chatgpt.com/) and give it the task to extract the data into a csv file.

### Foodstruct
Export [this](https://foodstruct.com/insulin-index-chart-food-list) website as a pdf and upload it to [ChatGPT](https://chatgpt.com/) and give it the task to extract the data into a csv file.
