import dropbox
import dropbox.files

import discord
from discord.ext import commands

with open("TOKEN_DROPBOX.txt", "r") as f:
    TOKEN_DROPBOX = f.read()

with open("TOKEN_DISCORD.txt", "r") as f:
    TOKEN_DISCORD = f.read()

# Create a Dropbox object using the access token
dbx = dropbox.Dropbox(TOKEN_DROPBOX)

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix = '!', intents=intents)

# Replace with the path of the directory you want to access
DIRECTORY_PATH = '/content'

@client.event
async def on_ready():
    print("ready!")

@client.command()
async def hello(ctx):
    await ctx.send("test")

@client.command()
async def folder(ctx):
    try:
        # Get the files in the folder
        result = dbx.files_list_folder(DIRECTORY_PATH)
        files = result.entries
        
        # Print out the files
        for file in files:
            await ctx.send(f"Name: {file.name}, Type: {'Folder' if isinstance(file, dropbox.files.FolderMetadata) else 'File'}")
    
    except dropbox.exceptions.ApiError as err:
        await ctx.send(f"API error: {err}")

client.run(TOKEN_DISCORD)