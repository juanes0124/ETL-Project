
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from config import DB, CSV_PATH
from scripts.extract     import extract_data
from scripts.extract_api import extract_weather_data
from scripts.transform   import run_transform
from scripts.validate    import run_validation
from scripts.load        import get_engine, load_all

def main():
    print("\n" + "█"*55)
    print("  ETL ACCIDENTES DE TRÁFICO — SEGUNDA ENTREGA")
    print("█"*55)

    # 1. EXTRACT CSV
    df_raw = extract_data(CSV_PATH)

    # 2. EXTRACT API
    df_clima = extract_weather_data(df_raw)

    # 3. TRANSFORM + INTEGRACIÓN
    dim_tiempo, dim_ubicacion, dim_vehiculo, dim_gravedad, dim_clima, fact = \
        run_transform(df_raw, df_clima)

    # 4. VALIDATE
    run_validation({
        "dim_tiempo":    dim_tiempo,
        "dim_ubicacion": dim_ubicacion,
        "dim_vehiculo":  dim_vehiculo,
        "dim_gravedad":  dim_gravedad,
        "dim_clima":     dim_clima,
        "fact_accidentes": fact,
    })

    # 5. LOAD → PostgreSQL
    engine = get_engine(DB)
    load_all(engine, dim_tiempo, dim_ubicacion, dim_vehiculo,
             dim_gravedad, dim_clima, fact)

    print("\n" + "█"*55)
    print("  ✅ PIPELINE COMPLETADO EXITOSAMENTE")
    print("█"*55)
    print(f"\n  Base de datos: {DB['database']} en {DB['host']}:{DB['port']}")
    print("  Tablas cargadas en esquema: dw")
    print("  → dw.dim_tiempo")
    print("  → dw.dim_ubicacion")
    print("  → dw.dim_vehiculo")
    print("  → dw.dim_gravedad")
    print("  → dw.dim_clima       ← NUEVA (API Open-Meteo)")
    print("  → dw.fact_accidentes")
    print("\n  Ahora puedes conectar Power BI a PostgreSQL 🎉\n")

if __name__ == "__main__":
    main()
