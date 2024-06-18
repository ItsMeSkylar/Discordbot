import dropbox
import dropbox.files

with open("tokens/TOKEN_DROPBOX.txt", "r") as f:
    TOKEN_DROPBOX = f.read()

# Create a Dropbox object using the access token
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
