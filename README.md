# Edge WebDriver 
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


# MyFitnessPal Log Dashboard
```bash
python build_myfitnesspal_log_dashboard.py
```
