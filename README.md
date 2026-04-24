# 🚗 ETL Accidentes de Tráfico — Segunda Entrega

## ⚡ Pasos para ejecutar TODO desde cero

---

### PASO 1 — Abrir VS Code en la carpeta del proyecto

```
Archivo → Abrir Carpeta → seleccionar "etl_proyecto_v2"
```

---

### PASO 2 — Crear la base de datos en PostgreSQL

Abre **pgAdmin** o la terminal de PostgreSQL y ejecuta:

```sql
CREATE DATABASE etl_accidentes;
```

---

### PASO 3 — Editar tus credenciales

Abre el archivo **`config.py`** y cambia la contraseña si es necesario:

```python
DB = {
    "host":     "localhost",
    "port":     "5432",
    "user":     "postgres",
    "password": "123",          # ← pon tu contraseña real aquí
    "database": "etl_accidentes"
}
```

---

### PASO 4 — Instalar dependencias

Abre la terminal de VS Code (`Ctrl + Ñ`) y ejecuta:

```bash
pip install pandas numpy requests sqlalchemy psycopg2-binary pyarrow
```

> Para Airflow también:
> ```bash
> pip install apache-airflow
> ```

---

### PASO 5 — Copiar el CSV de datos

Coloca el archivo **`accidentes_colombia.csv`** dentro de la carpeta **`data/`**:

```
etl_proyecto_v2/
  data/
    accidentes_colombia.csv   ← aquí
```

---

### PASO 6 — Ejecutar el pipeline (sin Airflow)

```bash
python run_pipeline.py
```

Verás en la terminal:
- ✅ Extracción del CSV (70,000 filas)
- 🌤️ Datos climáticos de la API Open-Meteo
- 🔗 Transformación e integración de ambas fuentes
- 🔍 Validación de calidad de datos
- 📦 Carga a PostgreSQL

---

### PASO 7 — Verificar en pgAdmin

Abre **pgAdmin** → base de datos `etl_accidentes` → esquema `dw`:

```
dw.dim_tiempo
dw.dim_ubicacion
dw.dim_vehiculo
dw.dim_gravedad
dw.dim_clima          ← nueva, viene de la API
dw.fact_accidentes
```

---

### PASO 8 — Conectar Power BI

1. Abre **Power BI Desktop**
2. `Obtener datos` → `PostgreSQL`
3. Servidor: `localhost`
4. Base de datos: `etl_accidentes`
5. Selecciona las 6 tablas del esquema `dw`
6. ¡Crea tus visualizaciones!

**Consulta sugerida para Power BI:**
```sql
SELECT
    f.cantidad,
    t.anio, t.mes, t.grupo_horario, t.dia_semana,
    u.departamento, u.municipio,
    v.tipo_vehiculo, v.marca,
    g.gravedad, g.nivel_severidad,
    c.descripcion_clima, c.condicion_lluvia,
    c.precipitacion_mm, c.temperatura_max
FROM dw.fact_accidentes f
LEFT JOIN dw.dim_tiempo     t ON f.tiempo_id    = t.tiempo_id
LEFT JOIN dw.dim_ubicacion  u ON f.ubicacion_id = u.ubicacion_id
LEFT JOIN dw.dim_vehiculo   v ON f.vehiculo_id  = v.vehiculo_id
LEFT JOIN dw.dim_gravedad   g ON f.gravedad_id  = g.gravedad_id
LEFT JOIN dw.dim_clima      c ON f.clima_id     = c.clima_id;
```

---

### PASO 9 — Usar con Airflow (opcional)

```bash
# Inicializar Airflow (solo la primera vez)
airflow db init
airflow users create --username admin --password admin \
    --firstname Admin --lastname User --role Admin --email admin@example.com

# Apuntar Airflow a tu carpeta de DAGs
export AIRFLOW__CORE__DAGS_FOLDER=/ruta/a/etl_proyecto_v2/dags

# Arrancar
airflow webserver --port 8080 &
airflow scheduler &

# Abrir en el navegador: http://localhost:8080
# Buscar el DAG: etl_accidentes_v2
```

---

## 📁 Estructura del proyecto

```
etl_proyecto_v2/
├── config.py                ← credenciales PostgreSQL
├── run_pipeline.py          ← ejecuta todo sin Airflow
├── requirements.txt
├── data/
│   └── accidentes_colombia.csv
├── scripts/
│   ├── extract.py           ← lee el CSV
│   ├── extract_api.py       ← API Open-Meteo (clima)
│   ├── transform.py         ← limpieza + modelo dimensional
│   ├── validate.py          ← validaciones tipo Great Expectations
│   └── load.py              ← carga a PostgreSQL
├── dags/
│   └── dag_accidentes.py    ← DAG de Airflow
└── outputs/
    └── validation_*.json    ← reportes de validación
```

