import datetime
from scripts.JsonScripts import generate_json_file
from scripts.JsonScripts import validate_json_file
from scripts.JsonScripts import rename_json_files
from scripts.JsonScripts import strip_file_exif

""""
from scripts.DiscordScripts import post_content
from scripts.DiscordScripts import check_date_and_time

from scripts.DropboxScripts import rename_dropbox_files
"""

from discord.ext import commands
import os
import json
import discord
import aiohttp
import io
import os
import json
import discord
import datetime
import dropbox.files
import os
import json
import discord
import aiohttp, json

with open('config.json') as config_file:
    config = json.load(config_file)

# with open("tokens/TOKEN_DROPBOX.txt", "r") as f:
#    TOKEN_DROPBOX = f.read()
"""TOKEN_DROPBOX = os.environ["DROPBOX_BEARER"]"""

with open("tokens/TOKEN_DISCORD.txt", "r") as f:
    TOKEN_DISCORD = f.read()

# Create a Dropbox object using the access token
"""dbx = dropbox.Dropbox(TOKEN_DROPBOX)"""

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

APP_ABSOLUTE_PATH = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)))


def user_validation(user):
    if user in config["whitelist"]:
        return True
    else:
        raise Exception("user not whitelisted")


async def date_validation(year, month, day=None):
    if not year.isdigit() or not month.isdigit():
        raise Exception(f"ERROR: Year and month must be numeric.")

    ret = ""

    year_num = int(year)
    month_num = int(month)

    if year_num < 100:
        year_num += 2000

    if year_num < 1000 or year_num > 9999:
        raise Exception(f"ERROR: Invalid year. Please provide a 4-digit year.")

    ret += str(year_num)

    if month_num < 1 or month_num > 12:
        raise Exception(
            f"ERROR: Invalid month. Please provide a month between 1 and 12.")

    ret += f"-{month_num:02d}"

    if day:
        day_num = int(day)
        if day_num < 1 or day_num > 31:
            raise Exception(
                f"ERROR: Invalid day. Please provide a day between 1 and 31.")

        ret += f"-{day_num:02d}"

    return ret


# /Apps/Shared/content/upload-schedule/2026-02/july file 4.JPG

BASE_URL = "http://localhost/api"  # must be reachable from the bot machine
INTERNAL_TOKEN = "abc123"
APP_DROPBOX_SCHEDULE_PATH = "/Apps/Shared/content/upload-schedule"

@client.tree.command(name="test")
async def post_image(interaction: discord.Interaction, dropbox_path: str) -> None:

    if not dropbox_path.strip():
        raise RuntimeError("No date provided.")

    await interaction.response.defer()

    schedule_date = dropbox_path.strip()
    dbx = dropbox.Dropbox(os.environ["DROPBOX_BEARER"])
    file_paths = []
    schedule_path = f"/Apps/Shared/content/upload-schedule/{schedule_date}.json"
    _metadata, response = dbx.files_download(schedule_path)
    schedule = json.loads(response.content.decode("utf-8"))
    if not schedule.get("content"):
        raise RuntimeError("Schedule JSON has no content.")

    matching_date = None
    for content_date in sorted(schedule["content"].keys()):
        if content_date.startswith(f"{schedule_date}-"):
            matching_date = content_date
            break

    if not matching_date:
        raise RuntimeError(f"No content found for {schedule_date}.")

    files = schedule["content"][matching_date].get("files", {})
    if not files:
        raise RuntimeError(f"Schedule JSON has no files for {matching_date}.")

    for file_key in list(files.keys())[:4]:
        file_paths.append(f"/content/uploads/{schedule_date}/{file_key}")


    embeds = []
    files = []
    for index, file_path in enumerate(file_paths, start=1):
        _metadata, response = dbx.files_download(file_path)
        data = response.content
        filename = os.path.basename(file_path) or f"image-{index}.jpg"
        file = discord.File(fp=io.BytesIO(data), filename=filename)
        files.append(file)
        embed = discord.Embed(
            # title="Example Header",
            description="header description",
            colour=0x9900ff)
        embed.set_footer(text="footer description")
        embed.set_image(url=f"attachment://{filename}")
        embeds.append(embed)

    await interaction.followup.send(
        content="Text above all embeds",
        embeds=embeds,
        files=files
    )
    
    await interaction.followup.send(
    content="Text below all embeds"
    )
















@client.event
async def on_ready():
    try:
        # client.loop.create_task(check_date_and_time(client))
        await client.change_presence(activity=discord.Game(name="Sqrrrks~"))
        await client.tree.sync()
        print("Command tree synced successfully.")
        print("JenniferBot ready!")
    except Exception as err:
        print(f"Failed to sync command tree: {err}")


@client.tree.command(name="channel_id")
async def get_channel_id(interaction: discord.Interaction, channel: discord.TextChannel):
    try:
        return channel.id
    except Exception as err:
        return await interaction.response.send_message(f"{err}")


@client.tree.command(name="clear_all_messages")
async def clear_all_messages(interaction: discord.Interaction, channel: discord.TextChannel):
    try:

        user_validation(interaction.user.name)

        if not channel.id in config["permitted-id-clear-all-messages"]:
            return await interaction.response.send_message(f"{channel} is not permitted to clear all messages")

        # funny solution, defer message, message will be deleted, dont respond to it
        await interaction.response.defer()
        await channel.purge(limit=None)

    except discord.NotFound:
        await interaction.followup.send("Error: The message was not found.")
    except discord.Forbidden:
        await interaction.followup.send("Error: You do not have the required permissions to delete messages in this channel.")
    except discord.HTTPException as e:
        await interaction.followup.send(f"Error: Failed to clear messages due to an HTTPException: {e}")
    except Exception as e:
        await interaction.followup.send(f" (clear_all_messages) ERROR: {e}")


client.run(TOKEN_DISCORD)
