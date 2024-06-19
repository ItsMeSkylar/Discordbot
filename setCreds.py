import os, json, requests

## GLOBALS ########################################################################
CREDSFILE = "creds.json"
######################################################################## GLOBALS ##


def authorizeDropbox():
    dev_url = "https://www.dropbox.com/developers/apps/info/" + os.environ["DROPBOX_APP_KEY"]
    user_input_token = input("Enter a DROPBOX token from " + dev_url + " or hit return to proceed with an OAuth Flow")

    if user_input_token == "":
        # build the authorization URL:
        authorization_url = "https://www.dropbox.com/oauth2/authorize?client_id=%s&response_type=code" % os.environ["DROPBOX_APP_KEY"]
        # send the user to the authorization URL:
        print('Go to the following URL and allow access:')
        print(authorization_url)

        # get the authorization code from the user:
        authorization_code = input('Enter the code:\n')

        # exchange the authorization code for an access token:
        token_url = "https://api.dropboxapi.com/oauth2/token"
        params = {
            "code": authorization_code,
            "grant_type": "authorization_code",
            "client_id": os.environ["DROPBOX_APP_KEY"],
            "client_secret": os.environ["DROPBOX_APP_SECRET"]
        }
        r = requests.post(token_url, data=params)
        print(r.text)

        commitLatestDropboxBearer(r.json()["access_token"])
    else:
        commitLatestDropboxBearer(user_input_token)

# A function which creates a file for the app user. The user will access the file and fill it with keys.
# RUN ME FIRST
def bootstrap_creds():
    # Test if the JSON file exists and has something in it..
    if (not os.path.exists(CREDSFILE)) or (os.stat(CREDSFILE).st_size == 0):
        # a template JSON file for storing sensitive API keys
        creds = {
            "DROPBOX_APP_KEY": "",
            "DROPBOX_APP_SECRET": ""
        }
        with open(CREDSFILE, "w") as write_file:
            json.dump(creds, write_file)
        print("I created a file named "+ CREDSFILE + " for you. Fill in the things and save it.")
        exit()

    else: # JSON file exists. Attempt to read credencials from it and dump those creds to the shell environment variables
        with open(CREDSFILE, "r") as read_file:
            r = json.load(read_file)
            try:
                os.environ["DROPBOX_APP_KEY"] = r["DROPBOX_APP_KEY"]
                os.environ["DROPBOX_APP_SECRET"] = r["DROPBOX_APP_SECRET"]
            except KeyError:
                print("BADLY FORMATTED " + CREDSFILE + ". TRY AGAIN...")
                exit()
            try:
                os.environ["DROPBOX_BEARER"] = r["DROPBOX_BEARER"]
            except KeyError:
                print("No DROPBOX_BEARER token stored in " + CREDSFILE)
                print("Not an issue. The app will need to run the OAuth Flow...")

# A function used to append the most recent DROPBOX Bearer token to the JSON file, so we do not have to authorize the app on every run..
def commitLatestDropboxBearer(intoken):
    try:
        #DROPBOX_BEARER = os.environ["DROPBOX_BEARER"]
        DROPBOX_BEARER = os.environ["DROPBOX_BEARER"] = intoken
        with open(CREDSFILE, "r+") as write_file:
            f = json.load(write_file)
            f["DROPBOX_BEARER"] = DROPBOX_BEARER

            write_file.truncate(0) # clear the file contents
            write_file.seek(0) # move the file cursor back to start

            json.dump(f, write_file) # write the updated file contents
    except KeyError:
        print("no token loaded in memory.. The app did not successfully acquire an OAuth BEARER TOKEN")

