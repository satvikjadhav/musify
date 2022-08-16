# Local Spark Setup via Docker

 Setting up local spark development env from scratch involves multiple steps, and definitely not for a faint of heart. Thankfully using docker means you can skip a lot of steps
 We will also be setting up this useing the jupyter notebook preinstalled so that we can have a much easier time running different parts of code easily rather than running the entire script.

## Instructions

1. Make sure you have installed Docker in your local/virtual machine. 
2. Create a `docker-compose.yaml` file in a directory that you want to use as the Spark folder
```yaml
version: '3.3'

services:
  pyspark:
    container_name: pyspark
    image: jupyter/pyspark-notebook:latest
    ports:
      - "8888:8888"
    volumes:
      - ./:/home/satvikjadhav/musify/spark
```

3. Run `docker-compose` up from the same folder where the above file is located.

This snippet

```yaml
volumes:
    - ./:/home/satvikjadhav/musify/spark
```

Basically means that anything we put in the folder containing the `docker-compose.yaml` file can be accessed by the jupyter notebook running inside the Docker container, and vise versa. 

And that is it. Pretty simple, right?

Alternatively, if you would like to set up `spark` in the "raw" form on a virtual machine, you can find the setup guide [here](https://github.com/satvikjadhav/data-engineering-zoomcamp/blob/main/week_5_batch_processing/notes/installing_spark_on_linux.md), and for setting up `pyspark` you can find the setup guide [here](https://github.com/satvikjadhav/data-engineering-zoomcamp/blob/main/week_5_batch_processing/notes/setting_up_pyspark_on_linux.md)


# Connect Spark to Google Cloud Storage (DataLake)

To upload any file or folder from our Google VM to our Google Cloud Storage, we can use the following command in terminal:
```bash
gsutil cp -m -r pq/ gs://dtc_data_lake_data-engineering-339113/pq
```

Here the following flags are:
- **r**: for recursive flag. We want to upload all the files in a folder
- **m**: multi threaded. We want to upload the files in parallel so the process will be faster 

# Connect to Google Cloud Storage

1. IMPORTANT: Download the Cloud Storage connector for Hadoop here: https://cloud.google.com/dataproc/docs/concepts/connectors/cloud-storage#clusters
- As the name implies, this .jar file is what essentially connects PySpark with your GCS
- In order to download it into our own Google VM we can use the following command:
```bash
gsutil cp gs://hadoop-lib/gcs/gcs-connector-hadoop3-2.2.5.jar .
```

2. Move the .jar file to your Spark file directory.
- MacOS example: create a /jars directory under "/opt/homebrew/Cellar/apache-spark/3.2.1/ (where my spark dir is located)

3.  In our Python script, there are a few extra classes we will have to import:
```python
import pyspark
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
```

4. Set up your configurations before building your SparkSession. Here’s an example code snippet:
```python
conf = SparkConf() \
    .setMaster('local[*]') \
    .setAppName('test') \
    .set("spark.jars", "/opt/homebrew/Cellar/apache-spark/3.2.1/jars/gcs-connector-hadoop3-latest.jar") \
    .set("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
    .set("spark.hadoop.google.cloud.auth.service.account.json.keyfile", "path/to/google_credentials.json")

sc = SparkContext(conf=conf)

sc._jsc.hadoopConfiguration().set("fs.AbstractFileSystem.gs.impl",  "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS")
sc._jsc.hadoopConfiguration().set("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
sc._jsc.hadoopConfiguration().set("fs.gs.auth.service.account.json.keyfile", "path/to/google_credentials.json")
sc._jsc.hadoopConfiguration().set("fs.gs.auth.service.account.enable", "true")
```

5. Now, build `SparkSession` with the new parameters we’d just instantiated in the previous step
```python
spark = SparkSession.builder \
    .config(conf=sc.getConf()) \
    .getOrCreate()
```

6. Finally, we are able to read your files straight from GCS!
```python
df_green = spark.read.parquet("gs://{BUCKET}/green/202*/")

```