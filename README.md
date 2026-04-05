# Healthcare BI Analysis

## Table of contents
- [Project Overview](#project_overview)
- [Data Prerequisites](#data_prerequisites)
- [Data Extraction, Loading and Transformation](#data_extraction_loading_and_transformation)
- [Analytics & Visualization](#analytics_&_visualization)
- [Addressed Questions](#key_questions_being_addressed_by_eda)
- [Results & Findings](#results_&_findings)
- [Recommendation](#recommendation)
- [Limitations](#limitations)

### Project Overview

This project will provide insights on the operations of a healthcare facility and also tacle different emerging issues facing healthcare facilities when it comes to resource allocation. The analysis of the healthcare business is crucial to enable continuous provision of not only good healthcare services but also affordable and reliable healthcare services. Therefore, it's important for healthcare companies to strategize and conduct proper resource planning using data to ensure they are working optimally.


### Data Prerequisites

- Data source: Healthcare data: [Healthcare Management System_Data](https://www.kaggle.com/datasets/anouskaabhisikta/healthcare-management-system/data)
- Analytics Tool: Python - Data ETL, Exploratory Analysis and Data Visualization

### Data Extraction, Loading and Transformation [Python](dataanalysis_health.py)

Performed the following tasks: 
1. Data Loading
   ```python
   import kagglehub; print('kagglehub imported successfully')
   from kagglehub import KaggleDatasetAdapter
   ```
3. Data Cleaning and inspection
4. Merging and joining of datasets
5. Handling missing values

### Analytics & Visualization [Python](dataanalysis_health.py)

1. Exploratory Data Analysis
   - Total Revenue, Visits, Revenue per Visit, Growth rates     
2. Data Visualization
   - Revenue Trends, Visits trends, Billing rates

### Key questions being adressed by EDA

- What is the total visits of patients being billed?
- What percentage of visits are billable?
- What is the revenue and cost implicated?
- What is the distribution per service and per billing?
- Which service has low and high billing rate?

### Results and Findings

## Tables

## Charts
### Healthcare Trends (2020 - 2023) - Visits, Revenue
![Healthcare Visits and Revenue Trends](healthcare_KPI_summary.png)
### Billing rate of actual visits (2020 - 2023)
![Billing rate](patient_visits_vs_bills.png)

#### Summary 
The analysis results were as follows:
1. The healthcare facility had the lowest revenue in the year with the lowest billing
2. The was a consistent decline in revenue in 2021 o 2022 due to .... compared to 2023 where...
3. The speciality with the highest visits was ....

### Recommendation

Based on the analysis conducted, I would recommend the following:
- 
- 

### Limitations
- The zero values in PatientsID were removed since they are considured as no visits

### References
- Kaggle



