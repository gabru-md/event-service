import psycopg2
from typing import Optional, List
from event import Event
import os
from dotenv import load_dotenv
from log import Logger

load_dotenv()


class EventsDB:
    def __init__(self):

        self.dbname = os.environ.get("EVENTS_POSTGRES_DB", "events")
        self.user = os.environ.get("EVENTS_POSTGRES_USER", "manish")
        self.password = os.environ.get("EVENTS_POSTGRES_PASSWORD", "password")
        self.host = os.environ.get("EVENTS_POSTGRES_HOST", "localhost")
        self.port = os.environ.get("EVENTS_POSTGRES_PORT", "5432")

        self.log = Logger.get_log(self.__class__.__name__)

        self.conn = None
        self._connect()
        self._create_table()

    def _connect(self):
        """Establishes a connection to the PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.log.info("Connected to PostgreSQL database.")
        except psycopg2.Error as e:
            self.log.error(f"Error connecting to the database: {e}")
            self.conn = None

    def _create_table(self):
        """Creates the events table if it doesn't exist."""
        if self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id SERIAL PRIMARY KEY,
                        event_type VARCHAR(255) NOT NULL,
                        timestamp BIGINT NOT NULL,
                        description TEXT,
                        tags TEXT[]
                    )
                """)
                self.conn.commit()

    def create(self, event: Event) -> Optional[int]:
        """Creates a new event and returns its ID."""
        if not self.conn:
            return None
        with self.conn.cursor() as cursor:
            # PostgreSQL uses arrays for lists, and we need to cast them
            cursor.execute(
                "INSERT INTO events (event_type, timestamp, description, tags) VALUES (%s, %s, %s, %s) RETURNING id",
                (event.event_type, event.timestamp, event.description, event.tags)
            )
            self.conn.commit()
            return cursor.fetchone()[0]

    def get_by_id(self, event_id: int) -> Optional[Event]:
        """Retrieves an event by its ID."""
        if not self.conn:
            return None
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT id, event_type, timestamp, description, tags FROM events WHERE id = %s", (event_id,))
            row = cursor.fetchone()
            if row:
                event_dict = {
                    "id": row[0],
                    "event_type": row[1],
                    "timestamp": row[2],
                    "description": row[3],
                    "tags": row[4] if row[4] else []
                }
                return Event(**event_dict)
        return None

    def get_all(self) -> List[Event]:
        """Retrieves all events from the database."""
        if not self.conn:
            return []
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT id, event_type, timestamp, description, tags FROM events")
            rows = cursor.fetchall()
            events = []
            for row in rows:
                event_dict = {
                    "id": row[0],
                    "event_type": row[1],
                    "timestamp": row[2],
                    "description": row[3],
                    "tags": row[4] if row[4] else []
                }
                events.append(Event(**event_dict))
            return events

    def update(self, event: Event) -> bool:
        """Updates an existing event. Returns True on success, False otherwise."""
        if not self.conn or event.id is None:
            return False
        with self.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE events SET event_type=%s, timestamp=%s, description=%s, tags=%s WHERE id=%s",
                (event.event_type, event.timestamp, event.description, event.tags, event.id)
            )
            self.conn.commit()
            return cursor.rowcount > 0

    def delete(self, event_id: int) -> bool:
        """Deletes an event by its ID. Returns True on success, False otherwise."""
        if not self.conn:
            return False
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM events WHERE id=%s", (event_id,))
            self.conn.commit()
            return cursor.rowcount > 0

    def get_recent_events(self, limit: int = 20) -> List[Event]:
        """Retrieves the most recent events from the database."""
        if not self.conn:
            return []
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, event_type, timestamp, description, tags FROM events ORDER BY timestamp DESC LIMIT %s",
                (limit,)
            )
            rows = cursor.fetchall()
            events = []
            for row in rows:
                event_dict = {
                    "id": row[0],
                    "event_type": row[1],
                    "timestamp": row[2],
                    "description": row[3],
                    "tags": row[4] if row[4] else []
                }
                events.append(Event(**event_dict))
            return events

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
