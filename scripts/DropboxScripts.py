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

APP_ABSOLUTE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
APP_DROPBOX_PATH = "/content/uploads"

settings = dropbox.sharing.SharedLinkSettings(
    requested_visibility=dropbox.sharing.RequestedVisibility.public, # Specifies the requested visibility for the shared link. Possible values are public (anyone with the link), team_only (only members of the same Dropbox Business team), or password (with a password).
    expires=None  # or set an expiration time
)

# Create a Dropbox object using the access token
dbx = dropbox.Dropbox(TOKEN_DROPBOX)
try:
    print(dbx.users_get_current_account())
except dropbox.exceptions.AuthError as err:
    setCreds.authorizeDropbox()
    TOKEN_DROPBOX = os.environ["DROPBOX_BEARER"]
    dbx = dropbox.Dropbox(TOKEN_DROPBOX)
    
    
async def check_validity():
    try:
        dbx.users_get_current_account()
        return True
    except dropbox.exceptions.AuthError as err:
        print(f"dropbox Access token is invalid: {err}")
        return False 


async def rename_dropbox_files(date):
    try:
        folder = os.path.join(APP_ABSOLUTE_PATH, "content\\uploads", date)
        
        dropbox_path = f"{APP_DROPBOX_PATH}/{date}"
        
        with open(f'{folder}.json', 'r') as json_file:
            data = json.load(json_file)
        
        for jsondate, content in data["content"].items():
                for file_key, file_data in content["files"].items():
                    filename = file_data.get("filename", "")
                    
                    old_name = dropbox_path + f"/{filename}"
                    new_name = dropbox_path + f"/{file_key}"
                    
                    dbx.files_move_v2(old_name, new_name)
        
    except dropbox.exceptions.ApiError as err:
        raise RuntimeError(f"API error: {err}") from err


def get_or_create_shared_link(path):
    try:
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