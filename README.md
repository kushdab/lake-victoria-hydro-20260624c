# Lake Victoria Hydro ETL 2026

Automated ETL pipeline for aggregating and cleaning hydrological monitoring data from Lake Victoria stations.

## Project Description
This project processes raw sensor data (CSV format) including water levels and surface temperatures. It performs data cleaning (handling nulls), daily aggregation, and risk assessment before loading the results into a SQLite database and a processed CSV report.

## Installation
1. Ensure Python 3.8+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the pipeline via the main script:
```bash
python pipeline.py
```

## Outputs
- `data/raw/`: Generated mock sensor data.
- `data/processed/`: Cleaned daily summary reports.
- `lake_victoria_hydro.db`: SQLite database containing the table `hydrological_stats`.