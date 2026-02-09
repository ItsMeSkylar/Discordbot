from discord.ext import commands
import json
import discord
import aiohttp
import io
import discord
import datetime
import os
import discord

with open('config.json') as config_file:
    config = json.load(config_file)

with open("tokens/TOKEN_DISCORD.txt", "r") as f:
    TOKEN_DISCORD = f.read()

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

# /test dropbox_path:/Apps/Shared/content/upload-schedule/2026-02/DSC00808.JPG
# /test dropbox_path:/Apps/Shared/content/upload-schedule/2026-02/

BASE_URL = "http://localhost/api"  # must be reachable from the bot machine
INTERNAL_TOKEN = "abc123"
APP_DROPBOX_SCHEDULE_PATH = "/Apps/Shared/content/upload-schedule"


@client.tree.command(name="test")
async def post_image(interaction: discord.Interaction, date: str) -> None:
    headers = {"X-Internal-Token": INTERNAL_TOKEN}

    if not date.strip():
        raise RuntimeError("No date path provided.")

    await interaction.response.defer()

    yyyyMM = date.strip()
    DD = "09"

    schedule_url = f"{BASE_URL}/internal/schedule"
    file_url = f"{BASE_URL}/internal/file"

    downloaded = []  # (filename, bytes, description)

    async with aiohttp.ClientSession() as session:
        print("fetch respond from webserver")
        
        # 1) fetch schedule JSON
        async with session.get(
            schedule_url,
            params={"path": yyyyMM, "DD": DD},
            headers=headers,
        ) as resp:
            print("webserver fetch completed!")
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(
                    f"backend schedule failed: {resp.status} {text[:200]}")
            payload = await resp.json()

        # 2) download each file
        for item in payload.get("files", []):
            file_path = item["fileDir"]
            filename = file_path.rsplit("/", 1)[-1]
            desc = item.get("description") or ""
            print("fetch file from webserver: " + filename)

            async with session.get(
                file_url,
                params={"path": file_path},
                headers=headers,
            ) as r:
                print(filename + "fetched!")
                if r.status != 200:
                    text = await r.text()
                    raise RuntimeError(
                        f"backend file failed: {r.status} {text[:200]}")
                data = await r.read()

            downloaded.append((filename, data, desc))

    # 3) send header + embeds + attachments in ONE message
    header_text = payload.get("header") or ""
    footer_text = payload.get("footer") or ""

    embeds = []
    attachments = []

    for filename, data, desc in downloaded:
        attachments.append(discord.File(
            fp=io.BytesIO(data), filename=filename))

        embed = discord.Embed(description=desc or " ", colour=0x9900ff)
        if footer_text:
            embed.set_footer(text=footer_text)

        lower = filename.lower()
        if lower.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
            embed.set_image(url=f"attachment://{filename}")

        embeds.append(embed)

    print("Sending data!")
    await interaction.followup.send(
        content=header_text if header_text else None,
        embeds=embeds,
        files=attachments,
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


def user_validation(user):
    if user in config["whitelist"]:
        return True
    else:
        raise Exception("user not whitelisted")


client.run(TOKEN_DISCORD)
