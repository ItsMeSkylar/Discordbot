import dropbox
import dropbox.files
import discord

with open("TOKEN.txt", "r") as f:
    TOKEN = f.read()

dbx = dropbox.Dropbox(TOKEN)