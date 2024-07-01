from scripts.DropboxScripts import get_or_create_shared_link

import json, re, os, discord

async def post_content(client, dropbox_path, absolute_path, date):
    try:
        with open(f'{absolute_path}.json', 'r') as json_file:
            data = json.load(json_file)
        
        #video files MUST be send seperately
        pattern = re.compile("(?<=\.)mp4+$")
        
        if date in data['content']:
            json_data = data['content'][date]
            
            channel = client.get_channel(json_data["channel"])
            
            await channel.send(json_data["header"])
            message = ""
            
            for file_key, files in json_data["files"].items():
                
                extension = pattern.search(file_key)
                
                if extension:
                    filename = dropbox_path+f"/{file_key}"
                    try:    
                        url = get_or_create_shared_link(filename)
                        message += f"\n{files['description']}\n{url}"
                    except Exception as err:
                        raise Exception(f"ERROR (post_content): {err}")
                else:
                    image_path = os.path.join(absolute_path, file_key)
                    try:
                        # Upload the image to Discord and get its URL
                        with open(image_path, 'rb') as image_file:
                            image = discord.File(image_file)
                            await channel.send(content=files['description'], file=image)
                            #image_url = uploaded_image.attachments[0].url  # Assuming single attachment
                    except Exception as err:
                        raise Exception(f"ERROR (post_content): {err}")
                    
            message += f"\n\n{json_data['footer']}"
                
            await channel.send(message)
        else:
            raise KeyError(f"Content for date '{date}' not found.")
        
    except Exception as err:
        raise Exception(f"error {err}")