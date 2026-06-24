import pandas as pd
import numpy as np
import sqlite3
import logging
import os
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Ensure data directories exist."""
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

def generate_mock_source_data(file_path):
    """Creates a dummy CSV file to simulate raw hydrological sensor data."""
    stations = ['Jinja', 'Kisumu', 'Mwanza', 'Entebbe', 'Bukoba']
    dates = pd.date_range(start="2026-06-01", periods=30, freq='D')
    data = []
    
    for date in dates:
        for station in stations:
            level = round(1134.0 + np.random.uniform(-0.5, 0.5), 2)
            temp = round(25.0 + np.random.uniform(-2, 2), 1)
            # Introduce some nulls for the cleaning step
            if np.random.rand() > 0.95:
                level = np.nan
            data.append([date, station, level, temp])
            
    df = pd.DataFrame(data, columns=['timestamp', 'station_id', 'water_level_m', 'surface_temp_c'])
    df.to_csv(file_path, index=False)
    logger.info(f"Mock data generated at {file_path}")

class HydroETL:
    def __init__(self, db_name="lake_victoria_hydro.db"):
        self.db_name = db_name
        self.raw_path = "data/raw/sensor_logs.csv"
        self.processed_path = "data/processed/daily_summary.csv"

    def extract(self):
        """Extract data from CSV."""
        logger.info("Starting extraction phase...")
        if not os.path.exists(self.raw_path):
            generate_mock_source_data(self.raw_path)
        return pd.read_csv(self.raw_path)

    def transform(self, df):
        """Clean and aggregate the hydrological data."""
        logger.info("Starting transformation phase...")
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Handle missing values: Forward fill then mean
        df['water_level_m'] = df.groupby('station_id')['water_level_m'].ffill()
        df['water_level_m'] = df['water_level_m'].fillna(df['water_level_m'].mean())
        
        # Calculate daily aggregates per station
        summary = df.groupby(['station_id', df['timestamp'].dt.date]).agg({
            'water_level_m': ['mean', 'max', 'min'],
            'surface_temp_c': 'mean'
        }).reset_index()
        
        # Flatten multi-index columns
        summary.columns = [
            'station_id', 'observation_date', 
            'avg_level', 'max_level', 'min_level', 'avg_temp'
        ]
        
        # Add a risk flag for high water levels
        threshold = 1134.3
        summary['flood_risk'] = summary['max_level'].apply(lambda x: 'High' if x > threshold else 'Low')
        
        return summary

    def load(self, df):
        """Load the transformed data into SQLite and a CSV summary."""
        logger.info("Starting load phase...")
        
        # Save to CSV for reporting
        df.to_csv(self.processed_path, index=False)
        
        # Save to SQLite database
        conn = sqlite3.connect(self.db_name)
        df.to_sql('hydrological_stats', conn, if_exists='replace', index=False)
        conn.close()
        
        logger.info(f"Data successfully loaded into {self.db_name} and {self.processed_path}")

    def run(self):
        """Execute the full ETL pipeline."""
        try:
            setup_environment()
            raw_data = self.extract()
            clean_data = self.transform(raw_data)
            self.load(clean_data)
            logger.info("ETL Pipeline completed successfully.")
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise

if __name__ == "__main__":
    etl = HydroETL()
    etl.run()