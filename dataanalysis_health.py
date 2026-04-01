import kagglehub; print('kagglehub imported successfully') # download dependencies pip install kagglehub[pandas-datasets]
from kagglehub import KaggleDatasetAdapter

# load dataset directly into Dataframe
dataset = "anouskaabhisikta/healthcare-management-system"
files = [
    "Appointment.csv",
    "Billing.csv",
    "Doctor.csv",
    "Medical Procedure.csv",
    "Patient.csv",
]

dfs = {}
for file_name in files:
    dfs[file_name] = kagglehub.dataset_load(
        KaggleDatasetAdapter.PANDAS, #Give me this data as a pandas DataFrame
        dataset, #Go to this specific dataset on Kaggle
        file_name, ## Load a DataFrame with a specific version of a CSV
    )
    print(file_name, "loaded:", dfs[file_name].shape)

# usage:
appointment = dfs["Appointment.csv"]
billing = dfs["Billing.csv"]
doctor = dfs["Doctor.csv"]
procedures = dfs["Medical Procedure.csv"]
patients = dfs["Patient.csv"]

for file_name,df in dfs.items():
    print(f"{file_name}: listcolumns={df.columns}")

# ANALYSIS: Find similar columns across datasets
from itertools import combinations # for comparing all pairs of columns across tables
from difflib import SequenceMatcher # for fuzzy string matching (to find similar column names that aren't exact matches)

print("\n" + "="*40) # separator for clarity in output
print("FINDING SIMILAR COLUMNS ACROSS DATASETS")
print("-"*60) # separator for clarity in output

# Step 1: Collect all columns from each table
all_columns = {table: set(df.columns) for table, df in dfs.items()}

# Step 2: List all unique column names across all tables
print("\n>>> ALL UNIQUE COLUMN NAMES")
print("-" * 60)
all_cols = sorted(set().union(*all_columns.values()))
for col in all_cols:
    print(f"  {col}")

# Step 3: Find exact column name matches (potential foreign keys)
print("\n>>> EXACT MATCHES (columns with same name)")
print("-" * 60)
for col in all_cols:
    tables = [t for t, cols in all_columns.items() if col in cols]
    if len(tables) > 1:
        print(f"\n  Column: '{col}'")
        print(f"  Found in: {', '.join(tables)}")
        for table in tables:
            sample = dfs[table][col].dropna().head(2).tolist()
            print(f"    {table}: {sample}")