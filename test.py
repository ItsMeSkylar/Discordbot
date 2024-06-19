import dropbox, discord, requests, os
import dropbox.files
from discord.ext import commands

## SCRIPTS ########################################################################
import setCreds

######################################################################## SCRIPTS ##
# with open("TOKEN_DROPBOX.txt", "r") as f:
# TOKEN_DROPBOX = f.read()
# with open("TOKEN_DISCORD.txt", "r") as f:
# TOKEN_DISCORD = f.read()

## GLOBALS ########################################################################
#setCreds
# DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
DROPBOX_APP_KEY = os.environ["DROPBOX_APP_KEY"]
DROPBOX_APP_SECRET = os.environ["DROPBOX_APP_SECRET"]


######################################################################## GLOBALS ##





# attempt to fetch the DROPBOX BEARER token from the shell environment variables.
try:
    DROPBOX_BEARER = os.environ["DROPBOX_BEARER"]

# NO BEARER TOKEN FOUND. Run the OAuth flow to go get one.
except KeyError:
    setCreds.authorizeDropbox()

    # fetch the newly created token from the system environment..
    DROPBOX_BEARER = os.environ["DROPBOX_BEARER"]


# Create a Dropbox object using the access token
dbx = dropbox.Dropbox(DROPBOX_BEARER)

print(dbx.users_get_current_account())


# Function to list files in a directory
def list_files(folder_path):
    try:
        # Get the files in the folder
        result = dbx.files_list_folder(folder_path)
        files = result.entries

        # Print out the files
        for file in files:
            print(f"Name: {file.name}, Type: {'Folder' if isinstance(file, dropbox.files.FolderMetadata) else 'File'}")

    except dropbox.exceptions.ApiError as err:
        print(f"API error: {err}")


# Replace with the path of the directory you want to access
DIRECTORY_PATH = ''

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)


@client.event
async def on_ready():
    print("ready!")
    print("---------------------")


# !hello in discord
@client.command()
async def hello(ctx):
    await ctx.send("test")


# client.run(TOKEN_DISCORD)


list_files(DIRECTORY_PATH)

