import logging
import azure.functions as func
import json
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from datetime import datetime
import os

# Initialize Cosmos client and set the connection string
COSMOS_DB_URL = os.getenv("COSMOS_DB_URL")  # Set this in your Azure Function App Settings
COSMOS_DB_KEY = os.getenv("COSMOS_DB_KEY")  # Set this in your Azure Function App Settings
COSMOS_DB_NAME = "EventDB"  # Your Cosmos DB database name
CONTAINER_NAME = "Events"  # Your Cosmos DB container name

# Initialize Cosmos DB Client
client = CosmosClient(COSMOS_DB_URL, credential=COSMOS_DB_KEY)
database = client.get_database_client(COSMOS_DB_NAME)
container = database.get_container_client(CONTAINER_NAME)

# The Event class to define the event structure
class Event:
    def __init__(self, event_id, name, description, created_at):
        self.event_id = event_id
        self.name = name
        self.description = description
        self.created_at = created_at

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat()
        }

def save_event_to_cosmos(event: Event):
    try:
        container.upsert_item(event.to_dict())
        logging.info(f"Event {event.event_id} saved to Cosmos DB.")
    except exceptions.CosmosResourceExistsError as e:
        logging.error(f"Error saving event to Cosmos DB: {e}")
        raise

# The function for handling HTTP requests to create events
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing a request to create event.')

    # Parse the incoming JSON body
    try:
        req_body = req.get_json()
        name = req_body.get('name')
        description = req_body.get('description')
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON body. Please provide valid event data.",
            status_code=400
        )

    # Validate input
    if not name or not description:
        return func.HttpResponse(
            "Missing required event details (name and description).",
            status_code=400
        )

    # Create a new event instance
    event_id = str(datetime.utcnow().timestamp())  # Generate a simple event ID based on timestamp
    created_at = datetime.utcnow()

    event = Event(event_id, name, description, created_at)

    # Save the event to Cosmos DB
    try:
        save_event_to_cosmos(event)
        return func.HttpResponse(
            json.dumps({"message": "Event created successfully!", "event_id": event.event_id}),
            mimetype="application/json",
            status_code=201
        )
    except Exception as e:
        return func.HttpResponse(
            f"Error saving event to Cosmos DB: {str(e)}",
            status_code=500
        )
