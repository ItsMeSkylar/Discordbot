import dropbox
import dropbox.files
import discord

with open("TOKEN.txt", "r") as f:
    TOKEN = f.read()

# Create a Dropbox object using the access token
dbx = dropbox.Dropbox(TOKEN)

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

list_files(DIRECTORY_PATH)