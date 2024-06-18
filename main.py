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
TEST = "/content/uploads/2024-07/images"


def get_or_create_shared_link(path):
    try:
        # Try to create a shared link
        shared_link = dbx.sharing_create_shared_link_with_settings(path)
        return shared_link.url
    except dropbox.exceptions.ApiError as err:
        if isinstance(err.error, dropbox.sharing.CreateSharedLinkWithSettingsError) and err.error.is_shared_link_already_exists():
            # If the shared link already exists, retrieve the existing link
            links = dbx.sharing_list_shared_links(path=path)
            if links.links:
                return links.links[0].url
        raise err


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
        result = dbx.files_list_folder(TEST)
        files = result.entries
        
        # Print out the files
        for file in files:
            await ctx.send(f"Name: {file.name}, Type: {'Folder' if isinstance(file, dropbox.files.FolderMetadata) else 'File'}")

        test = files[0]

        shared_link_url = get_or_create_shared_link(test.path_lower)
        await ctx.send(f"{shared_link_url}")

    except dropbox.exceptions.ApiError as err:
        await ctx.send(f"API error: {err}")

client.run(TOKEN_DISCORD)