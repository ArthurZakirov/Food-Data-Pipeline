# Food Data Pipeline
![Data-Food-Pipeline](images/Food%20Data%20Pipeline.drawio.svg)


## Table Of Contents
- [1. Overview](#overview)
- [2. Installation](#installation)
- [3. Rewe-Online-Shop-Data Pipeline](#rewe-online-shop-data)
- [4. FoodData Central Pipeline](#fooddata-central)
- [5. Insulin Index Data Pipeline](#insulin-index)
- [6. Merging Datasets](#merging-datasets)

## Overview
This project fetches nutrition data from a variety of data sources and merges it into one standardized dataset, which is used for data analysis and mealplan generation in this project [here](https://github.com/ArthurZakirov/Mealplan-App)

I've built pipelines for the following datasources, out of which only some turned out to be useful:
- **FoodData Central** SR Legacy Food (Click [here](https://fdc.nal.usda.gov/download-datasets.html))
- **REWE Online Shop Data**  Click [here](https://shop.rewe.de/)
- **Insulin Index** Click [here](https://www.scribd.com/document/379537249/Bell-KJ-thesis-2-pdf) & [here](https://foodstruct.com/insulin-index-chart-food-list)
- **Fullness Factor** calculated through a formula
- **Preparation Time** estimated by openAi API

## Installation
- Python 3.x
- Required Python libraries (listed in `requirements.txt`)

1. Clone the repository:
   ```bash
   git clone https://github.com/ArthurZakirov/food-data-pipeline.git
   ```
2. Navigate to the project directory:
   ```bash
    cd food-data-pipeline
   ```
3. Install the dependencies
   ```bash
   python3 -m venv venv
   venv/Scripts/activate
   pip install -r requirements.txt
   ```

   If the installation of hydra fails, run `pip install hydra-core --upgrade --user`
# REWE Online Shop Data 
### 1. Setup Edge WebDriver
Download and setup the Microsoft WebDriver folling the instructions [here](https://learn.microsoft.com/en-us/microsoft-edge/webdriver-chromium/?tabs=python&form=MA13LH)

### 2. Start Edge Browser With Debugging Port
Run the following command in a new Terminal
```bash
start msedge --remote-debugging-port=9222 --user-data-dir=<path\to\your\user\data>
```

| Argument | Example | Description |
|----------|-------------|---------|
| `--remote-debugging-port` | `9222` | Debugging Port |
| `--user-data-dir` | `"C:\Users\arthu\Documents\EdgeUserData"` | Where you store the edge browsing data |

### 3. Manually Navigate To Website
Inside the edge browser tab that was created by the previous terminal command, manually navigate to https://shop.rewe.de/ and accept cookies, to avoid bot protection.

### 4. Scrape The Dataset
Run the following command in a new Terminal
```bash
python src/rewe_data/scrape_rewe_online_shop.py --output_path=<path/to/your/data> --remote-debugging-port=<port> --edge_driver_path=<path/to/your/driver> --url=<url>
```
| Argument | Example | Description |
|----------|-------------|---------|
| ```--output_path``` | ```"data/rewe_dataset.csv"``` | Where to store your scraped dataset |
| ```--remote-debugging-port``` | ```9222``` | Debugging Port |
| ```--edge_driver_path``` | ```"C:\\Users\\arthu\\Tools\\WebDriver\\edgedriver_win64\\msedgedriver.exe"``` | Path to msedgedriver.exe |
| ```--url``` | ```"https://shop.rewe.de/"``` | URL to the Rewe Website |

### 4. Process Rewe Dataset
1. Run the following
```bash
python src/rewe_data/process_rewe_dataset.py
```
2. Set the following config inside `config/config.yaml`:
-  `defaults.chain` to `extract_regulated_food_name`
- `data.input_path` to `data\raw\cleaned_rewe_dataset.csv`
- `data.output_path` to `data\raw\cleaned_rewe_dataset.csv`
- `data.input_column` to `Name`
- `data.output_column` to `Regulated Name`

Then run
```bash
python src/my_langchain/run_llm_processing_of_df.py
```

3. Set the following config inside `config/config.yaml`:
-  `defaults.chain` to `translate_ger_to_eng`
- `data.input_path` to `data\raw\cleaned_rewe_dataset.csv`
- `data.output_path` to `data\raw\cleaned_rewe_dataset.csv`
- `data.input_column` to `Regulated Name`
- `data.output_column` to `Regulated Name English`
Then run
```bash
python src/my_langchain/run_llm_processing_of_df.py
```


# FoodData Central 
### 1. Download Dataset
Latest Downloads > SR Legacy > April 2018 (CSV)
![README](images/readme/FoodDataCentral-Download%20Data.png)

I selected the SR Legacy version over all other datasets by the USDA because it is the only one that satisfies the following 2 properties:
- It has the highest number of micronutrients provided
- It has general food names (instead of branded food names), which makes it more convenient to match with foods from other data sources

1. Download [here](https://fdc.nal.usda.gov/download-datasets.html)
2. Unzip the folder
3. Move the folder so that the path becomes "data/raw/FoodData_Central_sr_legacy_food_csv_2018-04"  

Run this
```bash
python src/food_data_central/process_fdc_data.py
```

# Insulin Index
### University Of Sydney: Bell KJ Thesis
Upload [this](https://www.scribd.com/document/379537249/Bell-KJ-thesis-2-pdf) pdf to [ChatGPT](https://chatgpt.com/) and give it the task to extract the data into a csv file.

### Foodstruct
Export [this](https://foodstruct.com/insulin-index-chart-food-list) website as a pdf and upload it to [ChatGPT](https://chatgpt.com/) and give it the task to extract the data into a csv file.

# Merging Datasets
### 1. Merge REWE & FDC
Note: If creating embeddings fails it might be because in a previous langchain operation something in the dataframe output column turned to `NaN`.
If that's the case, open a jupyter notebook, perform dropna and save the dataset again.

Inside `config/config.yaml` set `defaults.embedding` to `rewe_embedding`. Then run
```bash
python src/data_merging/create_embeddings.py
```

Inside `config/config.yaml` set `defaults.embedding` to `fdc_embedding`. Then run
```bash
python src/data_merging/create_embeddings.py
```

Run this
```bash
python src/data_merging/merge_rewe_and_fdc_using_embeddings.py
```

### 2. Merge REWE & FDC & Insulin Index
Inside `config/config.yaml` set `defaults.embedding` to `insulin_index_embedding`. Then run
```bash
python src/data_merging/create_embeddings.py
```
Inside `config/config.yaml` set `defaults.embedding` to `rewe_fdc_embedding`. Then run
```bash
python src/data_merging/create_embeddings.py
```
Run this
```bash
python src/data_merging/merge_rewe_and_fdc_with_insulin_using_embeddings.py
```

### 3. Merge REWE & FDC & Insulin Index & Fullness Factor
```bash
python src/fullness_factor/append_fullness_factor.py
```

### 4. Merge REWE & FDC & Insulin Index & Fullness Factor & Preparation Time
Inside `config/config.yaml` set `defaults.chain` to `food_preparation_time`. Then run
```bash
python run_llm_processing_of_df.py
```