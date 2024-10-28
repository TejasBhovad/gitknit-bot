from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
import os
from dotenv import load_dotenv
from typing import Final

# Load environment variables from .env file
load_dotenv()

# Initialize the Appwrite client
client = Client()
client.set_endpoint('https://cloud.appwrite.io/v1')

# Define constants for project and database IDs
PROJECT_ID: Final[str] = os.getenv("APPWRITE_PROJECT_ID")
API_KEY: Final[str] = os.getenv("APPWRITE_PROJECT_KEY")
DATABASE_ID: Final[str] = os.getenv("APPWRITE_DATABASE_ID")
REPOSITORY_ID: Final[str] = os.getenv("APPWRITE_REPOSITORY_ID")  # Corrected variable name

# Set project and API key for the client
client.set_project(PROJECT_ID)
client.set_key(API_KEY)


def check_auth(channel_id: str):
    database = Databases(client)

    # List documents in the specified database and collection
    result = database.list_documents(
        database_id=DATABASE_ID,
        collection_id=REPOSITORY_ID  # Use REPOSITORY_ID constant here
    )

    print(result)  # For debugging purposes

    # Check if the channel_id exists in any of the documents
    for document in result['documents']:
        if document.get('channel_id') == channel_id:
            print(f"Channel ID {channel_id} found in database.")
            return True

    print(f"Channel ID {channel_id} not found in database.")
    return False