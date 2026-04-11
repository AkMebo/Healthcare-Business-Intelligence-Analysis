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

# Joining tables: 
patients_seen_df = patients.merge(appointments, on='PatientID', how='outer').merge(billings, on='PatientID', how='outer')
appointments_patientdoc_df = appointments.merge(patients, on= 'PatientID', how= 'outer').merge(doctors, on='DoctorID', how='outer')
appointments_procedure_df = appointments_patientdoc_df.merge(procedures, on= 'AppointmentID', how= 'left').merge(billings, on= 'PatientID', how= 'left')


# Data cleaning: Drop unnecessary columns and rows with missing key IDs
columns_to_drop = [
    'DoctorContact',
    'firstname',
    'lastname',
    'email',
]
appointments_procedure_cln = appointments_procedure_df.drop(columns=columns_to_drop).dropna(subset=['AppointmentID']) # Drop rows with missing key IDs
appointments_procedure_cln.to_csv('appointments_df.csv', index=False) 
print(appointments_procedure_cln.to_csv)  #pip install openpyxl for excel
print(appointments_procedure_cln.columns.tolist())


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
from matplotlib.ticker import FuncFormatter

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
fig, ax1 = plt.subplots(figsize=(8, 6 ))

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

# Prepare the data - count visits by Year, Specialization, and Procedure
appointments_procedure_cln['Year'] = pd.to_datetime(appointments_procedure_cln['Date']).dt.year # Extract year from date
year_procedure = sorted(appointments_procedure_cln['Year'].unique()) # Get unique years for iteration

procedures_visits = appointments_procedure_cln.groupby(
    ['Year', 'Specialization', 'ProcedureName']
).size().reset_index(name='visit_procedure_count')
top_20_specialties = appointments_procedure_cln.groupby('Specialization').size().nlargest(20).index # Top 20 specialties by visit count
procedure_counts_top20 = procedures_visits[procedures_visits['Specialization'].isin(top_20_specialties)] # Filter to top 20 specialties

# Get top 5-10 procedures for better visualization
top_procedures = procedures_visits.groupby('ProcedureName')['visit_procedure_count'].sum().nlargest(8).index
procedure_counts_top20 = procedure_counts_top20[procedure_counts_top20['ProcedureName'].isin(top_procedures)]

fig, axes = plt.subplots(2, 2, figsize=(20, 16))
fig.subplots_adjust(hspace=0.4, wspace=0.3, top=0.92, bottom=0.08, left=0.12, right=0.85)
fig.suptitle('Top 20 Specialties: Procedure Visit Counts by Year', fontsize=16, fontweight='bold')
axes_flat = axes.flatten() # Flatten axes for easier iteration

# Create color map for procedures
colors = plt.cm.tab20(np.linspace(0, 1, len(top_procedures)))
procedure_colors = dict(zip(top_procedures, colors))

for idx, year in enumerate(year_procedure):
    # Filter data for the year
    year_procedure = procedure_counts_top20[procedure_counts_top20['Year'] == year]
    
    # Create pivot table: Specialization as rows, Procedure as columns
    pivot_data = year_procedure.pivot(
        index='Specialization', 
        columns='ProcedureName', 
        values='visit_procedure_count'
    ).fillna(0)
    
    # Ensure all top 20 specializations are present
    for specialty in top_20_specialties:
        if specialty not in pivot_data.index:
            pivot_data.loc[specialty] = 0
    
    # Sort by total visits
    pivot_data['Total'] = pivot_data.sum(axis=1)
    pivot_data = pivot_data.sort_values('Total', ascending=True) # Sort by total visits
    pivot_data = pivot_data.drop('Total', axis=1)
    
    # Plot stacked horizontal bar chart
    bottom = np.zeros(len(pivot_data))
    
    for procedure in top_procedures:
        if procedure in pivot_data.columns:
            values = pivot_data[procedure].values
            axes_flat[idx].barh(
                pivot_data.index, 
                values, 
                left=bottom,
                label=procedure,  # Only show legend on first subplot
                color=procedure_colors[procedure],
                edgecolor='white',
                linewidth=0.5
            )
            bottom += values
    
    # Customize the subplot
    axes_flat[idx].set_title(f'{year} - Total Visits: {year_procedure["visit_procedure_count"].sum():,}', fontsize=12, fontweight='bold')
    axes_flat[idx].set_xlabel('Number of Visits', fontsize=10)
    if idx == 0:
        axes_flat[idx].set_ylabel('Specialization', fontsize=14, fontweight='semibold', wrap=True)

    # Add grid
    axes_flat[idx].grid(True, alpha=0.3, axis='x')
    
    # Add value labels for total visits at the end of bars
    for i, (specialty, row) in enumerate(pivot_data.iterrows()):
        total = row.sum()
        if total > 0:
            axes_flat[idx].text(
                bottom[i] + 0.5, i, 
                f'{int(total)}', 
                va='center', ha='left', fontsize=7, alpha=0.8
            )

