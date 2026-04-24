# scripts/transform.py
import pandas as pd
import numpy as np

# ── LIMPIEZA ─────────────────────────────────────────────────────────────────

def clean_accidents(df: pd.DataFrame) -> pd.DataFrame:
    print("\n[CLEAN] Limpiando dataset de accidentes...")
    df = df.copy()
    n0 = len(df)

    df.drop_duplicates(inplace=True)
    print(f"  Duplicados eliminados: {n0-len(df):,}")

    for col in ["DEPARTAMENTO_ACCIDENTE","MUNICIPIO_ACCIDENTE","TIPO_VEHICULO",
                "MARCA_VEHICULO","GRAVEDAD_ACCIDENTE","CLASE_ACCIDENTE","ZONA","VIA","CONDICION_VIA"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper().replace("NAN", np.nan)

    df["FECHA_ACCIDENTE"] = pd.to_datetime(df["FECHA_ACCIDENTE"], errors="coerce")
    inv = df["FECHA_ACCIDENTE"].isna().sum()
    df.dropna(subset=["FECHA_ACCIDENTE"], inplace=True)
    print(f"  Fechas inválidas: {inv:,}")

    df = df[(df["FECHA_ACCIDENTE"].dt.year >= 2010) & (df["FECHA_ACCIDENTE"].dt.year <= 2025)]

    for col in ["DEPARTAMENTO_ACCIDENTE","MUNICIPIO_ACCIDENTE","TIPO_VEHICULO",
                "GRAVEDAD_ACCIDENTE","CLASE_ACCIDENTE","ZONA","VIA"]:
        if col in df.columns:
            df[col] = df[col].fillna("DESCONOCIDO")

    if "EDAD_VEHICULO" in df.columns:
        df["EDAD_VEHICULO"] = pd.to_numeric(df["EDAD_VEHICULO"], errors="coerce")
        df["EDAD_VEHICULO"] = df["EDAD_VEHICULO"].fillna(df["EDAD_VEHICULO"].median()).clip(0)

    if "MARCA_VEHICULO" in df.columns:
        df["MARCA_VEHICULO"] = df["MARCA_VEHICULO"].fillna("DESCONOCIDO")

    print(f"  ✅ Accidentes limpios: {len(df):,} filas")
    return df

def clean_weather(df: pd.DataFrame) -> pd.DataFrame:
    print("\n[CLEAN] Limpiando datos climáticos...")
    df = df.copy()
    for col in ["temperatura_max","temperatura_min"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").clip(-5, 45)
        df[col] = df[col].fillna(df[col].median())
    df["precipitacion_mm"] = pd.to_numeric(df["precipitacion_mm"],errors="coerce").clip(0).fillna(0)
    df["velocidad_viento_max"] = pd.to_numeric(df["velocidad_viento_max"],errors="coerce").clip(0).fillna(df["velocidad_viento_max"].median())
    df["codigo_clima"] = pd.to_numeric(df["codigo_clima"],errors="coerce").fillna(-1).astype(int)
    df["descripcion_clima"] = df["descripcion_clima"].fillna("Sin datos")
    df["condicion_lluvia"] = df["condicion_lluvia"].fillna("Sin datos")
    print(f"  ✅ Clima limpio: {len(df):,} registros")
    return df

# ── TRANSFORMACIÓN ────────────────────────────────────────────────────────────

def transform_accidents(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["anio"]        = df["FECHA_ACCIDENTE"].dt.year
    df["mes"]         = df["FECHA_ACCIDENTE"].dt.month
    df["dia"]         = df["FECHA_ACCIDENTE"].dt.day
    df["hora"]        = df["FECHA_ACCIDENTE"].dt.hour
    df["dia_semana"]  = df["FECHA_ACCIDENTE"].dt.day_name()
    df["es_fin_semana"] = df["FECHA_ACCIDENTE"].dt.dayofweek >= 5
    df["grupo_horario"] = pd.cut(df["hora"], bins=[0,6,12,18,24],
                                 labels=["Madrugada","Mañana","Tarde","Noche"], right=False).astype(str)
    df["fecha_solo"]  = df["FECHA_ACCIDENTE"].dt.strftime("%Y-%m-%d")
    return df

# ── DIMENSIONES ───────────────────────────────────────────────────────────────

def build_dim_tiempo(df):
    dim = df[["FECHA_ACCIDENTE","anio","mes","dia","hora",
              "grupo_horario","dia_semana","es_fin_semana"]].drop_duplicates().reset_index(drop=True)
    dim.columns = ["fecha","anio","mes","dia","hora","grupo_horario","dia_semana","es_fin_semana"]
    dim.insert(0, "tiempo_id", range(1, len(dim)+1))
    return dim

def build_dim_ubicacion(df):
    dim = df[["DEPARTAMENTO_ACCIDENTE","MUNICIPIO_ACCIDENTE"]].drop_duplicates().reset_index(drop=True)
    dim.columns = ["departamento","municipio"]
    dim.insert(0, "ubicacion_id", range(1, len(dim)+1))
    return dim

def build_dim_vehiculo(df):
    cols = [c for c in ["TIPO_VEHICULO","MARCA_VEHICULO","MODELO_VEHICULO","EDAD_VEHICULO"] if c in df.columns]
    dim = df[cols].drop_duplicates().reset_index(drop=True)
    dim.columns = ["tipo_vehiculo","marca","modelo","edad"][:len(cols)]
    dim.insert(0, "vehiculo_id", range(1, len(dim)+1))
    return dim

def build_dim_gravedad(df):
    dim = df[["GRAVEDAD_ACCIDENTE"]].drop_duplicates().reset_index(drop=True)
    dim.columns = ["gravedad"]
    sev = {"MUERTO":"Alta","HERIDO":"Media","SOLO DAÑOS":"Baja","DAÑOS":"Baja"}
    dim["nivel_severidad"] = dim["gravedad"].apply(
        lambda g: next((v for k,v in sev.items() if k in str(g)),"Desconocida"))
    dim.insert(0, "gravedad_id", range(1, len(dim)+1))
    return dim

def build_dim_clima(df_clima):
    dim = df_clima.drop_duplicates(subset=["departamento","fecha"]).reset_index(drop=True)
    dim.insert(0, "clima_id", range(1, len(dim)+1))
    return dim

# ── TABLA DE HECHOS ───────────────────────────────────────────────────────────

def build_fact(df, dim_tiempo, dim_ubicacion, dim_vehiculo, dim_gravedad, dim_clima):
    print("\n[TRANSFORM] Construyendo tabla de hechos...")
    f = df.copy()

    # join tiempo
    f = f.merge(dim_tiempo[["tiempo_id","fecha","hora","grupo_horario"]],
                left_on=["FECHA_ACCIDENTE","hora","grupo_horario"],
                right_on=["fecha","hora","grupo_horario"], how="left")

    # join ubicacion
    f = f.merge(dim_ubicacion,
                left_on=["DEPARTAMENTO_ACCIDENTE","MUNICIPIO_ACCIDENTE"],
                right_on=["departamento","municipio"], how="left")

    # join vehiculo
    vcols_l = [c for c in ["TIPO_VEHICULO","MARCA_VEHICULO","MODELO_VEHICULO","EDAD_VEHICULO"] if c in f.columns]
    vcols_r = ["tipo_vehiculo","marca","modelo","edad"][:len(vcols_l)]
    f = f.merge(dim_vehiculo, left_on=vcols_l, right_on=vcols_r, how="left")

    # join gravedad
    f = f.merge(dim_gravedad[["gravedad_id","gravedad"]],
                left_on="GRAVEDAD_ACCIDENTE", right_on="gravedad", how="left")

    # join clima (llave: departamento + fecha_solo)
    f = f.merge(dim_clima[["clima_id","departamento","fecha"]],
                left_on=["DEPARTAMENTO_ACCIDENTE","fecha_solo"],
                right_on=["departamento","fecha"], how="left")

    fact = f[["tiempo_id","ubicacion_id","vehiculo_id","gravedad_id","clima_id"]].copy()
    fact["cantidad"] = 1

    nulos = fact[["tiempo_id","ubicacion_id","gravedad_id"]].isna().sum()
    if nulos.sum() > 0:
        print(f"  ⚠️  FKs nulas:\n{nulos[nulos>0]}")

    print(f"  ✅ fact_accidentes: {len(fact):,} filas")
    return fact

# ── PUNTO ÚNICO DE ENTRADA ────────────────────────────────────────────────────

def run_transform(df_raw, df_clima_raw):
    print("\n" + "="*55)
    print("  TRANSFORMACIÓN E INTEGRACIÓN")
    print("="*55)

    df_c  = clean_accidents(df_raw)
    df_wx = clean_weather(df_clima_raw)
    df_t  = transform_accidents(df_c)

    d_tiempo    = build_dim_tiempo(df_t)
    d_ubicacion = build_dim_ubicacion(df_t)
    d_vehiculo  = build_dim_vehiculo(df_t)
    d_gravedad  = build_dim_gravedad(df_t)
    d_clima     = build_dim_clima(df_wx)
    fact        = build_fact(df_t, d_tiempo, d_ubicacion, d_vehiculo, d_gravedad, d_clima)

    print(f"\n  dim_tiempo:      {len(d_tiempo):,}")
    print(f"  dim_ubicacion:   {len(d_ubicacion):,}")
    print(f"  dim_vehiculo:    {len(d_vehiculo):,}")
    print(f"  dim_gravedad:    {len(d_gravedad):,}")
    print(f"  dim_clima:       {len(d_clima):,}  ← API")
    print(f"  fact_accidentes: {len(fact):,}")
    return d_tiempo, d_ubicacion, d_vehiculo, d_gravedad, d_clima, fact
