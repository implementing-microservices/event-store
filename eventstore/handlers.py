import boto3
import logging as log

from . import db

def get_events(event_type, since, count):

  events = db.get_events(event_type, since)
  return events

def save_events(event_type, events):
  db.save_events(event_type, events)

  event_ids = [e["eventId"] for e in events]
  return event_ids