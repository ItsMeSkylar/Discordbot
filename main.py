from scripts.DropboxScripts import get_or_create_shared_link

import dropbox
import dropbox.files

import discord
from discord.ext import commands

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
    print("JenniferBot ready!")

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