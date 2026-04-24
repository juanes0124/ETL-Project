# 📊 Exploratory Data Analysis (EDA)

## 1. Objective

The purpose of this Exploratory Data Analysis (EDA) is to understand the structure, quality, and distribution of both data sources (the original accidents dataset and the external climate API), identify potential data quality issues, and evaluate how the integration of the new data source enhances the analytical model.

---

## 2. Data Sources Description

### Primary Dataset (Accidents Data)
- Contains approximately **70,000 records**
- Includes information about:
  - Time of the accident
  - Location (department and municipality)
  - Vehicle type
  - Severity of the accident

### External API (Climate Data)
- Source: Open-Meteo API
- Provides weather data by date and location
- Includes variables such as:
  - Maximum temperature
  - Precipitation (mm)
  - Maximum wind speed

---

## 3. Data Profiling & Quality Assessment

### dim_tiempo
- No duplicate values in `tiempo_id`
- No null values in `fecha`
- All attributes (year, month, day, hour) fall within valid ranges
- Valid categorical values in `grupo_horario`

### dim_ubicacion
- No duplicate values in `ubicacion_id`
- No null values in `departamento` and `municipio`
- Low cardinality (52 unique locations)

### dim_vehiculo
- No duplicate values in `vehiculo_id`
- No null values in `tipo_vehiculo`
- `edad` values fall within a valid range

### dim_gravedad
- No duplicate values in `gravedad_id`
- No null values in `gravedad`

### dim_clima (API Data)
- No duplicate values in `clima_id`
- No null values in key fields (`departamento`, `fecha`)
- All numerical variables within valid ranges:
  - Temperature
  - Precipitation
  - Wind speed

### fact_accidentes
- No null values in foreign keys:
  - `tiempo_id`
  - `ubicacion_id`
  - `gravedad_id`
  - `vehiculo_id`
  - `clima_id`
- Measure `cantidad = 1` is consistent across all records
- Referential integrity is preserved

---

## 4. Exploratory Analysis

### Temporal Distribution
- Accidents show concentration in specific hours of the day
- Peaks are likely associated with rush hours

### Geographic Distribution
- Certain municipalities present higher accident frequencies
- This may correlate with population density and traffic volume

### Vehicle Analysis
- Some vehicle types are more frequently involved in accidents
- Suggests potential risk patterns

### Climate Analysis
- Higher accident rates observed during rainy conditions
- Temperature and wind variations show potential influence

---

## 5. Impact of API Integration

The integration of climate data enhanced the analytical model by introducing environmental variables, enabling deeper insights into accident patterns and external risk factors.

---

## 6. Data Issues & Considerations

- Differences in date formats required standardization
- Temporal alignment between datasets was necessary
- Assumptions were made when matching climate data with accident records

---

## 7. Conclusion

The datasets are of high quality and suitable for integration. The inclusion of climate data improves the analytical power of the model and supports more comprehensive insights into accident behavior.
