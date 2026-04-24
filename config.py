# config.py — Configuración central del proyecto
# ¡Edita este archivo con tus credenciales de PostgreSQL!

DB = {
    "host":     "localhost",
    "port":     "5432",
    "user":     "postgres",
    "password": "123",          
    "database": "etl_accidentes"
}

# Ruta al CSV de accidentes
CSV_PATH = "data/accidentes_colombia.csv"

# Ruta donde se guardará la base de datos SQLite de respaldo
SQLITE_PATH = "data/warehouse.db"
