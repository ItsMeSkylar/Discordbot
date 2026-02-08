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
import aiohttp
import io
from PIL import Image

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


BASE_URL = "http://localhost/api"  # must be reachable from the bot machine


@client.tree.command(name="test")
async def post_image(interaction: discord.Interaction, dropbox_path: str) -> None:
    url = f"{BASE_URL}/internal/image"
    headers = {"X-Internal-Token": "abc123"}
    if not dropbox_path.strip():
        raise RuntimeError("No dropbox path provided.")

    await interaction.response.defer()

    async with aiohttp.ClientSession() as session:
        params = {"path": dropbox_path.strip()}
        async with session.get(url, params=params, headers=headers) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(
                    f"backend image fetch failed: {resp.status} {text[:200]}")
            data = await resp.read()

    with Image.open(io.BytesIO(data)) as source_image:
        image = source_image.convert("RGB")
        max_tile_size = 600
        image.thumbnail((max_tile_size, max_tile_size))
        width, height = image.size
        grid_image = Image.new("RGB", (width * 2, height * 2))
        positions = [
            (0, 0),
            (width, 0),
            (0, height),
            (width, height),
        ]
        for position in positions:
            grid_image.paste(image, position)

    output = io.BytesIO()
    grid_image.save(output, format="JPEG", quality=80, optimize=True)
    output.seek(0)
    filename = "image-grid.jpg"
    file = discord.File(fp=output, filename=filename)

    embed = discord.Embed(
        title="Example Header",
        description="This is an example description. Markdown works too!\n\nhttps://automatic.links\n> Block Quotes\n```\nCode Blocks\n```\n*Emphasis* or _emphasis_\n`Inline code` or ``inline code``\n[Links](https://example.com)\n<@123>, <@!123>, <#123>, <@&123>, @here, @everyone mentions\n||Spoilers||\n~~Strikethrough~~\n**Strong**\n__Underline__",
        colour=0x00b0f4,
        timestamp=datetime.datetime.now())
    embed.set_footer(text="Example Footer")
    embed.set_image(url=f"attachment://{filename}")

    await interaction.followup.send(embed=embed, file=file)






@client.tree.command(name="posting")
async def post_image(channel: discord.abc.Messageable, image_id: str):
    url = f"{BASE_URL}/api/internal/image/{image_id}"
    headers = {"X-Internal-Token": "abc123"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                raise RuntimeError(f"{resp.status}: {await resp.text()}")
            data = await resp.read()
            content_type = resp.headers.get("Content-Type", "")

    filename = "image.png" if "png" in content_type else "image.jpg"
    await channel.send(file=discord.File(io.BytesIO(data), filename=filename))


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


# simply generates a folder, you lazy bum
@client.tree.command(name="generate_folder", description="generates folder for content")
async def generate_folders(interaction: discord.Interaction, year: str, month: str):
    try:
        user_validation(interaction.user.name)

        date = await date_validation(year, month)
        absolute_path = os.path.join(
            APP_ABSOLUTE_PATH, f"content\\uploads\\{date}")

        if not os.path.exists(absolute_path):
            os.makedirs(absolute_path)
            await interaction.response.send_message(f"Successfully generated folder: {absolute_path}\nPlease add your content to the folder and then run generate_json.")
        else:
            raise Exception(
                f"Folder '{date}' already exists at '{absolute_path}'")

    except Exception as err:
        await interaction.response.send_message(f"(generate_folders) ERROR: {err}")


# generates json based of content in given folder
@client.tree.command(name="generate_json", description="generates json file based of content in folder")
async def generate_json(interaction: discord.Interaction, year: str, month: str):
    try:
        user_validation(interaction.user.name)

        date = await date_validation(year, month)
        absolute_path = os.path.join(
            APP_ABSOLUTE_PATH, f"content\\uploads\\{date}")

        if not os.path.exists(absolute_path):
            raise Exception(f"missing folder: '{absolute_path}'")

        generate_json_file(date)
        await interaction.response.send_message(f"json successfully generated at {absolute_path}!\nplease edit the json file and then run validate_folder.")

    except Exception as err:
        await interaction.response.send_message(f"(generate_json) ERROR: {err}")


# validate prefix name, dates, and filenames
@client.tree.command(name="validate_folder", description="validate content for specific folder")
async def validate_folder(interaction: discord.Interaction, year: str, month: str):
    try:
        user_validation(interaction.user.name)

        date = await date_validation(year, month)
        dropbox_path = f"/content/uploads/{date}"
        print(dropbox_path)
        await validate_json_file(date)
        await rename_json_files(date)

        # rename_dropbox_files takes longer than 3 seconds, defer and follow up
        await interaction.response.defer()

        await strip_file_exif(date)
        # await rename_dropbox_files(date)

        await interaction.followup.send(f"Folder and Json validated!\nensure that it works by using /post")

    except Exception as err:
        await interaction.response.send_message(f"(validate_folder) ERROR: {err}")


@client.tree.command(name="post", description="posts content to channel")
async def post(interaction: discord.Interaction, year: str, month: str, day: str, channel: discord.TextChannel = None):
    try:
        user_validation(interaction.user.name)

        date = await date_validation(year, month, day)

        # post_content takes longer than 3 seconds, defer and follow up
        await interaction.response.defer()
        """"
        if channel:
           await post_content(client, date, channel.id)
        else:
            await post_content(client, date)
        """

        await interaction.delete_original_response()

    except Exception as err:
        await interaction.response.send_message(f"(post) ERROR: {err}")


@client.tree.command(name="set_channel")
async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    try:
        user_validation(interaction.user.name)
        config['channel'] = channel.id
        await interaction.response.send_message(f'Config variable "channel" set to {channel.id}')

    except Exception as err:
        return await interaction.response.send_message(f"{err}")


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
