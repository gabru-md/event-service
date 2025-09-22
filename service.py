from crypt import methods

from flask import Flask, request, jsonify, render_template
from datetime import datetime

from event import Event
from events_db import EventsDB
from log import Logger

app = Flask(__name__)
log = Logger.get_log('EventService')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/events')
def get_events():
    db = None
    try:
        db = EventsDB()
        events = db.get_recent_events()
        # Convert events to a list of dictionaries for JSON serialization
        event_dicts = [event.model_dump() for event in events]
        return jsonify(event_dicts), 200
    except Exception as e:
        log.exception(e)
        return jsonify({"status": "error", "message": "Failed to retrieve events"}), 500
    finally:
        if db:
            db.close()


@app.route('/log', methods=['POST'])
def log_event():
    json_data = request.json
    db = None
    try:
        db = EventsDB()
        if json_data:
            current_timestamp = datetime.now()
            tags = json_data['tags']
            if tags:
                json_data["tags"] = [t.strip() for t in tags.split(',')]
            else:
                json_data["tags"] = []
            json_data["timestamp"] = int(current_timestamp.timestamp())
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
