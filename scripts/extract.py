# scripts/extract.py
import pandas as pd, os, sys

def extract_data(path: str) -> pd.DataFrame:
    print(f"\n[EXTRACT] Leyendo archivo: {path}")
    if not os.path.exists(path):
        print(f"  ❌ Archivo no encontrado: {path}"); sys.exit(1)

    df = pd.read_csv(path, low_memory=False)
    print(f"  ✅ Filas: {len(df):,}  |  Columnas: {len(df.columns)}")
    print(f"  📋 {list(df.columns)}")
    return df
