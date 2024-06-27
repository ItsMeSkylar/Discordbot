from scripts.DropboxScripts import get_all_files
import json

def generate_json_File (dropbox_path, absolute_path, month):
    example_month = f"{month}-XX"
    
    data = {
        #prefix for every file name
        "namePrefix": "",
        "content": {
            example_month: {
                "header": "",
                "footer": ""
            }
        }
    }
    
    files = get_all_files(dropbox_path)
    for file in files:
        data["content"][example_month][file.name] = {}
        data["content"][example_month][file.name]["filename"] = ""
        data["content"][example_month][file.name]["description"] = ""

    # Save data to JSON file
    with open(f'{absolute_path}.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)