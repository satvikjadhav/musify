import os
from stream_functions import *
from schema import schema

# Kafka topics
LISTEN_EVENTS_TOPIC = 'listen_events'
PAGE_VIEW_TOPIC = 'page_view_events'
AUTH_EVENTS_TOPIC = 'auth_events'

KAFKA_PORT = '9092'

KAFKA_ADDRESS = os.getenv('KAFKA_ADDRESS', 'localhost')
GCP_GCS_BUCKET = os.getenv('GCP_GCS_BUCKET', 'musify')
GCS_STORAGE_PATH = f'gs://{GCP_GCS_BUCKET}'

# Inatialize spark session
spark = create_or_get_spark_session('Eventsim Stream')
spark.streams.resetTerminated()

# Listen Events Topic Stream
listen_events = create_kafka_read_stream(spark, KAFKA_ADDRESS, KAFKA_PORT, LISTEN_EVENTS_TOPIC)
listen_events = stream_process(listen_events, schema[LISTEN_EVENTS_TOPIC], LISTEN_EVENTS_TOPIC)

# Page View Events Topic Stream
page_view_events = create_kafka_read_stream(spark, KAFKA_ADDRESS, KAFKA_PORT, PAGE_VIEW_TOPIC)
page_view_events = stream_process(page_view_events, schema[PAGE_VIEW_TOPIC], PAGE_VIEW_TOPIC)

# Auth Events Topic Stream
auth_events = create_kafka_read_stream(spark, KAFKA_ADDRESS, KAFKA_PORT, AUTH_EVENTS_TOPIC)
auth_events = stream_process(auth_events, schema[AUTH_EVENTS_TOPIC], AUTH_EVENTS_TOPIC)

# Write stream to an output location (local or cloud) every 2 mins in parquet format
write_listen_events = spark_write_stream(listen_events, f'{GCS_STORAGE_PATH}/{LISTEN_EVENTS_TOPIC}', f'{GCS_STORAGE_PATH}/checkpoint/{LISTEN_EVENTS_TOPIC}')

write_page_view_events = spark_write_stream(page_view_events, f'{GCS_STORAGE_PATH}/{PAGE_VIEW_TOPIC}', f'{GCS_STORAGE_PATH}/checkpoint/{PAGE_VIEW_TOPIC}')

write_auth_events = spark_write_stream(auth_events, f'{GCS_STORAGE_PATH}/{AUTH_EVENTS_TOPIC}', f'{GCS_STORAGE_PATH}/checkpoint/{AUTH_EVENTS_TOPIC}')

#Start the stream writing processes
write_listen_events.start()
write_page_view_events.start()
write_auth_events.start()

spark.streams.awaitAnyTermination()
