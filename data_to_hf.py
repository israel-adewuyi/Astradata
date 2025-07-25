from datasets import DatasetDict, Dataset
import pandas as pd

# Read CSV files
df1 = pd.read_csv("datafiles/cp_datasetv3_train.csv")
df2 = pd.read_csv("datafiles/cp_datasetv3_test.csv")

# Convert to Hugging Face Dataset
dataset1 = Dataset.from_pandas(df1)
dataset2 = Dataset.from_pandas(df2)

# Combine into a DatasetDict (optional, if you want splits)
dataset = DatasetDict({
    "train": dataset1,
    "test": dataset2,
})

# Push to the Hub
dataset.push_to_hub("israel-adewuyi/Astra_datav1", private=True)