---

## 🔑 Tecnologías

| Capa | Herramienta |
|------|-------------|
| Datos primarios | CSV accidentes Colombia (70,000 filas) |
| API externa | Open-Meteo (clima histórico, gratis) |
| Transformación | Python + Pandas |
| Validación | Great Expectations (estilo) |
| Base de datos | PostgreSQL — esquema `dw` |
| Orquestación | Apache Airflow |
| Visualización | Power BI |
| Desarrollo | VS Code |

---

# 🎯 Objetivos Refinados

El objetivo de este proyecto es operacionalizar un pipeline ETL analítico enfocado en accidentes de tránsito en Colombia, integrando una API externa complementaria de clima.

Este pipeline permite:

- Identificar patrones de accidentes por fecha, ubicación y tipo de vehículo.
- Analizar la relación entre las condiciones climáticas y la severidad de los accidentes.
- Proveer datos confiables y validados para dashboards de inteligencia de negocios.
- Automatizar el proceso ETL usando Apache Airflow.

---

# 📊 Resumen del Data Profiling

## Profiling del Dataset Principal

El dataset principal contiene más de **70.000 filas** y más de **10 atributos**, incluyendo:

- Fecha y hora del accidente
- Departamento y municipio
- Tipo y marca del vehículo
- Severidad y número de víctimas

### Problemas de calidad encontrados:

- Valores nulos en algunos campos descriptivos
- Formatos de texto inconsistentes
- Registros duplicados en algunas combinaciones
- Diferentes formatos de fecha/hora

### Acciones tomadas:

- Reemplazo de valores nulos
- Eliminación de duplicados
- Estandarización de texto y fechas

---

## Profiling del Dataset de la API (Open-Meteo)

La API del clima proporciona:

- Temperatura máxima
- Temperatura mínima
- Precipitación
- Indicador de lluvia
- Código o descripción del clima

### Problemas de calidad encontrados:

- Fechas faltantes para algunas ubicaciones
- Valores nulos en precipitación
- Posibles outliers en temperatura

### Acciones tomadas:

- Manejo de nulos
- Valores por defecto para datos faltantes
- Validación de rangos en métricas climáticas

---

# 🌤️ Detalles de la API y por qué fue elegida

La API seleccionada fue Open-Meteo porque:

- Es gratuita y pública
- Proporciona datos históricos del clima
- No requiere API Key
- Fácil integración mediante solicitudes HTTP
- Agrega valor analítico para explicar el comportamiento de accidentes bajo condiciones climáticas

Esta API mejora el modelo dimensional agregando la tabla **dim_clima**.

---

# 🔗 Estrategia de Integración de Datos

La integración entre ambas fuentes se realizó usando:

### Claves de unión

- `fecha`
- `departamento`

### Estrategia

Se aplicó un **LEFT JOIN** para conservar todos los registros de accidentes.

### Manejo de inconsistencias

- Registros climáticos faltantes se reemplazan con valores por defecto
- Las fechas fueron estandarizadas antes del merge

### Alineación temporal

Los datos climáticos se alinean diariamente con la fecha del accidente.

---

# ⭐ Diseño del Modelo Dimensional

## Grano

El grano de la tabla de hechos es:

**Un evento de accidente agregado por fecha, ubicación, vehículo, severidad y condición climática.**

## Tabla de Hechos

- `fact_accidentes`

Medidas:

- cantidad
- heridos
- muertos

## Tablas Dimensionales

- dim_tiempo
- dim_ubicacion
- dim_vehiculo
- dim_gravedad
- dim_clima

La API impactó el modelo añadiendo capacidades analíticas relacionadas con el clima.

---

# ✅ Estrategia de Validación

Se implementó una capa de validación inspirada en Great Expectations.

## Reglas Críticas

- Validación de nulos en columnas clave
- Restricciones de unicidad
- Consistencia referencial

## Reglas No Críticas

- Validación de rangos numéricos
- Detección de outliers
- Validaciones de consistencia lógica

Ejemplos:

- Temperatura entre -10 y 50
- Precipitación mayor o igual a 0
- Sin duplicados en la tabla de hechos

La validación se ejecuta antes de cargar al Data Warehouse.

---

# 🔄 Diseño del DAG en Airflow

El DAG representa el flujo completo ETL:

```text
inicio
↓
extract_csv
↓
extract_api
↓
transform
↓
validate
↓
load
↓
fin
