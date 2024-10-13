from typing import Final, Dict, List
import os
from dotenv import load_dotenv
import discord
from discord import Intents, Thread, Reaction
from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")
FORUM_CHANNEL_ID: Final[str] = os.getenv("FORUM_CHANNEL_ID")
COMMAND_PREFIX: Final[str] = os.getenv("COMMAND_PREFIX")

intents = Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True

client = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Initialize global variables
guild_channels: Dict[str, List[str]] = {}
thread_creators: Dict[int, int] = {}


async def get_thread_creator(thread: Thread) -> int:
    if thread.id in thread_creators:
        return thread_creators[thread.id]

    async for message in thread.history(limit=1, oldest_first=True):
        creator = message.author  # This should be a User object
        thread_creators[thread.id] = creator.id
        return creator.id  # Return the creator's ID

    return None  # Return None if no creator found


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    global guild_channels
    for guild in client.guilds:
        channels = [channel.name for channel in guild.channels]
        guild_channels[guild.name] = channels
        print(f'Channels in {guild.name}: {channels}')

    # Sync the command tree to register slash commands
    await client.tree.sync()

@client.tree.command(name="push", description="Send a push notification with an optional title and tags.")
@app_commands.describe(message="The message to send", title="Optional title for the push", tags="Optional tags for the push")
async def push(interaction: discord.Interaction, message: str, title: str = None, tags: str = None):
    # Construct the response message
    response_message = f"**Message:** {message}"
    if title:
        response_message += f"\n**Title:** {title}"
    if tags:
        response_message += f"\n**Tags:** {tags}"

    # Send the response
    await interaction.response.send_message(response_message)

@client.tree.command(name="close", description="Close the current thread.")
async def close_thread(interaction: discord.Interaction):
    if not isinstance(interaction.channel, Thread):
        await interaction.response.send_message("This command can only be used in a thread.", ephemeral=True)
        return

    thread = interaction.channel
    creator_id = await get_thread_creator(thread)

    # Check if the user is either the creator or has Manage Threads permission
    if interaction.user.id != creator_id and not interaction.user.guild_permissions.manage_threads:
        await interaction.response.send_message("You do not have permission to close this thread.", ephemeral=True)
        return

    try:
        # Check if the thread is already locked or archived
        if thread.locked or thread.archived:
            await interaction.response.send_message("This thread is already closed or archived.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        await thread.send("Closing this thread...")

        # Create a button to link to Google
        button = Button(label="Go to Google", url="https://www.google.com")
        view = View()
        view.add_item(button)

        # Attempt to close the thread
        await thread.edit(locked=True, archived=True)

        # Send a message with the button
        await interaction.followup.send(
            "Thread has been closed and archived. You can visit Google using the button below:",
            view=view,
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.followup.send("I don't have permission to close this thread.", ephemeral=True)
    except Exception as e:
        print(f"Error closing thread: {e}")
        await interaction.followup.send("An error occurred while trying to close the thread.", ephemeral=True)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    username: str = str(message.author.name)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'{username} in {channel} says: {user_message}')


@client.event
async def on_thread_create(thread: Thread) -> None:
    forum_channel = client.get_channel(int(FORUM_CHANNEL_ID))

    if thread.parent_id == forum_channel.id:
        try:
            await thread.send(f"Welcome to the new thread: **{thread.name}**! Feel free to discuss here.")
            creator_id = await get_thread_creator(thread)

            if creator_id:
                print(f"New thread created: {thread.name} in {forum_channel.name} by user ID {creator_id}")
                thread_creators[thread.id] = creator_id
            else:
                print("Creator not found for this thread.")

        except Exception as e:
            print(f"Error sending welcome message or fetching creator: {e}")


@client.event
async def on_reaction_add(reaction: Reaction, user) -> None:
    print(f"{user.name} reacted with {reaction.emoji} on message ID {reaction.message.id}")

    if user == client.user:
        return

    if isinstance(reaction.message.channel, Thread):
        thread = reaction.message.channel

        creator_id = await get_thread_creator(thread)

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

                    await thread.edit(archived=True)
                    print(f"Thread {thread.name} (ID: {thread.id}) has been archived.")
                except Exception as e:
                    print(f"Error closing or archiving thread: {e}")


def main() -> None:
    client.run(TOKEN)


if __name__ == '__main__':
    main()