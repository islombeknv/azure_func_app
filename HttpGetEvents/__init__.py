import logging
import azure.functions as func
from azure.cosmos import CosmosClient
import os
import json

# Load Cosmos DB config from environment variables
COSMOS_DB_URL = os.getenv("COSMOS_DB_URL")
COSMOS_DB_KEY = os.getenv("COSMOS_DB_KEY")
COSMOS_DB_NAME = "EventDB"
CONTAINER_NAME = "Events"

client = CosmosClient(COSMOS_DB_URL, credential=COSMOS_DB_KEY)
database = client.get_database_client(COSMOS_DB_NAME)
container = database.get_container_client(CONTAINER_NAME)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Received request to get events.")

    try:
        query = "SELECT * FROM c"
        events = list(container.query_items(query, enable_cross_partition_query=True))

        return func.HttpResponse(
            json.dumps(events, indent=2),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Failed to get events: {e}")
        return func.HttpResponse(
            f"Error fetching events: {str(e)}",
            status_code=500
        )
