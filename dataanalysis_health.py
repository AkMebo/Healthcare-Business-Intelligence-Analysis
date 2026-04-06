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

print("\n" + "-"*60) # separator for clarity in output
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


import pandas as pd
import numpy as np
# Outer join: patients + appointments + billing on PatientID
patients_seen_df = patients.merge(appointments, on='PatientID', how='outer').merge(billings, on='PatientID', how='outer')


# Data cleaning: Check for missing values and null rows
patients_seen_df = patients_seen_df.dropna(subset=['PatientID']) # Remove missing values
patients_seen_unique_df = patients_seen_df.drop_duplicates(subset=['PatientID']) # Remove duplicate patient records if any

patients_seen_unique_df['Year'] = pd.to_datetime(patients_seen_unique_df['Date']).dt.year # Extract year from date

#Create a yearly summary table
yearly_summary = patients_seen_unique_df.groupby('Year').agg(
    total_revenue=('Amount', 'sum'),
    total_patient_visits=('PatientID', 'nunique'),  
    total_bills=('InvoiceID', 'nunique'),
).reset_index()

yearly_summary['billing_rate'] = (yearly_summary['total_bills']/yearly_summary['total_patient_visits']).round(2)
yearly_summary['revenue_per_visit'] = (yearly_summary['total_revenue']/yearly_summary['total_bills']).round(2)

#Add % change
yearly_summary['revenue_growth'] = (yearly_summary['total_revenue'].pct_change()*100)
yearly_summary['visits_growth'] = (yearly_summary['total_patient_visits'].pct_change()*100)
for col in ['Year']:
    yearly_summary['Year'] = yearly_summary['Year'].apply(lambda x: f"{x:.0f}")

# Create a display version with formatted strings
display_df = yearly_summary.copy()
display_df['total_revenue'] = display_df['total_revenue'].apply(lambda x: f"${x:,.0f}")
display_df['revenue_per_visit'] = display_df['revenue_per_visit'].apply(lambda x: f"${x:,.0f}")
display_df['billing_rate'] = display_df['billing_rate'].apply(lambda x: f"{x:.1%}")
display_df['revenue_growth'] = display_df['revenue_growth'].apply(lambda x: f"{x:.1}")
display_df['visits_growth'] = display_df['visits_growth'].apply(lambda x: f"{x:.1}")

# Then convert to markdown
markdown_table = display_df.to_markdown(index=False, tablefmt='github')
print("REVENUE PERFORMANCE WITH GROWTH RATES")
print("="*60)
print(markdown_table)


# Visualizing the data
import matplotlib
import matplotlib.pyplot as plt #pip install matplotlib
import matplotlib.ticker as ticker
import seaborn as sns

# Create figure with subplots
fig, axes = plt.subplots(1, 2, figsize=(10, 6))

# Plot 1: Total Revenue by Year
axes[0].bar(yearly_summary['Year'], yearly_summary['total_revenue'], color='coral')
axes[0].set_title('Total Revenue by Year')
axes[0].set_xlabel('Year')
axes[0].set_ylabel('Revenue ($)')
axes[0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${int(x):,}')) # Format y-axis with commas and dollar sign

# Plot 1: Total Visits by Year
axes[1].bar(yearly_summary['Year'], yearly_summary['total_patient_visits'], color='steelblue')
axes[1].set_title('Total Patient Visits by Year')
axes[1].set_xlabel('Year')
axes[1].set_ylabel('Number of Visits')

plt.savefig('healthcare_KPI_summary.png') # Save and show
plt.show()

# Create combo graph
fig, ax1 = plt.subplots(figsize=(8, 6))

# Bars for visits and bills
x = np.arange(len(yearly_summary['Year']))
width = 0.35

bars1 = ax1.bar(x - width/2, yearly_summary['total_patient_visits'], 
                width, label='Patient Visits', color='steelblue', alpha=0.8)
bars2 = ax1.bar(x + width/2, yearly_summary['total_bills'], 
                width, label='Bills', color='coral', alpha=0.8)

# Line for billing rate
ax2 = ax1.twinx()
line = ax2.plot(yearly_summary['Year'], yearly_summary['billing_rate'], 
                color='green', marker='o', linewidth=2.5, markersize=8, 
                label='Billing Rate')

# Formatting
ax1.set_xlabel('Year', fontsize=12)
ax1.set_ylabel('Patient visits, bills', fontsize=12)
ax2.set_ylabel('Billing Rate (%)', fontsize=12, color='green')
ax2.tick_params(axis='y', labelcolor='green')

# Format numbers with commas and percent
ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'))
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x:.1%}'))

# Set x-ticks
ax1.set_xticks(x)
ax1.set_xticklabels(yearly_summary['Year'])

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}', ha='center', va='bottom', fontsize=9)

for i, (year, rate) in enumerate(zip(yearly_summary['Year'], yearly_summary['billing_rate'])):
    ax2.text(year, rate + 1, f'{rate:.2f}', ha='center', fontsize=9, 
             color='green', fontweight='bold')

# Title and legend
plt.title('Patient Visits, Bills & Billing Rate (2020-2023)', fontsize=14, fontweight='bold')
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

# Grid
ax1.grid(True, alpha=0.3, axis='y')

plt.savefig('patient_visits_vs_bills.png')
plt.show()  


