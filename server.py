import boto3
import os
import logging as log
import uuid
import json
import decimal
from decimal import Decimal

from sanic import Sanic
from sanic import response
from sanic.request import RequestParameters

app = Sanic()

from eventstore import handlers, db

# @see: https://implementing-microservices.github.io/event-store/
@app.route('/events/<event_type>', methods=['POST'])
async def save_events(request, event_type):
    events = request.json

    resp = await handlers.save_events(event_type, events)
    return response.json(resp)

@app.route('/events/<event_type>', methods=['GET'])
async def get_events(request, event_type):
    since = request.args.get('since', '')
    count = request.args.get('count', 10)

    resp = await handlers.get_events(event_type, since, count)
    return response.json(resp)
    # return resp

def init():
    uuid.uuid1() # prime the uuid generator at startup
    db.init_db()


if __name__ == "__main__":
    init()
    app.run(host="0.0.0.0", port=5000)