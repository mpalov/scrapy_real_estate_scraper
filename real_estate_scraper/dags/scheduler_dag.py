import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

sys.path.append(os.path.abspath('/opt/airflow/app'))

from health_check_dag import run_health_checks

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 4, 12),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'scrapy_health_check_dag',
    default_args=default_args,
    description='Run health checks on all Scrapy spiders and send notifications',
    schedule_interval='@monthly',
    catchup=False,
)

health_check_task = PythonOperator(
    task_id='run_health_check',
    python_callable=run_health_checks,
    dag=dag,
)
