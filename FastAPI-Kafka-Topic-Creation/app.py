import os
# env and Fast api import
from dotenv import load_dotenv
from fastapi import FastAPI
# Kafka Imports
from kafka import KafkaAdminClient
from kafka.admin import NewTopic, ConfigResource, ConfigResourceType
from kafka.errors import TopicAlreadyExistsError

load_dotenv(verbose=True)

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    # Kafka Admin Client
    client = KafkaAdminClient(
        bootstrap_servers=os.environ.get("BOOTSTRAP_SERVERS"))
    # Creating topic
    topic = NewTopic(name=os.environ.get("TOPIC_PEOPLE_BASIC_NAME"),
                     num_partitions=int(os.environ.get(
                         "TOPIC_PEOPLE_BASIC_PARTITIONS")),
                     replication_factor=int(os.environ.get("TOPIC_PEOPLE_BASIC_REPLICATION_FACTOR")))
    # If topic already exists, it will throw an error
    try:
        # Creating topic
        client.create_topics(new_topics=[topic], validate_only=False)
    except TopicAlreadyExistsError:
        pass
    # Updating Kafka Config
    cfg_resources_update = ConfigResource(
        ConfigResourceType.TOPIC,
        os.environ.get("TOPIC_PEOPLE_BASIC_NAME"),
        configs={"retention.ms": "360"})
    client.alter_configs([cfg_resources_update])
    client.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}
