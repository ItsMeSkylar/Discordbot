
import dropbox, os
import dropbox.files
import setCreds
import json

# Load credencials into system environment variables.
# os.environ["DROPBOX_APP_KEY"]
# os.environ["DROPBOX_APP_SECRET"]
# os.environ["DROPBOX_BEARER"]
setCreds.bootstrap_creds()

#with open("tokens/TOKEN_DROPBOX.txt", "r") as f:
#    TOKEN_DROPBOX = f.read()

TOKEN_DROPBOX = os.environ["DROPBOX_BEARER"]

# Create a Dropbox object using the access token
dbx = dropbox.Dropbox(TOKEN_DROPBOX)
try:
    print(dbx.users_get_current_account())
except dropbox.exceptions.AuthError as err:
    setCreds.authorizeDropbox()
    TOKEN_DROPBOX = os.environ["DROPBOX_BEARER"]
    dbx = dropbox.Dropbox(TOKEN_DROPBOX)


async def rename_dropbox_files(absolute_path, dropbox_path):
    try:
        with open(f'{absolute_path}.json', 'r') as json_file:
            data = json.load(json_file)
        
        for date, content in data["content"].items():
                for file_key, file_data in content["files"].items():
                    filename = file_data.get("filename", "")
                    
                    old_name = dropbox_path + f"/{filename}"
                    new_name = dropbox_path + f"/{file_key}"
                    
                    dbx.files_move_v2(old_name, new_name)
        
    except dropbox.exceptions.ApiError as err:
        raise RuntimeError(f"API error: {err}") from err


def get_or_create_shared_link(path):
    try:
        # Create settings object
        settings = dropbox.sharing.SharedLinkSettings(
            requested_visibility=dropbox.sharing.RequestedVisibility.public, # Specifies the requested visibility for the shared link. Possible values are public (anyone with the link), team_only (only members of the same Dropbox Business team), or password (with a password).
            expires=None  # or set an expiration time
        )
        
        # Try to create a shared link
        shared_link = dbx.sharing_create_shared_link_with_settings(path, settings)
        return shared_link.url
    
    except dropbox.exceptions.ApiError as err:
        if isinstance(err.error, dropbox.sharing.CreateSharedLinkWithSettingsError) and err.error.is_shared_link_already_exists():
            # If the shared link already exists, retrieve the existing link
            links = dbx.sharing_list_shared_links(path=path)
            if links.links:
                return links.links[0].url
            else:
                raise Exception(f"No shared link found for '{path}'")
            
        elif isinstance(err.error, dropbox.exceptions.HttpError):
            # Handle HTTP errors (e.g., connection issues)
            raise Exception(f"HTTP error occurred: {err}")

        else:
            # Handle other Dropbox API errors
            raise Exception(f"Dropbox API error occurred: {err}")

def get_all_files(path):
    try:
        result = dbx.files_list_folder(path)
        files = result.entries
        return files
    
    except Exception as err:
        raise (f"API error: {err}")