# Add single legend for the entire figure with adjusted position to prevent overlap
handles, labels = axes_flat[0].get_legend_handles_labels()
fig.legend(
    handles, labels, 
    title='Procedure Type', 
    title_fontsize=12,
    bbox_to_anchor=(1.02, 0.5), 
    loc='center left',
    fontsize=9,
    frameon=True,
    shadow=True
)

# Adjust layout to prevent any overlap
plt.tight_layout(rect=[0, 0, 0.85, 0.97])
plt.savefig('procedure_visits_by_specialty.png', bbox_inches='tight') # Save and show
plt.show()

# Specializations Revenue Yearly Trend and RPV
fig, axes = plt.subplots(1, 2, figsize=(14, 7))
fig.suptitle('Top 5 Specializations: Revenue Analysis', fontsize=14, fontweight='bold', y=1.02)

# Get top 5 specializations by total revenue
top_5_specialties = appointments_procedure_cln.groupby(['Specialization'])['Amount'].sum().nlargest(5).index.tolist()

print(appointments_procedure_cln.columns.tolist())
# Create pivot table for revenue by specialization and year 
revenue_pivot = appointments_procedure_cln[appointments_procedure_cln['Specialization'].isin(top_5_specialties)].pivot_table(
    index='Specialization',
    columns='Year',
    values='Amount',
    aggfunc='sum',
    fill_value=0
)

revenue_pivot['Total'] = revenue_pivot.sum(axis=1) # Sort by total revenue
revenue_pivot = revenue_pivot.sort_values('Total', ascending=True)
revenue_pivot = revenue_pivot.drop('Total', axis=1)

# Format revenue values
def format_revenue(x):
    if x >= 1_000_000:
        return f'${x/1_000_000:.1f}M'
    elif x >= 1_000:
        return f'${x/1_000:.0f}K'
    else:
        return f'${x:,.0f}'

# Format table data
table_data = revenue_pivot.copy()
for col in table_data.columns:
    table_data[col] = table_data[col].apply(format_revenue)

# Hide axes for table
axes[0].axis('tight')
axes[0].axis('off')

# Create table
revenue_table = axes[0].table(
    cellText=table_data.values,
    rowLabels=table_data.index,
    colLabels=table_data.columns,
    cellLoc='center',
    loc='center',
    bbox=[0, 0, 1, 1]
)

# Style table
revenue_table.auto_set_font_size(False)
revenue_table.set_fontsize(10)
revenue_table.scale(1.2, 1.6)

# Color header
for (row, col), cell in revenue_table.get_celld().items():
    if row == 0:
        cell.set_facecolor('#2c3e50')
        cell.set_text_props(weight='bold', color='white')
    else:
        cell.set_facecolor('#ecf0f1')
    cell.set_edgecolor('#bdc3c7')

axes[0].set_title('Revenue by Year (Top 5 Specializations)', 
                  fontsize=11, fontweight='bold', pad=20)

# Revenue Per Visit (Bar Chart)
# Calculate revenue per visit for all specializations
revenue_per_visit = appointments_procedure_cln.groupby('Specialization').agg({
    'Amount': 'sum',
    'PatientID': 'nunique'
}).reset_index()

revenue_per_visit['Revenue Per Visit'] = revenue_per_visit['Amount'] / revenue_per_visit['PatientID']
revenue_per_visit = revenue_per_visit.sort_values('Revenue Per Visit', ascending=True).head(10)

# Create horizontal bar chart
colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(revenue_per_visit)))
bars = axes[1].barh(range(len(revenue_per_visit)), 
                     revenue_per_visit['Revenue Per Visit'], 
                     color=colors)

# Customize chart
axes[1].set_yticks(range(len(revenue_per_visit)))
axes[1].set_yticklabels(revenue_per_visit['Specialization'], fontsize=9)
axes[1].set_xlabel('Revenue Per Visit ($)', fontsize=10, fontweight='semibold')
axes[1].set_title('Top 10 Specializations by Revenue Per Visit', 
                  fontsize=11, fontweight='bold', pad=20)

# Add value labels
for i, (bar, value) in enumerate(zip(bars, revenue_per_visit['Revenue Per Visit'])):
    axes[1].text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2, 
                 f'${value:,.0f}', va='center', ha='left', fontsize=8)

# Add grid
axes[1].grid(True, alpha=0.3, axis='x')

# Adjust layout
plt.tight_layout()

# Save and show
plt.savefig('specialization_revenue_analysis.png', bbox_inches='tight', dpi=300)
plt.show()