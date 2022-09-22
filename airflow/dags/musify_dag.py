import os
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

from schema import schema
from task_functions_template import (create_external_table,
                                     create_empty_table,
                                     insert_job,
                                     delete_external_table)

# we have data coming in from three events
EVENTS = ['listen_events', 'page_view_events', 'auth_events']

GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
GCP_GCS_BUCKET = os.environ.get('GCP_GCS_BUCKET')
BIGQUERY_DATASET = os.environ.get('BIGQUERY_DATASET', 'musify_stg')


EXECUTION_MONTH = '{{ logical_date.strftime("%-m") }}'
EXECUTION_DAY = '{{ logical_date.strftime("%-d") }}'
EXECUTION_HOUR = '{{ logical_date.strftime("%-H") }}'
EXECUTION_DATETIME_STR = '{{ logical_date.strftime("%m%d%H") }}'

TABLE_MAP = { f"{event.upper()}_TABLE" : event for event in EVENTS}

MACRO_VARS = {"GCP_PROJECT_ID":GCP_PROJECT_ID, 
              "BIGQUERY_DATASET": BIGQUERY_DATASET, 
              "EXECUTION_DATETIME_STR": EXECUTION_DATETIME_STR
              }

MACRO_VARS.update(TABLE_MAP)

default_args = {
    'owner' : 'satvik'
}
