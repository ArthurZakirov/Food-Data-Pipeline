RAW_DATA_DIR = data/raw
PROCESSED_DATA_DIR = data/processed

# Specific data files
SCRAPED_DATA = $(RAW_DATA_DIR)/rewe_dataset.csv
CLEANED_DATA = $(PROCESSED_DATA_DIR)/cleaned_data.csv
MERGED_DATA = $(PROCESSED_DATA_DIR)/merged_data.csv

all: $(MERGED_DATA)

# Cleaning data

$(SCRAPED_DATA):
	python scrape_rewe_online_shop.py --output $@


$(CLEANED_DATA): $(RAW_DATA)
	python process_rewe_dataset.py --input $< --output $@

# Fetching additional data
$(MERGED_DATA): $(CLEANED_DATA)
	python fetch_myfitnesspal_dataset.py --input $< --output $@
