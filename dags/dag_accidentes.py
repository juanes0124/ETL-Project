"""
dag_accidentes.py — VERSION DOCKER
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
import os, sys

sys.path.insert(0, "/opt/airflow/scripts")

DB_CFG = {
    "host": "host.docker.internal",
    "port": "5432",
    "user": "postgres",
    "password": "123",
    "database": "etl_accidentes"
}
CSV_PATH = "/opt/airflow/data/accidentes_colombia.csv"
TMP = "/tmp/etl_accidentes"
os.makedirs(TMP, exist_ok=True)

def t_extract_csv(**ctx):
    import pandas as pd
    from extract import extract_data
    df = extract_data(CSV_PATH)
    out = f"{TMP}/raw.parquet"
    df.to_parquet(out, index=False)
    ctx["ti"].xcom_push(key="raw", value=out)

def t_extract_api(**ctx):
    import pandas as pd
    from extract_api import extract_weather_data
    df = pd.read_parquet(ctx["ti"].xcom_pull(key="raw", task_ids="extract_csv"))
    df_wx = extract_weather_data(df)
    out = f"{TMP}/weather.parquet"
    df_wx.to_parquet(out, index=False)
    ctx["ti"].xcom_push(key="weather", value=out)

def t_transform(**ctx):
    import pandas as pd
    from transform import run_transform
    ti = ctx["ti"]
    df    = pd.read_parquet(ti.xcom_pull(key="raw",     task_ids="extract_csv"))
    df_wx = pd.read_parquet(ti.xcom_pull(key="weather", task_ids="extract_api"))
    dims = run_transform(df, df_wx)
    nombres = ["dim_tiempo","dim_ubicacion","dim_vehiculo","dim_gravedad","dim_clima","fact_accidentes"]
    paths = {}
    for nombre, tabla in zip(nombres, dims):
        p = f"{TMP}/{nombre}.parquet"
        tabla.to_parquet(p, index=False)
        paths[nombre] = p
    ti.xcom_push(key="paths", value=paths)

def t_validate(**ctx):
    import pandas as pd
    from validate import run_validation
    paths = ctx["ti"].xcom_pull(key="paths", task_ids="transform")
    run_validation({n: pd.read_parquet(p) for n, p in paths.items()})

def t_load(**ctx):
    import pandas as pd
    from load import get_engine, load_all
    paths  = ctx["ti"].xcom_pull(key="paths", task_ids="transform")
    engine = get_engine(DB_CFG)
    load_all(engine,
        pd.read_parquet(paths["dim_tiempo"]),
        pd.read_parquet(paths["dim_ubicacion"]),
        pd.read_parquet(paths["dim_vehiculo"]),
        pd.read_parquet(paths["dim_gravedad"]),
        pd.read_parquet(paths["dim_clima"]),
        pd.read_parquet(paths["fact_accidentes"]),
    )

with DAG(
    dag_id="etl_accidentes_v2",
    description="Pipeline ETL Accidentes de Tráfico + Clima Colombia",
    schedule_interval="0 2 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args={"owner":"data-engineering","retries":1,"retry_delay":timedelta(minutes=2)},
    tags=["etl","accidentes","clima"],
) as dag:

    inicio      = EmptyOperator(task_id="inicio")
    extract_csv = PythonOperator(task_id="extract_csv", python_callable=t_extract_csv)
    extract_api = PythonOperator(task_id="extract_api", python_callable=t_extract_api)
    transform   = PythonOperator(task_id="transform",   python_callable=t_transform)
    validate    = PythonOperator(task_id="validate",    python_callable=t_validate)
    load        = PythonOperator(task_id="load",        python_callable=t_load)
    fin         = EmptyOperator(task_id="fin")

    inicio >> extract_csv >> extract_api >> transform >> validate >> load >> fin