ETL Project – Traffic Accidents in Colombia
Sustainable Development Goal: Road Safety (SDG 3)

##1. Project Objective

The objective of this project is to design and implement the first stage of a production-style ETL pipeline using an open government dataset from Colombia related to traffic accidents.

This project focuses on building a Data Warehouse architecture that enables analytical insights about traffic accidents and their impact on road safety.

The pipeline performs:

Data extraction from a raw CSV dataset

Data cleaning and transformation

Dimensional modeling

Loading structured data into a PostgreSQL Data Warehouse

Visualization through Power BI

This analysis supports the Sustainable Development Goal (SDG) 3 – Good Health and Well-being, particularly in reducing injuries and deaths caused by traffic accidents.

##2. Business Scenario

Traffic accidents represent a major public safety issue in Colombia. Government institutions require analytical tools to understand:

Where accidents occur most frequently

Which vehicle types are most involved

The severity of accidents

Temporal trends in accident occurrences

A Data Warehouse enables efficient analysis of these patterns for policy planning and prevention strategies.

##3. Analytical Questions

The system is designed to answer the following questions:

How many traffic accidents occur per year?

Which vehicle types are most involved in accidents?

What is the distribution of accident severity?

In which departments or municipalities do most accidents occur?

How do accident trends evolve over time?

##4. Key Performance Indicators (KPIs)

The main KPIs include:

Total number of accidents

Accidents by vehicle type

Accidents by severity

Accidents by year

Accidents by geographic location

Example KPI from the dashboard:

Total accidents: 407,000+

##5. Data Source

The dataset used is an open government dataset from Colombia related to road traffic accidents.

Characteristics:

More than 50,000 records

More than 10 attributes

Publicly available government data

Structured tabular format (CSV)

Reasons for selecting this dataset:

High analytical relevance for road safety

Large volume of records

Suitable for dimensional modeling

Allows geographic, temporal, and categorical analysis

##6. Data Profiling and Quality Assessment

Before building the ETL process, an exploratory data analysis was performed.

The following checks were applied:

Null Value Analysis

Some columns contained missing values which were handled through cleaning or filtering.

Duplicate Detection

Duplicate records were identified and removed to ensure data integrity.

Data Type Validation

Columns were converted to appropriate types such as:

Integer

Date

String

Categorical values

Inconsistent Formatting

Standardization was applied to columns such as:

Vehicle type names

Geographic fields

Severity categories

##7. Grain Definition (Fact Table)

The grain of the fact table is:

One record per accident event classified by time, location, vehicle type, and severity.

Each row in the fact table represents:

The count of accidents for a specific combination of time, location, vehicle type, and severity.

Measure:

cantidad → number of accidents

##8. Dimensional Data Model

A Star Schema was designed for the Data Warehouse.

Fact Table:

dw_fact_accidentes

Dimension Tables:

dw_dim_tiempo

dw_dim_ubicacion

dw_dim_vehiculo

dw_dim_gravedad

This structure allows efficient aggregation and filtering for analytical queries.

9. Star Schema Structure
Fact Table
dw_fact_accidentes
Column	Description
tiempo_id	Foreign key to time dimension
ubicacion_id	Foreign key to location dimension
vehiculo_id	Foreign key to vehicle dimension
gravedad_id	Foreign key to severity dimension
cantidad	Number of accidents
Dimension Tables
dw_dim_tiempo

Attributes:

tiempo_id (PK)

fecha

anio

mes

dia

hora

grupo_horario

This dimension enables time-based analysis.

dw_dim_ubicacion

Attributes:

ubicacion_id (PK)

departamento

municipio

This dimension enables geographical analysis of accidents.

dw_dim_vehiculo

Attributes:

vehiculo_id (PK)

tipo_vehiculo

marca

modelo

edad

This dimension describes the vehicles involved in accidents.

dw_dim_gravedad

Attributes:

gravedad_id (PK)

gravedad

Represents the severity of the accident:

With injuries

Fatal accidents

##10. ETL Process

The ETL pipeline was implemented using Python and Jupyter Notebook.

Extract

The raw accident dataset is loaded from a CSV file using Python libraries such as:

pandas

Example:

df = pd.read_csv("accidentes.csv")
Transform

Several transformations were applied:

Data Cleaning

Remove duplicates

Handle missing values

Standardization

Normalize categorical values

Clean text fields

Type Conversion

Convert date columns

Convert numeric fields

Derived Columns

Examples:

Year

Month

Hour groups

Surrogate Key Generation

Unique IDs were created for dimension tables.

Validation Rules

Ensure no null foreign keys

Ensure valid categorical values

Load

The transformed data is loaded into PostgreSQL.

Steps:

Load dimension tables

Generate surrogate keys

Load fact table

Maintain referential integrity

Tools used:

SQL

PostgreSQL

Python database connectors

##11. Database Layer

The Data Warehouse is implemented in PostgreSQL.

Schema used:

dw

Tables created:

dw_fact_accidentes

dw_dim_tiempo

dw_dim_ubicacion

dw_dim_vehiculo

dw_dim_gravedad

This design supports efficient analytical queries and BI tools.

##12. Visualization

The analytical dashboard was built using Power BI.

Example insights:

Total accidents KPI

Accidents by vehicle type

Accidents by severity

Accident trends over time

These visualizations are generated directly from the Data Warehouse, not from the raw CSV.

##13. System Architecture

The architecture follows a classic ETL pipeline:

Raw CSV Dataset
       ↓
Python ETL Pipeline
       ↓
Data Cleaning & Transformation
       ↓
PostgreSQL Data Warehouse
       ↓
Power BI Dashboard

##14. How to Run the Project

1 Install dependencies
pip install pandas psycopg2 sqlalchemy

2 Configure database connection

3 Run ETL pipeline

Execute the ETL notebook or Python script:

etl_pipeline.ipynb
4 Verify tables in PostgreSQL

Tables should appear in:

dw schema
5 Open Power BI dashboard

Connect Power BI to PostgreSQL and load the Data Warehouse tables.

##15. Example Output

Example dashboard insights:

Total accidents: 407K+

Most common vehicle type involved: Motorcycle

Majority of accidents: With injuries

Trend analysis by year

##16. Technologies Used

Python

Pandas

Jupyter Notebook

PostgreSQL

SQL

Power BI

GitHub
