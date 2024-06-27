import dropbox, os
import dropbox.files
import setCreds

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



def get_or_create_shared_link(path):
    try:
        # Try to create a shared link
        shared_link = dbx.sharing_create_shared_link_with_settings(path)
        return shared_link.url
    
    except dropbox.exceptions.ApiError as err:
        if isinstance(err.error, dropbox.sharing.CreateSharedLinkWithSettingsError) and err.error.is_shared_link_already_exists():
            # If the shared link already exists, retrieve the existing link
            links = dbx.sharing_list_shared_links(path=path)
            if links.links:
                return links.links[0].url
        raise err



def get_all_files(path):
    try:
        result = dbx.files_list_folder(path)
        files = result.entries
        return files
    
    except Exception as err:
        raise (f"API error: {err}")