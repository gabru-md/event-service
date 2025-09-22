from flask import Flask, request, jsonify
from datetime import datetime

from event import Event
from events_db import EventsDB
from log import Logger

app = Flask(__name__)
log = Logger.get_log('EventService')


@app.route('/log')
def log_event():
    json_data = request.json
    db = None
    try:
        db = EventsDB()
        if json_data:
            json_data["timestamp"] = datetime.now()
            event: Event = Event(**json_data)
            db.create(event)
    except Exception as e:
        log.exception(e)
    finally:
        if db:
            db.close()

    return jsonify({
        "status": "error",
        "message": "Nothing to log"
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
