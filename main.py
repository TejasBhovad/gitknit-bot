from typing import Final, Dict, List
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, Thread, Reaction
from responses import get_response

load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")
FORUM_CHANNEL_ID: Final[str] = os.getenv("FORUM_CHANNEL_ID")

intents = Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True

client: Client = Client(intents=intents)

# Initialize global variables
guild_channels: Dict[str, List[str]] = {}
thread_creators: Dict[int, int] = {}


async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print("No user message received.")
        return
    guild_name = message.guild.name
    is_private = user_message.startswith('?')
    if is_private:
        user_message = user_message.replace('?', '')

    try:
        sorted_guild_channels = guild_channels.get(guild_name, [])
        response: str = get_response(user_message, sorted_guild_channels)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(f"Error sending message: {e}")


async def fetch_thread_details(thread: Thread) -> None:
    print(f'Details for Thread ID: {thread.id}, Name: {thread.name}')
    async for message in thread.history(limit=100):
        if message.reactions:
            for reaction in message.reactions:
                print(f'Reaction: {reaction.emoji}, Count: {reaction.count}')


async def get_thread_creator(thread: Thread) -> int:
    if thread.id in thread_creators:
        return thread_creators[thread.id]

    async for message in thread.history(limit=1, oldest_first=True):
        creator = message.author  # This should be a User object
        thread_creators[thread.id] = creator.id
        return creator

    return None


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    global guild_channels
    for guild in client.guilds:
        channels = [channel.name for channel in guild.channels]
        guild_channels[guild.name] = channels
        print(f'Channels in {guild.name}: {channels}')

    forum_channel = client.get_channel(int(FORUM_CHANNEL_ID))

    # Fetch all threads in the forum channel correctly
    threads = forum_channel.threads  # Accessing the property directly

    for thread in threads:
        print(f'Thread ID: {thread.id}, Name: {thread.name}')
        await fetch_thread_details(thread)

        # Fetch and store the creator for existing threads
        creator = await get_thread_creator(thread)
        if creator:
            thread_creators[thread.id] = creator.id


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
        try:
            await thread.send(f"Welcome to the new thread: **{thread.name}**! Feel free to discuss here.")
            creator = thread.owner or (await get_thread_creator(thread))

            if creator:
                print(f"New thread created: {thread.name} in {forum_channel.name} by {creator.name} (ID: {creator.id})")
                thread_creators[thread.id] = creator.id
            else:
                print("Creator not found for this thread.")

        except Exception as e:
            print(f"Error sending welcome message or fetching creator: {e}")


@client.event
async def on_reaction_add(reaction: Reaction, user) -> None:
    print(f"{user.name} reacted with {reaction.emoji} on message ID {reaction.message.id}")

    if user == client.user:
        return

    # Check if the reaction was added to a message in a thread.
    if isinstance(reaction.message.channel, Thread):
        # Get the thread (channel) where the reaction occurred.
        thread = reaction.message.channel

        # Fetch the thread creator if not already in our map.
        creator_id = await get_thread_creator(thread)

        # Check if the reacting user is the creator of the thread.
        if creator_id and user.id == creator_id:
            specific_emoji = "👍"
            if str(reaction.emoji) == specific_emoji:
                print("Creator reacted with the specific emoji!")
                await thread.send(f"{user.name} reacted with {specific_emoji}!")


                try:

                    if not thread.locked:
                        await thread.edit(locked=True)
                        await thread.send("This thread has been closed.")
                    else:
                        print("Thread was already locked.")

                    # Archive the thread
                    await thread.edit(archived=True)
                    print(f"Thread {thread.name} (ID: {thread.id}) has been archived.")
                except Exception as e:
                    print(f"Error closing or archiving thread: {e}")

def main() -> None:
    client.run(TOKEN)


if __name__ == '__main__':
    main()