import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from decimal import Decimal

import os
import sys
import logging as log
import json


# see: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html
def get_db():
  hostname = os.environ['DYNAMO_HOST'] if "DYNAMO_HOST" in os.environ else "0.0.0.0"
  port = os.environ['DYNAMO_PORT'] if "DYNAMO_PORT" in os.environ else 8248
  region = os.environ['DYNAMO_REGION'] if "DYNAMO_REGION" in os.environ else "us-east-1"

  db_url = f"http://{hostname}:{port}"

  try:
      db_conn = boto3.resource('dynamodb', endpoint_url=db_url, region_name = region)
  except Exception as e:
      log.error("Error connecting to DynamoDB:")
      log.error(e)
      sys.exit(1)

  return db_conn

  # table = db_conn.Table('events')

def get_events(event_type, event_id, count = 10):
  conn = get_db()
  table = conn.Table('events')
  response = table.query(
    # ProjectionExpression="#yr, title, info.genres, info.actors[0]",
    IndexName="EventTypeIndex",
    KeyConditionExpression=Key('eventType').eq(event_type) & Key('eventId').gte(event_id)
  )
  return response[u'Items']

def save_events(event_type, events):
  # List comprehension that works in Python 3.5+
  dbevents = [{**e, 'eventType': event_type} for e in events]

  # Fixing Boto's silly problem with floats:
  # https://github.com/boto/boto3/issues/665#issuecomment-453198154
  dumped = json.dumps(dbevents)
  dbevents = json.loads(dumped, parse_float=Decimal)

  conn = get_db()
  table = conn.Table('events')
  with table.batch_writer() as batch:
    log.info(dbevents)
    for event in dbevents:
      batch.put_item(Item=event)


def init_db():
  conn = get_db()

  table_name  = 'events'
  table_names = [table.name for table in conn.tables.all()]

  if table_name in table_names:
      log.info(f"Table {table_name} exists!")
  else: 
      log.warning(f"Table {table_name} does not exist! Creating…")
      create_db()
  
  return

def create_db():
    conn = get_db()

    try:
        resp = conn.create_table(
            TableName="events",
            # Declare your Primary Key in the KeySchema argument
            KeySchema=[
                {
                    "AttributeName": "eventId",
                    "KeyType": "HASH"
                }
            ],
            # Any attributes used in KeySchema or Indexes must be declared in AttributeDefinitions
            AttributeDefinitions=[
                {
                    "AttributeName": "eventId",
                    "AttributeType": "S"
                },              
                {
                    "AttributeName": "eventType",
                    "AttributeType": "S"
                }
            ],
            # This is where you add, update, or delete any global secondary indexes on your table.
            GlobalSecondaryIndexes=[
                {
                    # You need to name your index and specifically refer to it when using it for queries.
                    "IndexName": "EventTypeIndex",
                    # Like the table itself, you need to specify the key schema for an index.
                    # For a global secondary index, you can use a simple or composite key schema.
                    "KeySchema": [
                        {
                            "AttributeName": "eventType",
                            "KeyType": "HASH"
                        },
                        {
                            "AttributeName": "eventId",
                            "KeyType": "RANGE"
                        }
                    ],
                    # You can choose to copy only specific attributes from the original item into the index.
                    # You might want to copy only a few attributes to save space.
                    "Projection": {
                        "ProjectionType": "ALL"
                    },
                    # Global secondary indexes have read and write capacity separate from the underlying table.
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 1,
                        "WriteCapacityUnits": 1,
                    }
                  }
            ],            
            # ProvisionedThroughput controls the amount of data you can read or write to DynamoDB per second.
            # You can control read and write capacity independently.
            ProvisionedThroughput={
                "ReadCapacityUnits": 1,
                "WriteCapacityUnits": 1
            }
        )
        log.info("Table events created successfully!")
    except Exception as e:
        log.error("Error creating table:")
        log.error(e)
