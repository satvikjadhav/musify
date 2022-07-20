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

