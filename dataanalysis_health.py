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
appointments = dfs["Appointment.csv"]
billings = dfs["Billing.csv"]
doctors = dfs["Doctor.csv"]
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

# Outer join: patients + appointments + billing on PatientID
patients_seen_df = patients.merge(appointments, on='PatientID', how='outer').merge(billings, on='PatientID', how='outer')

import pandas as pd
import numpy as np
# Data cleaning: Check for missing values and null rows
patients_seen_df = patients_seen_df.dropna(subset=['PatientID']) # Remove missing values
patients_seen_unique_df = patients_seen_df.drop_duplicates(subset=['PatientID']) # Remove duplicate patient records if any

patients_seen_unique_df['Year'] = pd.to_datetime(patients_seen_unique_df['Date']).dt.year # Extract year from date

#Create a yearly summary table
yearly_summary = patients_seen_unique_df.groupby('Year').agg(
    total_patient_visits=('PatientID', 'count'),
    total_revenue=('Amount', 'sum'),  # Assuming 'Amount' column exists
    total_bills=('InvoiceID', 'count'),
).reset_index()

yearly_summary['revenue_per_visit'] = (yearly_summary['total_revenue']/yearly_summary['total_bills']).round(2)
yearly_summary['billing_rate'] = (yearly_summary['total_bills']/yearly_summary['total_patient_visits']).round(2)

#Add % change
yearly_summary['revenue_growth'] = (yearly_summary['total_revenue'].pct_change()*100)
yearly_summary['visits_growth'] = (yearly_summary['total_patient_visits'].pct_change()*100)
for col in ['Year']:
    yearly_summary[col] = yearly_summary[col].apply(lambda x: f"{x:.0f}")
for col in ['total_revenue', 'revenue_per_visit']:
    yearly_summary[col] = yearly_summary[col].apply(lambda x: f"{x:,.0f}")
for col in ['revenue_growth', 'visits_growth']:
    yearly_summary[col] = yearly_summary[col].apply(lambda x: f"{x:.1f}%")

print("\n" + "=" * 40)
print("YEARLY SUMMARY WITH GROWTH RATES")
print("=" * 40)
print(yearly_summary.to_string(index=False))


# Visualizing the data
import matplotlib.pyplot as plt #pip install matplotlib
import seaborn as sns

# Set style
sns.set_style("whitegrid")

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Total Visits by Year
axes[0,0].bar(yearly_summary['Year'], yearly_summary['total_patient_visits'], color='steelblue')
axes[0,0].set_title('Total Patient Visits by Year')
axes[0,0].set_xlabel('Year')
axes[0,0].set_ylabel('Number of Visits')

# Plot 2: Total Revenue by Year
axes[0,1].bar(yearly_summary['Year'], yearly_summary['total_revenue'], color='coral')
axes[0,1].set_title('Total Revenue by Year')
axes[0,1].set_xlabel('Year')
axes[0,1].set_ylabel('Revenue ($)')

# Plot 3: Revenue per Visit Trend
axes[1,0].plot(yearly_summary['Year'], yearly_summary['revenue_per_visit'], 
               marker='o', color='green', linewidth=2)
axes[1,0].set_title('Average Revenue per Visit')
axes[1,0].set_xlabel('Year')
axes[1,0].set_ylabel('Revenue per Visit ($)')

# Plot 4: Billing Rate
axes[1,1].bar(yearly_summary['Year'], yearly_summary['billing_rate'], color='purple')
axes[1,1].set_title('Billing Rate by Year')
axes[1,1].set_xlabel('Year')
axes[1,1].set_ylabel('Billing Rate (%)')

plt.tight_layout()
plt.show()