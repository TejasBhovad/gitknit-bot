from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
import os
from datetime import datetime

from dotenv import load_dotenv
from typing import Final

import json
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
THREADS_ID: Final[str] = os.getenv("APPWRITE_THREADS_ID")  # Corrected variable name
MESSAGES_ID: Final[str] = os.getenv("APPWRITE_MESSAGES_ID")  # Corrected variable name

# Set project and API key for the client
client.set_project(PROJECT_ID)
client.set_key(API_KEY)


TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")
FORUM_CHANNEL_ID: Final[str] = os.getenv("FORUM_CHANNEL_ID")
COMMAND_PREFIX: Final[str] = os.getenv("COMMAND_PREFIX")
APP_URL: Final[str] = os.getenv("NEXT_APP_URL")


def check_auth(channel_id: str):
    database = Databases(client)

    # List documents in the specified database and collection
    result = database.list_documents(
        database_id=DATABASE_ID,
        collection_id=REPOSITORY_ID  # Use REPOSITORY_ID constant here
    )

    print(result)  # For debugging purposes

    # Check if the channel_id exists in any of the documents and if verified is true
    for document in result['documents']:
        if document.get('channel_id') == channel_id and document.get('verified') is True:
            print(f"Channel ID {channel_id} found and verified in database.")
            return True

    print(f"Channel ID {channel_id} not found or not verified in database.")
    return False


def verify_repository(repository_id:str,channel_id:str):
    database = Databases(client)
    result = database.update_document(
        database_id=DATABASE_ID,
        collection_id=REPOSITORY_ID,
        document_id=repository_id,
        data={
            "verified": True,
            "channel_id": channel_id
        }
    )

    print(result)  # For debugging purposes

    if result['$id'] == repository_id:
        print(f"Repository ID {repository_id} verified successfully.")
        return True
    else:
        print(f"Failed to verify repository ID {repository_id}.")
        return False


async def push_threads(channel_id: str, title: str = None, tags: str = None, messages: list = None, pushed_by: str = None):
    print("Pushing threads")

    # Filter out messages by 'creator': 'GitKnit Bot#9755'
    messages = [message for message in messages if message['creator'] != 'GitKnit Bot#9755']
    # Print messages in pretty JSON
    print(json.dumps(messages, indent=4))
    # Get current time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(current_time)
    print(f"Pushed by: {pushed_by}")
    database = Databases(client)
    # From channel id get the repository id
    result = database.list_documents(
        database_id=DATABASE_ID,
        collection_id=REPOSITORY_ID
    )
    repository_id = None
    for document in result['documents']:
        if document.get('channel_id') == channel_id:
            repository_id = document['$id']

    # Push messages to the messages collection and store ids
    message_ids = []
    for message in messages:
        result = database.create_document(
            database_id=DATABASE_ID,
            collection_id=MESSAGES_ID,
            document_id=ID.unique(),
            data={
                "content": message['content'],
                "creator": message['creator'],
                "attachments": message['attachments'],
            }
        )
        message_ids.append(result['$id'])

    # Ensure title is not None
    if title is None:
        title = ""

    # Create a new document in the threads collection
    result = database.create_document(
        database_id=DATABASE_ID,
        collection_id=THREADS_ID,
        document_id=ID.unique(),
        data={
            "title": title,
            "messages": message_ids,
            "pushed_by": pushed_by,
            "pushed_at": current_time,
            "repositories": repository_id
        }
    )