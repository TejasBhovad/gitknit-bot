from typing import Final, Dict, List
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, Thread
from responses import get_response

load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")
FORUM_CHANNEL_ID: Final[str] = os.getenv("FORUM_CHANNEL_ID")

intents = Intents.default()
intents.message_content = True
intents.guilds = True

client: Client = Client(intents=intents)

# Initialize a global variable to hold guild channels
guild_channels: Dict[str, List[str]] = {}


async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print("No user message received.")
        return
    guild_name = message.guild.name
    is_private = user_message.startswith('?')
    if is_private:
        user_message = user_message.replace('?', '')

    try:
        # filter only the channels in the guild name
        sorted_guild_channels = guild_channels.get(guild_name, [])

        response: str = get_response(user_message, sorted_guild_channels)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(f"Error sending message: {e}")


async def fetch_thread_details(thread: Thread) -> None:
    print(f'Details for Thread ID: {thread.id}, Name: {thread.name}')

    # Fetch messages from the thread
    async for message in thread.history(limit=100):  # Iterate through messages directly
        print(f'Message ID: {message.id}, Author: {message.author}, Content: {message.content}')

        # Print reactions if any
        if message.reactions:
            for reaction in message.reactions:
                print(f'Reaction: {reaction.emoji}, Count: {reaction.count}')
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    global guild_channels
    for guild in client.guilds:
        channels = [channel.name for channel in guild.channels]
        guild_channels[guild.name] = channels
        print(f'Channels in {guild.name}: {channels}')
    forum_channel = client.get_channel(int(FORUM_CHANNEL_ID))
    threads = forum_channel.threads
    for thread in threads:
        print(f'Thread ID: {thread.id}, Name: {thread.name}')
        await fetch_thread_details(thread)
    print(threads)



@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author.name)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'{username} in {channel} says: {user_message}')

    await send_message(message, user_message)

@client.event
async def on_thread_create(thread: Thread) -> None:
    forum_channel = client.get_channel(int(FORUM_CHANNEL_ID))
    if thread.parent_id == forum_channel.id:
        await thread.send(f"Welcome to the new thread: **{thread.name}**! Feel free to discuss here.")

        creator = thread.owner
        if creator:
            print(f"New thread created: {thread.name} in {forum_channel.name} by {creator.name} (ID: {creator.id})")
        else:
            # If owner is NA then first msg is owner crappy but works(test for bots first tho later ofcourse)
            async for message in thread.history(limit=1, oldest_first=True):
                creator = message.author
                print(f"New thread created: {thread.name} in {forum_channel.name} by {creator.name} (ID: {creator.id})")
                break
            else:
                print(f"New thread created: {thread.name} in {forum_channel.name}, but creator information is unavailable.")
def main() -> None:
    client.run(TOKEN)


if __name__ == '__main__':
    main()