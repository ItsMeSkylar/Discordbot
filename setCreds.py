import os, json

## GLOBALS ########################################################################
CREDSFILE = "creds.json"
######################################################################## GLOBALS ##


# A function which creates a file for the app user. The user will access the file and fill it with keys.
def bootstrap_creds():

    # a template JSON file for storing sensitive API keys
    creds = {
        "DROPBOX_APP_KEY":"",
        "DROPBOX_APP_SECRET":""
    }
    with open(CREDSFILE, "w") as write_file:
        json.dump(creds, write_file)

# Test if the JSON file exists and has something in it..
if (not os.path.exists(CREDSFILE)) or (os.stat(CREDSFILE).st_size == 0):
    bootstrap_creds()
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
def commitLatestDropboxBearer():
    try:
        DROPBOX_BEARER = os.environ["DROPBOX_BEARER"]
        with open(CREDSFILE, "r+") as write_file:
            f = json.load(write_file)
            f["DROPBOX_BEARER"] = DROPBOX_BEARER

            write_file.truncate(0) # clear the file contents
            write_file.seek(0) # move the file cursor back to start

            json.dump(f, write_file) # write the updated file contents
    except KeyError:
        print("no token loaded in memory.. The app did not successfully acquire an OAuth BEARER TOKEN")

