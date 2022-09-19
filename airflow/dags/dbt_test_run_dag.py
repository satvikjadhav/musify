from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner' : 'satvik'
}

with DAG(
    dag_id = 'dbt_test',
    default_args = default_args,
    description = 'Test dbt',
    schedule_interval="@once", #At the 5th minute of every hour
    start_date=datetime(2022,9,19),
    catchup=True,
    tags=['musify', 'dbt']
) as dag:

    dbt_test_task = BashOperator(
        task_id = "dbt_test",
        bash_command = "cd /dbt && dbt deps && dbt compile --profiles-dir ."
    )

    dbt_test_task