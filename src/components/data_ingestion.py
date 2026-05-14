
import pandas as pd
import os

class DataIngestion:
    def ingest_data(self):
        os.makedirs("artifacts", exist_ok=True)
        df = pd.read_csv("data/raw/shipment.csv")
        df.to_csv("artifacts/raw.csv", index=False)
        return "artifacts/raw.csv"
