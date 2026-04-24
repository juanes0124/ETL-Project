# scripts/load.py
# Carga el modelo dimensional a PostgreSQL usando SQLAlchemy.

from sqlalchemy import create_engine, text
import pandas as pd

DDL = """
CREATE SCHEMA IF NOT EXISTS dw;

CREATE TABLE IF NOT EXISTS dw.dim_tiempo (
    tiempo_id       INTEGER PRIMARY KEY,
    fecha           TIMESTAMP,
    anio            INTEGER,
    mes             INTEGER,
    dia             INTEGER,
    hora            INTEGER,
    grupo_horario   VARCHAR(20),
    dia_semana      VARCHAR(20),
    es_fin_semana   BOOLEAN
);

CREATE TABLE IF NOT EXISTS dw.dim_ubicacion (
    ubicacion_id    INTEGER PRIMARY KEY,
    departamento    VARCHAR(100),
    municipio       VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dw.dim_vehiculo (
    vehiculo_id     INTEGER PRIMARY KEY,
    tipo_vehiculo   VARCHAR(100),
    marca           VARCHAR(100),
    modelo          FLOAT,
    edad            FLOAT
);

CREATE TABLE IF NOT EXISTS dw.dim_gravedad (
    gravedad_id     INTEGER PRIMARY KEY,
    gravedad        VARCHAR(100),
    nivel_severidad VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS dw.dim_clima (
    clima_id             INTEGER PRIMARY KEY,
    departamento         VARCHAR(100),
    fecha                DATE,
    temperatura_max      FLOAT,
    temperatura_min      FLOAT,
    precipitacion_mm     FLOAT,
    velocidad_viento_max FLOAT,
    codigo_clima         INTEGER,
    descripcion_clima    VARCHAR(100),
    condicion_lluvia     VARCHAR(30),
    latitud              FLOAT,
    longitud             FLOAT
);

CREATE TABLE IF NOT EXISTS dw.fact_accidentes (
    accidente_id    SERIAL PRIMARY KEY,
    tiempo_id       INTEGER REFERENCES dw.dim_tiempo(tiempo_id),
    ubicacion_id    INTEGER REFERENCES dw.dim_ubicacion(ubicacion_id),
    vehiculo_id     INTEGER REFERENCES dw.dim_vehiculo(vehiculo_id),
    gravedad_id     INTEGER REFERENCES dw.dim_gravedad(gravedad_id),
    clima_id        INTEGER REFERENCES dw.dim_clima(clima_id),
    cantidad        INTEGER DEFAULT 1
);
"""

def get_engine(cfg: dict):
    url = (f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}"
           f"@{cfg['host']}:{cfg['port']}/{cfg['database']}")
    return create_engine(url)

def _limpiar_df(df):
    """Convierte tipos numpy a tipos Python nativos para PostgreSQL."""
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == 'bool' or str(df[col].dtype) == 'bool':
            df[col] = df[col].astype(bool)
        elif hasattr(df[col].dtype, 'numpy_dtype'):
            pass
    return df.astype(object).where(df.notna(), None)
def load_all(engine, dim_tiempo, dim_ubicacion, dim_vehiculo,
             dim_gravedad, dim_clima, fact_accidentes):
    print("\n" + "="*55)
    print("  CARGA AL DATA WAREHOUSE (PostgreSQL)")
    print("="*55)

    with engine.begin() as con:
        con.execute(text(DDL))
    print("  ✅ Esquema y tablas creadas/verificadas")

    # Orden: primero dimensiones, luego fact (por las FK)
    print("\n  Cargando dimensiones...")
    with engine.begin() as con:
        for t in ["fact_accidentes","dim_clima","dim_gravedad",
                  "dim_vehiculo","dim_ubicacion","dim_tiempo"]:
            con.execute(text(f"TRUNCATE dw.{t} CASCADE"))

    for df, tabla in [
        (dim_tiempo,    "dim_tiempo"),
        (dim_ubicacion, "dim_ubicacion"),
        (dim_vehiculo,  "dim_vehiculo"),
        (dim_gravedad,  "dim_gravedad"),
        (dim_clima,     "dim_clima"),
    ]:
        df_clean = df.copy()
        df_clean = df_clean.astype(object).where(df_clean.notna(), None)
        df_clean.to_sql(tabla, con=engine, schema="dw",
                        if_exists="append", index=False, chunksize=500)
        print(f"    ✅ dw.{tabla}: {len(df):,} filas")

    print("\n  Cargando tabla de hechos...")
    fact_clean = fact_accidentes.copy()
    fact_clean = fact_clean.astype(object).where(fact_clean.notna(), None)
    fact_clean.to_sql("fact_accidentes", con=engine, schema="dw",
                      if_exists="append", index=False, chunksize=500)
    print(f"    ✅ dw.fact_accidentes: {len(fact_accidentes):,} filas")
        
