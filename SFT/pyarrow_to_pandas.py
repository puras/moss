import pyarrow.parquet as pq
import pandas as pd

parquet_file = pq.ParquetFile("../datasets/instruction_dataset.parquet")
data = parquet_file.read().to_pandas()

print(data.head())
data.to_csv('data.csv', index=False)