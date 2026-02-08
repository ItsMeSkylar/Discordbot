"""from scripts.DropboxScripts import get_all_files"""
import json, re, os, piexif, time, subprocess
from PIL import Image

with open('config.json') as config_file:
    config = json.load(config_file)

APP_ABSOLUTE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
APP_DROPBOX_PATH = "/content/uploads"


async def strip_file_exif(date):
    folder = os.path.join(APP_ABSOLUTE_PATH, "content\\uploads", date)
    
    #BUG: mp4 files exif old file still exists
    
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)

        # exif strip for image files
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            try:
                # Open image and get exif data
                img = Image.open(file_path)
                piexif.load(img.info['exif'])

                # Remove exif data
                exif_bytes = piexif.dump({})
                
                # Save stripped image back to original file
                img.save(file_path, exif=exif_bytes)
                print(f"Stripped EXIF data from {file_path}")
            except Exception as err:
                raise Exception(f"Failed to strip EXIF data from {file_path}: {err}")
            
        # exif strip for video files
        elif filename.lower().endswith(('.mp4')):
            try:
                # Create a temporary file path for the output
                temp_output_path = file_path + ".temp.mp4"
                
                # Command to strip metadata
                command = ["ffmpeg", "-y", "-i", file_path, "-map_metadata", "-1", "-c", "copy", temp_output_path]
                
                # Run the command
                subprocess.run(command, check=True)
                
                # Ensure the ffmpeg process is completed and file handles are closed
                time.sleep(1)

                # Replace original file with the stripped version
                os.replace(temp_output_path, file_path)
                print(f"Stripped EXIF data from {file_path}")
            except subprocess.CalledProcessError as err:
                raise Exception(f"Failed to strip metadata from {file_path}: {err}")
            finally:
                if os.path.exists(temp_output_path):
                    os.remove(temp_output_path)


def generate_json_file (date):
    example_month = f"{date}-XX"
    
    folder = os.path.join(APP_ABSOLUTE_PATH, "content\\uploads", date)
    dropbox_path = f"{APP_DROPBOX_PATH}/{date}"
    
    data = {
        #prefix for every file name
        "namePrefix": "",
        "validated": False,
        "shiny-media-id": config["shiny-media-id"],
        "super-shiny-media-id": config["super-shiny-media-id"],
        "content": {
            #eg 2024-11-xx
            example_month: {
                "header": "",
                "footer": "",
                "channel": 0,
                "posted": False,
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
    with open(f'{folder}.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
     

async def validate_json_file (date):
    #ex 2024-01-02
    pattern = re.compile("^20\d{2}-\d{2}-\d{2}$")
    
    dates = []
    filenames = []
    
    folder = os.path.join(APP_ABSOLUTE_PATH, "content\\uploads", date)
    
    with open(f'{folder}.json', 'r') as json_file:
        data = json.load(json_file)
        
        if data["namePrefix"] == "":
            raise Exception("namePrefix cannot be empty")
        
        for jsonDate in data["content"]:
            if not pattern.match(jsonDate):
                raise Exception("date is not correct")
            
            if data["content"][jsonDate]["channel"] == 0:
                raise Exception(f"channel not set")
            
            dates.append(jsonDate)
            if len(dates) != len(set(dates)):
                raise Exception(f"Duplicate dates found: '{jsonDate}'")
                
            for file_key, file_data in data["content"][jsonDate]["files"].items():
                filename = file_data.get("filename", "")
                
                if not filename:
                    raise Exception(f"filename for '{file_key}' cannot be empty")
                
                filenames.append(filename)
                
                if len(filenames) != len(set(filenames)):
                    raise Exception(f"Duplicate filenames found: '{filename}'")
          
                
async def rename_json_files (date):
    try:
        pattern = re.compile("(?<=\.)[^.]+$")
        
        folder = os.path.join(APP_ABSOLUTE_PATH, "content\\uploads", date)
        
        with open(f'{folder}.json', 'r') as json_file:
            data = json.load(json_file)
            
            if data["validated"] == True:
                raise Exception(f"File already validated")
            
            # Iterate over the content
            for jsondate, content in data["content"].items():
                
                new_files = {}
                
                for file_key, file_data in content["files"].items():
                    filename = file_data.get("filename", "")
                    
                    check = pattern.search(filename)
                    
                    #user has not added file extension by themselves
                    if not check:
                        extension_match = pattern.search(file_key)
                        if extension_match:
                            extension = extension_match.group(0)
                            new_key = f'{data["namePrefix"]} {filename}.{extension}'
                        else:
                            raise Exception("unkown file extension")
                    else:
                        new_key = f'{data["namePrefix"]} {filename}'
                    
                    file_data["filename"] = file_key
                    
                    # Add the new key-value pair to the new_files dictionary
                    new_files[new_key] = file_data
                
                # Replace the old files dictionary with the new one
                data["content"][jsondate]["files"] = new_files
        
        data["validated"] = True
        
        # Write the modified data back to the JSON file
        with open(f'{folder}.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)
                
    except Exception as err:
        raise Exception(f"rename_json_files: {err}")