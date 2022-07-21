import pyspark
from pyspark.sql import SparkSession

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

rs = rs.selectExpr( "CAST(value AS STRING)")

# Write stream content locally
# but if we want to store it in our google cloud storage, we simply have to 
# add the storage uri
ws = rs.writeStream.trigger(processingTime="120 seconds") \
                   .format("csv") \
                   .outputMode("append") \
                   .option("path", '/home/satvikjadhav/notebook') \
                   .option("checkpointLocation", '/home/satvikjadhav/notebook/spark_checkpoint')

ws.start()
spark.streams.awaitAnyTermination()