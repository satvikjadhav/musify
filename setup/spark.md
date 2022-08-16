## Setup Spark Cluster

![spark](../images/spark.JPG)

The Spark Streaming process will be done in a **DataProc** cluster that was created to communicate with the Kafka VM instance over the port `9092`. Port **9092** was also opened in the Terraform file to be able to accept connections.

- Establish SSH connection to the **master node**

  ```bash
  ssh musify-spark
  
- Clone git repo

  ```bash
  git clone https://github.com/satvikjadhav/musify.git && \
  cd musify/spark
  ```

- Set the evironment variables -

  - External IP of the Kafka VM so that spark can connect to it

  - Name of the GCS bucket. (Name given during the terraform setup)

    ```bash
    export KAFKA_ADDRESS=IP.ADD.RE.SS
    export GCP_GCS_BUCKET=bucket-name
    ```

     **Note**: Will have to setup these env vars every time you create a new shell session. Or if you stop/start your cluster. Otherwise can add this in the `.bashrc` file

- Start reading messages

  ```bash
  spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2 \
  stream_events.py
  ```

- If all went right, there will be new `parquet` files in the GCS Bucket! That is Spark writing a file every two minutes for each topic.

- Topics we are reading from

  - listen_events
  - page_view_events
  - auth_events