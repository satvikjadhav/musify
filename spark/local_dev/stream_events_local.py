from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, month, hour, dayofmonth, col, year, udf
from pyspark.conf import SparkConf
from pyspark.context import SparkContext

# decoding streaming data
@udf
def string_decode(string: str, encoding='utf-8'):
    if string:
        return (string.encode('latin1')         # To bytes, required by 'unicode-escape'
                      .decode('unicode-escape') # Perform the actual octal-escaping decode
                      .encode('latin1')         # 1:1 mapping back to bytes
                      .decode(encoding)         # Decode original encoding
                      .strip('\"')
                )
    else:
        return string


# creatring spark session
def create_or_get_spark_session(app_name: str, master: str = 'local[*]'):
    """
    Function to create spark session

    Parameters:
        app_name: Str
            The name of the respective Spark application
        master: Str
            Chosing the Spark Master type, by default it is Yarn. 
            In local development enviornment, it can be the local spark (local[*]) master for example.
        
    Returns: 
        spark: SparkSession Object
    """
    conf = SparkConf() \
            .setMaster(master) \
            .setAppName(app_name) \
            .set("spark.jars", "/home/satvikjadhav/spark/spark-3.1.3-bin-hadoop3.2/jars/gcs-connector-hadoop3-2.2.5.jar") \
            .set("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
            .set("spark.hadoop.google.cloud.auth.service.account.json.keyfile", "/home/satvikjadhav/.google/google_credentials.json")

    sc = SparkContext(conf=conf)

    sc._jsc.hadoopConfiguration().set("fs.AbstractFileSystem.gs.impl",  "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS")
    sc._jsc.hadoopConfiguration().set("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
    sc._jsc.hadoopConfiguration().set("fs.gs.auth.service.account.json.keyfile", "/home/satvikjadhav/.google/google_credentials.json")
    sc._jsc.hadoopConfiguration().set("fs.gs.auth.service.account.enable", "true")

    spark = (SparkSession.builder \
                         .config(conf=sc.getConf()) \
                         .getOrCreate())
    
    return spark


def create_kafka_read_stream(spark: SparkSession, kafka_address: str, kafka_port: int, topic: str, offset: str = 'earliest'):
    """
    Function to create a kafka read stream 

    Parameters:
        spark: SparkSession 
            Primary component of this function. A spark session object. 
        kafka_address: str
            The ip address of the virtual machine or the kafka bootstrap server
        kafka_port: int
            Port of the kafka bootstrap server
        topic: str
            Name of the kafka topic that we want to subscribe to
        starting_offset: str
            Starting offset configuration, "earliest" by default 
    Returns:
        read_stream: DataStreamReader object

    """
    read_stream = (spark.readStream \
                        .format('kafka') \
                        .option("kafka.bootstrap.servers", f"{kafka_address}:{kafka_port}") \
                        .option('subscribe', topic) \
                        .option('startingoffsets', offset) \
                        .load())
    
    return read_stream


def stream_process(stream, stream_schema, topic: str):
    """
    Fucntion to process the incoming stream data.
    Convert ts to timestamp format and produce year, month, day,
    hour columns

    Parameters:
        stream: DataStreamReader object
            The data stream reader for our stream
        stream_schema: dict
            Schema of stream data
        topic: str
            Kafka topic name
    """
    # read only value from the incoming message and convert the contents
    # inside to the passed schema
    stream = (stream.selectExpr("CAST(value AS STRING)")
                    .select(
                        from_json(col("value"), schema=stream_schema).alias("data")
                    )
                    .select("data.*")
            )

    ## adding month, day, hour columns to the stream data
    stream = (stream.withColumn("ts",  (col("ts")/1000).cast("timestamp"))
                    .withColumn("year", year(col("ts")))
                    .withColumn("month", month(col("ts")))
                    .withColumn("hour", hour(col("ts")))
                    .withColumn("day", dayofmonth(col("ts")))
              )
    
    # rectify string encoding
    if topic in ["listen_events", "page_view_events"]:
        stream = (stream.withColumn("song", string_decode("song"))
                        .withColumn("artist", string_decode('artist'))
                )

    return stream


def spark_write_stream(stream,  storage_path, checkpoint_path, trigger="120 seconds", output_mode="append", file_format="parquet"):
    """
    Write the stream back to a file store
    Parameters:
        stream : DataStreamReader
            The data stream reader for your stream
        file_format : str
            parquet, csv, orc etc
        storage_path : str
            The file output path
        checkpoint_path : str
            The checkpoint location for spark
        trigger : str
            The trigger interval
        output_mode : str
            append, complete, update
    """

    write_stream = (stream
                    .writeStream
                    .format(file_format)
                    .partitionBy('month', 'day', 'year')
                    .option("path", storage_path)
                    .option("checkpointLocation", checkpoint_path)
                    .trigger(processingTime=trigger)
                    .outputMode(output_mode)
                    )

    return write_stream
