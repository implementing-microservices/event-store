import os
import logging as log
import uuid
import json
import decimal

from quart import Quart, request, jsonify, Response

app = Quart(__name__)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

app.json_encoder = DecimalEncoder

from eventstore import handlers, db

# @see: https://implementing-microservices.github.io/event-store/
@app.route('/events/<event_type>', methods=['POST'])
async def save_events(event_type):
    events = await request.get_json(force=True)
    resp = await handlers.save_events(event_type, events)
    return jsonify(resp)

@app.route('/events/<event_type>', methods=['GET'])
async def get_events(event_type):
    since = request.args.get('since', '')
    count = request.args.get('count', 10)

    resp = await handlers.get_events(event_type, since, count)
    return jsonify(resp)
   

def init():
    uuid.uuid1() # prime the uuid generator at startup
    db.init_db()


if __name__ == "__main__":
    init()
    app.run(host="0.0.0.0", port=5000)