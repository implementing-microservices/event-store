import boto3
import logging as log

from . import db

async def get_events(event_type, since, count):

  events = await db.get_events(event_type, since)
  return events

async def save_events(event_type, events):
  await db.save_events(event_type, events)

  event_ids = [e["eventId"] for e in events]
  return event_ids