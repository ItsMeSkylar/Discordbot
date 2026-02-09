import json
import io
import threading
import asyncio

import discord
from discord.ext import commands
import aiohttp

from fastapi import FastAPI
import uvicorn

# ─────────────────────────────
# Config / tokens
# ─────────────────────────────

with open("config.json") as config_file:
    config = json.load(config_file)

with open("tokens/TOKEN_DISCORD.txt", "r") as f:
    TOKEN_DISCORD = f.read().strip()

BASE_URL = "http://localhost/api"
INTERNAL_TOKEN = "abc123"
HELLO_CHANNEL_ID = 1231050220633325628

# ─────────────────────────────
# Discord bot
# ─────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

# ─────────────────────────────
# FastAPI app
# ─────────────────────────────

app = FastAPI()
BOT_LOOP: asyncio.AbstractEventLoop | None = None
_http_started = False


async def _post_payload(payload: dict):
    channel = client.get_channel(HELLO_CHANNEL_ID)
    if channel is None:
        channel = await client.fetch_channel(HELLO_CHANNEL_ID)

    header_text = payload.get("header") or ""
    footer_text = payload.get("footer") or ""
    files_meta = payload.get("files") or []

    downloaded = []  # (filename, bytes, description)

    headers = {"X-Internal-Token": INTERNAL_TOKEN}
    file_url = f"{BASE_URL}/internal/file"

    async with aiohttp.ClientSession() as session:
        for item in files_meta:
            file_path = item["fileDir"]
            filename = file_path.rsplit("/", 1)[-1]
            desc = item.get("description") or ""

            async with session.get(
                file_url,
                params={"path": file_path},
                headers=headers,
            ) as r:
                if r.status != 200:
                    text = await r.text()
                    raise RuntimeError(f"backend file failed: {r.status} {text[:200]}")
                data = await r.read()

            downloaded.append((filename, data, desc))

    embeds = []
    attachments = []

    for filename, data, desc in downloaded:
        attachments.append(discord.File(fp=io.BytesIO(data), filename=filename))

        embed = discord.Embed(description=desc or " ", colour=0x9900ff)
        if footer_text:
            embed.set_footer(text=footer_text)

        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
            embed.set_image(url=f"attachment://{filename}")

        embeds.append(embed)

    await channel.send(
        content=header_text if header_text else None,
        embeds=embeds,
        files=attachments,
    )

@app.post("/hello")
async def hello(payload: dict):
    if BOT_LOOP is None:
        return {"ok": False, "error": "bot not ready yet"}

    fut = asyncio.run_coroutine_threadsafe(_post_payload(payload), BOT_LOOP)

    try:
        fut.result(timeout=60)  # allow time for file downloads + upload
    except Exception as e:
        return {"ok": False, "error": str(e)}

    return {"ok": True}

def start_http():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

# ─────────────────────────────
# Discord events
# ─────────────────────────────


@client.event
async def on_ready():
    global BOT_LOOP, _http_started

    BOT_LOOP = asyncio.get_running_loop()

    if not _http_started:
        _http_started = True
        threading.Thread(target=start_http, daemon=True).start()

    await client.change_presence(activity=discord.Game(name="Sqrrrks~"))
    await client.tree.sync()
    print("Command tree synced successfully.")
    print("JenniferBot ready!")

# ─────────────────────────────
# Slash command: /test
# ─────────────────────────────


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
        async with session.get(
            schedule_url,
            params={"path": yyyyMM, "DD": DD},
            headers=headers,
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(
                    f"backend schedule failed: {resp.status} {text[:200]}"
                )
            payload = await resp.json()

        for item in payload.get("files", []):
            file_path = item["fileDir"]
            filename = file_path.rsplit("/", 1)[-1]
            desc = item.get("description") or ""

            async with session.get(
                file_url,
                params={"path": file_path},
                headers=headers,
            ) as r:
                if r.status != 200:
                    text = await r.text()
                    raise RuntimeError(
                        f"backend file failed: {r.status} {text[:200]}"
                    )
                data = await r.read()

            downloaded.append((filename, data, desc))

    header_text = payload.get("header") or ""
    footer_text = payload.get("footer") or ""

    embeds = []
    attachments = []

    for filename, data, desc in downloaded:
        attachments.append(
            discord.File(fp=io.BytesIO(data), filename=filename)
        )

        embed = discord.Embed(description=desc or " ", colour=0x9900ff)
        if footer_text:
            embed.set_footer(text=footer_text)

        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
            embed.set_image(url=f"attachment://{filename}")

        embeds.append(embed)

    await interaction.followup.send(
        content=header_text if header_text else None,
        embeds=embeds,
        files=attachments,
    )

# ─────────────────────────────
# Utility command
# ─────────────────────────────


@client.tree.command(name="clear_all_messages")
async def clear_all_messages(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
):
    if interaction.user.name not in config["whitelist"]:
        return await interaction.response.send_message("Not authorized")

    if channel.id not in config["permitted-id-clear-all-messages"]:
        return await interaction.response.send_message(
            f"{channel} is not permitted to clear messages"
        )

    await interaction.response.defer()
    await channel.purge(limit=None)

# ─────────────────────────────
# Start bot
# ─────────────────────────────

client.run(TOKEN_DISCORD)
