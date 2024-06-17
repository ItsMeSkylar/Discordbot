import dropbox # type: ignore
import dropbox.files  # type: ignore

import discord  # type: ignore
from discord.ext import commands # type: ignore
import os

with open("TOKEN_DROPBOX.txt", "r") as f:
    TOKEN_DROPBOX = f.read()

with open("TOKEN_DISCORD.txt", "r") as f:
    TOKEN_DISCORD = f.read()

# Create a Dropbox object using the access token
dbx = dropbox.Dropbox(TOKEN_DROPBOX)

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
DIRECTORY_PATH = '/images'








list_files(DIRECTORY_PATH)