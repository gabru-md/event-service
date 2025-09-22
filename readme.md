# Event Log Service

This is a simple, self-hosted service for logging events. It's designed to be a lightweight backend for a personal "Life
OS" or habit-tracking system, built with Flask and PostgreSQL.

## Features

* **RESTful API:** Provides a single endpoint for logging events via `POST` requests.
* **Database Persistence:** Events are stored in a PostgreSQL database, ensuring data is not lost.
* **Structured Logging:** Uses a custom logger for clean and organized console output.
* **Simple Data Model:** Events are defined with a clear Pydantic model for data validation.

---

## Prerequisites

Before running the service, you'll need to have the following installed:

* **Python 3.8+**
* **Docker** (Recommended for running PostgreSQL in a container)

---

## Setup and Installation

1. **Clone the repository:**
   ```
   git clone [https://github.com/your-username/event-log-service.git](https://github.com/your-username/event-log-service.git)
   cd event-log-service
   ```
2. **Create a virtual environment and install dependencies:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install Flask psycopg2-binary pydantic
   ```
3. **Start the PostgreSQL database with Docker:**
   Create a `docker-compose.yml` file with the following content:
   ```
   version: '3.8'
   services:
     db:
       image: postgres:14-alpine
       restart: always
       environment:
         POSTGRES_USER: manish
         POSTGRES_PASSWORD: password
         POSTGRES_DB: events
       ports:
         - "5432:5432"
       volumes:
         - postgres_data:/var/lib/postgresql/data
   volumes:
     postgres_data:
   ```
   Now, run the container in the background:
   ```
   docker-compose up -d
   ```
4. **Set environment variables:**
   The `events_db.py` file reads database credentials from environment variables. Set them in your shell or a `.env`
   file before running the application.
   ```
   export POSTGRES_USER=manish
   export POSTGRES_PASSWORD=password
   export POSTGRES_DB=events
   export POSTGRES_HOST=localhost
   export POSTGRES_PORT=5432
   ```

---

## Running the Service

Once everything is set up, you can run the Flask application:

```
python service.py

```

The service will start on `http://localhost:5005`.

---

## API Reference

### Log an Event

Logs a new event with a JSON payload.

* **URL:** `/log`
* **Method:** `POST`
* **Content-Type:** `application/json`

#### Example Request

```

{
"event\_type": "finished\_dishes",
"description": "Cleaned all the dishes after dinner.",
"tags": ["chores", "kitchen"]
}

```

The `timestamp` field is automatically added by the service.

#### Example Response

A successful response will return a 200 OK status.

```

{
"status": "success",
"message": "Event logged successfully"
}

```

---

## Data Model

The `Event` data model is defined in `event.py` using Pydantic.

| **Field**     | **Type**    | **Description**                     | **Required** |
|:--------------|:------------|:------------------------------------|:-------------|
| `id`          | `int`       | Unique event ID (auto-generated)    | No           |
| `event_type`  | `str`       | The name of the event               | Yes          |
| `timestamp`   | `int`       | Unix timestamp of the event         | Yes          |
| `description` | `str`       | A detailed description of the event | No           |
| `tags`        | `List[str]` | A list of tags for categorization   | No           |

```