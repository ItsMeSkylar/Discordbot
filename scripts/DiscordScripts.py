from scripts.DropboxScripts import get_or_create_shared_link

import json, re, os, discord, asyncio
from datetime import datetime

APP_ABSOLUTE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

async def check_date_and_time(client):
    await client.wait_until_ready()
    while not client.is_closed():
        now = datetime.now()
        today_date = now.date().isoformat()
        
        absolute_path = os.path.join(APP_ABSOLUTE_PATH, "content\\uploads")
        folder = os.path.join(absolute_path, now.strftime('%Y-%m'))
        
        dropbox_path = f"/content/uploads/{now.strftime('%Y-%m')}"
        
        # only post if:
        # clock is after 17:00
        # folder exists
        # json exists
        # validated is true
        # json has current date in content
        # content has NOT been posted
        
        if now.hour >= 17:
            if os.path.exists(folder):
                if os.path.exists(f"{folder}.json"):
                    with open(f'{folder}.json', 'r') as json_file:
                        data = json.load(json_file)
    
                        if data["validated"] == True:
                            if today_date in data["content"]:
                                if data["content"][today_date]["posted"] == False:
                                    
                                    await post_content(client, dropbox_path, folder, today_date)
                                    
                                    data["content"][today_date]["posted"] = True
                                
                                    # Save the updated JSON data back to the file
                                    with open(f"{folder}.json", 'w') as json_file:
                                        json.dump(data, json_file, indent=4)
                                        
                                    print(f"Discord bot post from json: {today_date}")
                                    
                
        # Wait for 60 seconds before checking again
        print(f"Discord bot async update at: {now.strftime('%Y-%m-%d %H:%M')}")
        await asyncio.sleep(60*60)

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