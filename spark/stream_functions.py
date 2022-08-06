from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, month, hour, dayofmonth, col, year, udf

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
def create_or_get_spark_session(app_name: str, master: str = 'yarn'):
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

    spark = (SparkSession.builder \
                         .appName(app_name) \
                         .master(master) \
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
                        from_json(col("value"), stream_schema).alias("data")
                    )
                    .select("data.*")
            )

    ## INCOMPLETE
