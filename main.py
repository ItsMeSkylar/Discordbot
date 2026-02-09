import datetime


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
import aiohttp
import json

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


# /test dropbox_path:/Apps/Shared/content/upload-schedule/2026-02/DSC00808.JPG
# /test dropbox_path:/Apps/Shared/content/upload-schedule/2026-02/

BASE_URL = "http://localhost/api"  # must be reachable from the bot machine
INTERNAL_TOKEN = "abc123"
APP_DROPBOX_SCHEDULE_PATH = "/Apps/Shared/content/upload-schedule"


@client.tree.command(name="test")
async def post_image(interaction: discord.Interaction, date: str) -> None:
    url = f"{BASE_URL}/internal/image"
    headers = {"X-Internal-Token": INTERNAL_TOKEN}
    if not date.strip():
        raise RuntimeError("No date path provided.")

    await interaction.response.defer()


    yyyyMM = date.strip()
    DD = "03" 
    
    test =  f"{BASE_URL}/internal/schedule"
    print(test)
    
    async with aiohttp.ClientSession() as session:
        
        # 1) get schedule JSON
        async with session.get(
            test,
            params={"path": yyyyMM, "DD": DD},
            headers=headers,
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(f"backend schedule failed: {resp.status} {text[:200]}")
            payload = await resp.json()
            
        files = []
            
        # 2) fetch each file and attach
        for item in payload.get("files", []):
            file_path = item["fileDir"]  # exact Dropbox path
            filename = file_path.rsplit("/", 1)[-1]

            async with session.get(
                f"{BASE_URL}/internal/file",
                params={"path": file_path},
                headers=headers,
            ) as r:
                if r.status != 200:
                    text = await r.text()
                    raise RuntimeError(f"backend file failed: {r.status} {text[:200]}")
                data = await r.read()

            files.append(discord.File(fp=io.BytesIO(data), filename=filename))
        
          
    """above old change"""       
            
   # send message + attachments
    content = payload.get("header") or ""
    await interaction.followup.send(content=content, files=files)
    
    embeds = []
    files = []
    for index in range(1, 5):
        filename = f"image-{index}.jpg"
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
