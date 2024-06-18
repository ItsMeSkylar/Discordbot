from scripts.DropboxScripts import get_or_create_shared_link

import dropbox
import dropbox.files

import json

import discord
from discord.ext import commands
from discord import app_commands

with open('config.json') as config_file:
    config = json.load(config_file)

with open("tokens/TOKEN_DROPBOX.txt", "r") as f:
    TOKEN_DROPBOX = f.read()

with open("tokens/TOKEN_DISCORD.txt", "r") as f:
    TOKEN_DISCORD = f.read()

# Create a Dropbox object using the access token
dbx = dropbox.Dropbox(TOKEN_DROPBOX)

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix = '!', intents=intents)

# Replace with the path of the directory you want to access
DIRECTORY_PATH = '/content'
TEST = "/content/uploads/2024-07/images"

@client.event
async def on_ready():
    try:
        await client.tree.sync()
        print("Command tree synced successfully.")
        print("JenniferBot ready!")
    except Exception as err:
        print(f"Failed to sync command tree: {err}")

@client.tree.command(name="jen", description="test description")
@app_commands.choices(choice=[
    app_commands.Choice(name="Option 1", value="option_1"),
    app_commands.Choice(name="Option 2", value="option_2"),
    app_commands.Choice(name="Option 3", value="option_3"),
])
async def ping(interaction: discord.Interaction, choice: app_commands.Choice[str]):
    await interaction.response.send_message(f"selected: {choice.name}, value: {choice.value}")

@client.tree.command(name="set_channel")
async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    # Update the configuration with the new channel ID
    config['channel'] = channel.id
    await interaction.response.send_message(f'Config variable "channel" set to {channel.id}')

@client.command()
async def folder(ctx):
    try:
        # Get the files in the folder
        result = dbx.files_list_folder(TEST)
        files = result.entries
        
        # Print out the files
        #for file in files:
            #await ctx.send(f"Name: {file.name}, Type: {'Folder' if isinstance(file, dropbox.files.FolderMetadata) else 'File'}")

        test = files[0]

        shared_link_url = get_or_create_shared_link(test.path_lower)
        await ctx.send(f"{shared_link_url}")
        print(f"posted {test.name} with the following link: {shared_link_url}")

    except Exception as err:
        await ctx.send(f"API error: {err}")

client.run(TOKEN_DISCORD)