from scripts.DropboxScripts import get_or_create_shared_link

from scripts.DropboxScripts import rename_dropbox_files


from scripts.JsonScripts import generate_json_file
from scripts.JsonScripts import validate_json_file
from scripts.JsonScripts import rename_json_files

import dropbox.files, os, json, discord
from discord.ext import commands
from discord import app_commands
import re

with open('config.json') as config_file:
    config = json.load(config_file)

#with open("tokens/TOKEN_DROPBOX.txt", "r") as f:
#    TOKEN_DROPBOX = f.read()
TOKEN_DROPBOX = os.environ["DROPBOX_BEARER"]

with open("tokens/TOKEN_DISCORD.txt", "r") as f:
    TOKEN_DISCORD = f.read()

# Create a Dropbox object using the access token
dbx = dropbox.Dropbox(TOKEN_DROPBOX)

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix = '!', intents=intents)

APP_ABSOLUTE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# ex 2024-08
async def date_validation(year, month):
    if not year.isdigit() or not month.isdigit():
        raise Exception(f"ERROR: Year and month must be numeric.")
        
    year_num = int(year)
    month_num = int(month)
    
    if year_num < 100:
        year_num += 2000
        
    if year_num < 1000 or year_num > 9999:
        raise Exception(f"ERROR: Invalid year. Please provide a 4-digit year.")
    
    if month_num < 1 or month_num > 12:
        raise Exception(f"ERROR: Invalid month. Please provide a month between 1 and 12.")
        
    month_str = f"{month_num:02d}"
    
    return f"{year_num}-{month_str}"

@client.event
async def on_ready():
    try:
        await client.tree.sync()
        print("Command tree synced successfully.")
        print("JenniferBot ready!")
    except Exception as err:
        print(f"Failed to sync command tree: {err}")

# simply generates a folder, you lazy bum
@client.tree.command(name="generate_folder", description="generates folder for content")
async def generate_folders(interaction: discord.Interaction, year: str, month: str):
    try:
        date = await date_validation(year, month)
        absolute_path = os.path.join(APP_ABSOLUTE_PATH, f"content\\uploads\\{date}")
        
        if not os.path.exists(absolute_path):
            os.makedirs(absolute_path)
            await interaction.response.send_message(f"Successfully generated folder: {date} at {absolute_path}\nPlease add your content to the folder and then run validate")
        else:
            raise Exception(f"Folder '{date}' already exists at '{absolute_path}'")
            
    except Exception as err:
        await interaction.response.send_message(f"ERROR: {err}")

# generates json based of content in given folder
@client.tree.command(name="generate_json", description="generates json file based of content in folder")
async def generate_json(interaction: discord.Interaction, year: str, month: str):
    try:
        date = await date_validation(year, month)
        dropbox_path = f"/content/uploads/{date}"
        absolute_path = os.path.join(APP_ABSOLUTE_PATH, f"content\\uploads\\{date}")

        if os.path.exists(absolute_path):
            try:
                generate_json_file(dropbox_path, absolute_path, date)
                await interaction.response.send_message(f"json '{date}' generated at {absolute_path}")
                
            except Exception as err:
                raise Exception(f"ERROR (generate_json_File): {err}")
                
        else:
            raise Exception(f"missing folder: '{absolute_path}'")
            
    except Exception as err:
        await interaction.response.send_message(f"ERROR: {err}")

#validate prefix name, dates, and filenames
@client.tree.command(name="validate_folder", description="validate content for specific folder")
async def validate_folder(interaction: discord.Interaction, year: str, month: str):
    try:
        date = await date_validation(year, month)
        dropbox_path = f"/content/uploads/{date}"
        absolute_path = os.path.join(APP_ABSOLUTE_PATH, f"content\\uploads\\{date}")
        
        await validate_json_file(absolute_path)
        
        await rename_json_files(absolute_path)
        
        await interaction.response.defer() # rename_dropbox_files takes longer than 3 seconds, defer and follow up
        await rename_dropbox_files(absolute_path, dropbox_path)
            
        await interaction.followup.send(f"Success!")
                    
    except Exception as err:
        await interaction.response.send_message(f"validate_folder ERROR: {err}")



@client.tree.command(name="whoami", description="Identify the user who issued the command")
async def whoami(interaction: discord.Interaction):
    await interaction.response.send_message(f'You are {interaction.user.name}')

#@client.tree.command(name="jen", description="test description")
#@app_commands.choices(choice=[
#    app_commands.Choice(name="generate folders", value="option_1"),
#    app_commands.Choice(name="generate textfile", value="option_2"),
#    app_commands.Choice(name="validate files", value="option_3"),
#])
#async def ping(interaction: discord.Interaction, choice: app_commands.Choice[str]):
#    await interaction.response.send_message(f"selected: {choice.name}, value: {choice.value}")



#@client.tree.command(name="set_channel")
#async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
#    # Update the configuration with the new channel ID
#    config['channel'] = channel.id
#    await interaction.response.send_message(f'Config variable "channel" set to {channel.id}')



#@client.command()
#async def folder(ctx):
#    try:
#        # Get the files in the folder
#        result = dbx.files_list_folder(TEST)
#        files = result.entries
#        
#        # Print out the files
#        #for file in files:
#            #await ctx.send(f"Name: {file.name}, Type: {'Folder' if isinstance(file, dropbox.files.FolderMetadata) else 'File'}")
#
#        test = files[0]
#
#        shared_link_url = get_or_create_shared_link(test.path_lower)
#        await ctx.send(f"{shared_link_url}")
#        print(f"posted {test.name} with the following link: {shared_link_url}")
#
#    except Exception as err:
#        await ctx.send(f"API error: {err}")

client.run(TOKEN_DISCORD)