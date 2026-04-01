# Healthcare BI Analysis

## Table of contents
- [Project Overview](#project_overview)
- [Recommendation](#recommendation)

### Project Overview

This project will provide insights on the operations of a healthcare facility and also tacle different emerging issues facing healthcare facilities when it comes to resource allocation. The analysis of the healthcare business is crucial to enable continuous provision of not only good healthcare services but also affordable and reliable financial services.Therefore, it's important for healthcare companies to strategies and conduct proper resource planning using data to ensure they are working optimally.


### Data Sources

Healthcare data: [Healthcare Management System_Data](https://www.kaggle.com/datasets/anouskaabhisikta/healthcare-management-system/data)

### Tools

- SQL - Data Cleaning and EDA (Exploratory Data Analysis)
- Python - Data ETL, Prescriptive Analysis and Data Visualization

#### Preparing and installing data in Python
''' 
#download dependencies pip install kagglehub[pandas-datasets]
# download the dataset from Kaggle
import kagglehub; print('kagglehub imported successfully')
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
billing = dfs["Billing.csv"]
doctor = dfs["Doctor.csv"]
procedures = dfs["Medical Procedure.csv"]
patients = dfs["Patient.csv"]

'''

### Data Cleaning

Performed the following tasks: 
1. Data Loading and inspection,
2. Merging and joining of datasets
3. Handling missing values,
4. Data Cleaning and formatting

### Exploratory Analysis

- What is the average visits of patients?
- What is the revenue and cost implicated?
- What is the distribution per service and per center?

### Analytics

Introduce code/feature
```SQL
SELECT * FROM table 1
where Center = LAV;
```
### Findings
 
The analysis results were as follows:
1. DO
2. Do
3. Do

### Recommendation
Based on the analysis conducted
- Go
- Go

### Limitations
Outlliers, zero values

### References
Links to webpage
Book
[Stack_overflow]

|Name|Name2|

|....|.....|

|Meme|Meee|

