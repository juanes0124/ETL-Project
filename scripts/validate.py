# scripts/validate.py
# Validación de datos al estilo Great Expectations.
# Reglas CRÍTICAS detienen el pipeline; ADVERTENCIAS solo se registran.

import pandas as pd
import json
from datetime import datetime

REGLAS = {
    "fact_accidentes": {
        "criticas": [
            ("no_nulos",   "tiempo_id",    {},              "Sin tiempo no hay análisis temporal"),
            ("no_nulos",   "ubicacion_id", {},              "Sin ubicación no hay análisis geográfico"),
            ("no_nulos",   "gravedad_id",  {},              "Gravedad es métrica central"),
            ("valor_unico","cantidad",     {"valor":1},     "Grano: 1 fila = 1 accidente"),
            ("rango",      "tiempo_id",    {"min":1},       "IDs deben ser positivos"),
        ],
        "advertencias": [
            ("no_nulos",   "clima_id",     {},              "LEFT JOIN: puede ser NULL"),
            ("no_nulos",   "vehiculo_id",  {},              "Vehículo puede ser desconocido"),
        ]
    },
    "dim_tiempo": {
        "criticas": [
            ("unico",  "tiempo_id", {}, "PK debe ser única"),
            ("no_nulos","fecha",    {}, "Toda entrada temporal necesita fecha"),
            ("rango",  "anio", {"min":2010,"max":2025}, "Años válidos del dataset"),
            ("rango",  "mes",  {"min":1,  "max":12},    "Meses válidos"),
            ("rango",  "dia",  {"min":1,  "max":31},    "Días válidos"),
            ("rango",  "hora", {"min":0,  "max":23},    "Horas válidas"),
        ],
        "advertencias": [
            ("en_conjunto","grupo_horario",
             {"valores":["Madrugada","Mañana","Tarde","Noche"]},
             "Grupos horarios esperados"),
        ]
    },
    "dim_ubicacion": {
        "criticas": [
            ("unico",   "ubicacion_id", {}, "PK debe ser única"),
            ("no_nulos","departamento", {}, "Departamento es clave de análisis"),
        ],
        "advertencias": [
            ("no_nulos","municipio", {}, "Municipio puede faltar en algunos registros"),
        ]
    },
    "dim_vehiculo": {
        "criticas": [
            ("unico",   "vehiculo_id",  {}, "PK debe ser única"),
            ("no_nulos","tipo_vehiculo",{}, "Tipo de vehículo es esencial"),
        ],
        "advertencias": [
            ("rango","edad",{"min":0,"max":50},"Edad del vehículo 0-50 años"),
        ]
    },
    "dim_gravedad": {
        "criticas": [
            ("unico",   "gravedad_id",{}, "PK debe ser única"),
            ("no_nulos","gravedad",   {}, "Gravedad es dimensión core"),
        ],
        "advertencias": []
    },
    "dim_clima": {
        "criticas": [
            ("unico",   "clima_id",    {}, "PK debe ser única"),
            ("no_nulos","departamento",{}, "Llave de integración con accidentes"),
            ("no_nulos","fecha",       {}, "Llave temporal de integración"),
        ],
        "advertencias": [
            ("rango","temperatura_max",{"min":-5,"max":45},"Temperatura Colombia"),
            ("rango","precipitacion_mm",{"min":0,"max":500},"Precipitación diaria"),
            ("rango","velocidad_viento_max",{"min":0,"max":150},"Velocidad viento"),
        ]
    }
}

def _check(df, tipo, col, kwargs):
    if col not in df.columns:
        return False, f"Columna '{col}' no existe"
    if tipo == "no_nulos":
        n = df[col].isna().sum()
        return (n == 0), f"{n:,} nulos encontrados"
    if tipo == "unico":
        n = df[col].duplicated().sum()
        return (n == 0), f"{n:,} duplicados"
    if tipo == "rango":
        s = pd.to_numeric(df[col], errors="coerce")
        out = 0
        if "min" in kwargs: out += (s < kwargs["min"]).sum()
        if "max" in kwargs: out += (s > kwargs["max"]).sum()
        return (out == 0), f"{out:,} valores fuera de rango"
    if tipo == "valor_unico":
        n = (df[col] != kwargs["valor"]).sum()
        return (n == 0), f"{n:,} filas con valor distinto a {kwargs['valor']}"
    if tipo == "en_conjunto":
        n = (~df[col].isin(kwargs["valores"])).sum()
        return (n == 0), f"{n:,} valores fuera del conjunto"
    return False, "Tipo de regla desconocido"

def run_validation(tablas: dict) -> bool:
    print("\n" + "="*55)
    print("  VALIDACIÓN (Great Expectations style)")
    print("="*55)

    ok_total  = 0
    fail_crit = 0
    warnings  = 0
    reporte   = []

    for nombre, df in tablas.items():
        reglas = REGLAS.get(nombre, {"criticas":[],"advertencias":[]})
        print(f"\n  📋 {nombre}  ({len(df):,} filas)")

        for tipo, col, kwargs, just in reglas["criticas"]:
            paso, detalle = _check(df, tipo, col, kwargs)
            estado = "✅" if paso else "❌ CRÍTICO"
            print(f"    {estado}  [{tipo}] {col}  →  {detalle}")
            if paso: ok_total += 1
            else:
                fail_crit += 1
                reporte.append({"tabla":nombre,"tipo":"CRITICA","regla":tipo,
                                 "columna":col,"resultado":detalle,"justificacion":just})

        for tipo, col, kwargs, just in reglas["advertencias"]:
            paso, detalle = _check(df, tipo, col, kwargs)
            estado = "✅" if paso else "⚠️  ADVERTENCIA"
            print(f"    {estado}  [{tipo}] {col}  →  {detalle}")
            if not paso: warnings += 1

    print(f"\n  Resumen: ✅ {ok_total} OK  |  ❌ {fail_crit} críticas  |  ⚠️ {warnings} advertencias")

    # Guardar reporte JSON
    ruta = f"outputs/validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    import os; os.makedirs("outputs", exist_ok=True)
    with open(ruta, "w") as f:
        json.dump({"aprobado": fail_crit == 0, "criticas": fail_crit,
                   "advertencias": warnings, "detalle": reporte}, f, indent=2)
    print(f"  📄 Reporte guardado: {ruta}")

    if fail_crit > 0:
        raise ValueError(f"❌ PIPELINE DETENIDO: {fail_crit} validación(es) crítica(s) fallaron.")

    print("  ✅ VALIDACIÓN APROBADA — pipeline puede continuar")
    return True
