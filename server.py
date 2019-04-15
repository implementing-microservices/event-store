import boto3
import os
import logging as log
import uuid
import json
import decimal

from flask import Flask, request, jsonify, Response
from decimal import Decimal

from eventstore import handlers, db

app = Flask(__name__)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

# @see: https://implementing-microservices.github.io/event-store/
@app.route('/events/<event_type>', methods=['POST'])
def save_events(event_type):
    # Note 'force=True' ignores mime-type=app/json requirement default in Flask
    events = request.get_json(force=True)

    resp = handlers.save_events(event_type, events)
    return jsonify(resp)

@app.route('/events/<event_type>', methods=['GET'])
def get_events(event_type):
    since = request.args.get('since', '')
    count = request.args.get('count', 10)

    resp = handlers.get_events(event_type, since, count)
    resp = json.dumps(resp, cls=DecimalEncoder)
    return Response(resp, mimetype='application/json')
    # return resp

def init():
    uuid.uuid1() # prime the uuid generator at startup
    db.init_db()


if __name__ == '__main__':
    init()
    app.run(debug=True, host='0.0.0.0')