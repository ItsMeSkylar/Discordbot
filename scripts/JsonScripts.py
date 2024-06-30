from scripts.DropboxScripts import get_all_files
import json
import re

def generate_json_File (dropbox_path, absolute_path, date):
    example_month = f"{date}-XX"
    
    data = {
        #prefix for every file name
        "namePrefix": "",
        "content": {
            #eg 2024-11-xx
            example_month: {
                "header": "",
                "footer": "",
                "files": {}
            }
        }
    }
    
    files = get_all_files(dropbox_path)
    for file in files:
        data["content"][example_month]["files"][file.name] = {}
        data["content"][example_month]["files"][file.name]["filename"] = ""
        data["content"][example_month]["files"][file.name]["description"] = ""

    # Save data to JSON file
    with open(f'{absolute_path}.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
     
async def validate_json_life (absolute_path):
    #ex 2024-01-02
    pattern = re.compile("^20\d{2}-\d{2}-\d{2}$")
    
    filenames = []
    
    with open(f'{absolute_path}.json', 'r') as json_file:
        data = json.load(json_file)
        
        if data["namePrefix"] == "":
            raise Exception("namePrefix cannot be empty")
        
        for jsonDate in data["content"]:
            if not pattern.match(jsonDate):
                raise Exception("date is not correct")
                
            for file_key, file_data in data["content"][jsonDate]["files"].items():
                filename = file_data.get("filename", "")
                
                if not filename:
                    raise Exception(f"filename for '{file_key}' cannot be empty")
                
                filenames.append(filename)
                
                if len(filenames) != len(set(filenames)):
                    raise Exception(f"Duplicate filenames found: '{filename}'")