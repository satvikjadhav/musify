from spark import schema
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, month, hour, dayofmonth, col, year, udf

# spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.3 stream_test.py
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
# since we are running locally, we will use the "local" spark master
# in production mode, the master would be a proper cluster manager like "YARN"
spark = SparkSession.builder \
                    .master("local[*]") \
                    .appName('spark_streaming') \
                    .getOrCreate()

# Read kafka streams
# kafka server format: VM_IP_ADDRESS:KAFKA_BROKER_PORT
rs = spark.readStream \
          .format("kafka") \
          .option("kafka.bootstrap.servers", "34.69.20.14:9092") \
          .option("subscribe", "page_view_events") \
          .option("startingOffsets", "earliest") \
          .load()

rs = rs \
    .selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema=schema['page_view_events'])).alias("data") \
    .select("data.*")

# Process stream by adding month, day, hour columns to the stream data
ps = (rs.withColumn("ts",  (col("ts")/1000).cast("timestamp"))
        .withColumn("year", year(col("ts")))
        .withColumn("month", month(col("ts")))
        .withColumn("hour", hour(col("ts")))
        .withColumn("day", dayofmonth(col("ts")))
        .withColumn("song", string_decode("song"))
        .withColumn("artist", string_decode('artist'))
)

# Write stream content locally
# but if we want to store it in our google cloud storage, we simply have to 
# add the storage uri
ws = ps.writeStream.trigger(processingTime="120 seconds") \
                   .format("csv") \
                   .outputMode("append") \
                   .option("path", '/home/satvikjadhav/notebook') \
                   .option("checkpointLocation", '/home/satvikjadhav/notebook/spark_checkpoint') \
                   .option("header", True) # csv output by default has header = false

ws.start()
spark.streams.awaitAnyTermination()