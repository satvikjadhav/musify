from distutils.cmd import Command
import os
import pyarrow.csv as pv
import pyarrow.parquet as pq
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator

from google.cloud import storage
from schema import schema

default_args = {
    'owner': 'satvik'
}

AIRFLOW_HOME = os.environ.get('AIRFLOW_HOME', '/opt/airflow')

URL = 'https://github.com/satvikjadhav/musify/raw/main/dbt/seeds/songs.csv'
CSV_FILENAME = 'songs.csv'
PARQUET_FILENAME = CSV_FILENAME.replace('csv', 'parquet')

CSV_OUTFILE = f'{AIRFLOW_HOME}/{CSV_FILENAME}'
PARQUET_OUTFILE = f'{AIRFLOW_HOME}/{PARQUET_FILENAME}'
TABLE_NAME = 'songs'

GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
GCP_GCS_BUCKET = os.environ.get('GCP_GCS_BUCKET')
BIGQUERY_DATASET = os.environ.get('BIGQUERY_DATASET', 'musify_stg')


def convert_to_parquet(csv_file: str, parquet_file: str):
    if not csv_file.endswith('csv'):
        raise ValueError('Not in csv format!')

    table = pv.read_csv(csv_file)
    pq.write_table(table, parquet_file)


# NOTE: takes 20 mins, at an upload speed of 800kbps. Faster if your internet has a better upload speed
def upload_to_gcs(bucket, object_name, local_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    # storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    # storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)


with DAG(dag_id='load_songs_to_gcp',
         default_args=default_args,
         description=f'Execute only once to create songs table in bigquery',
         schedule_interval='@once',
         start_date=datetime(2022, 9, 20),
         end_date=datetime(2022, 9, 20),
         catchup=True,
         tags=['musify']
         ) as dag:

    download_songs = BashOperator(
        task_id='download_songs',
        bash_command=f'curl -sSLf {URL} > {CSV_OUTFILE}'

    )

    convert_to_parquet_file = PythonOperator(
        task_id='convert_to_parquet_file',
        python_callable=convert_to_parquet,
        op_kwargs={'csv_file': CSV_OUTFILE,
                   'parquet_file': PARQUET_OUTFILE
                   }
    )

    upload_to_gcs_task = PythonOperator(
        task_id='upload_to_gcs',
        python_callable=upload_to_gcs,
        op_kwargs={'bucket': GCP_GCS_BUCKET,
                   'object_name': f'{TABLE_NAME}/{PARQUET_FILENAME}',
                   'local_file': PARQUET_OUTFILE
                   }
    )

    remove_file_from_local = BashOperator(
        task_id='remove_file_from_local',
        bash_command=f'rm {CSV_OUTFILE} {PARQUET_OUTFILE}'
    )

    create_external_table = BigQueryCreateExternalTableOperator(
        task_id='create_external_table',
        table_resource={
            'tableReference': {
                'projectId': GCP_PROJECT_ID,
                'datasetId': BIGQUERY_DATASET,
                'tableId': TABLE_NAME,
            },
            'externalDataConfiguration': {
                'sourceFormat': 'PARQUET',
                'sourceUris': [f'gs://{GCP_GCS_BUCKET}/{TABLE_NAME}/*.parquet'],
            },
        }
    )

    download_songs >> convert_to_parquet_file >> upload_to_gcs_task >> remove_file_from_local >> create_external_table
