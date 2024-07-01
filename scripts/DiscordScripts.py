from scripts.DropboxScripts import get_or_create_shared_link

import json, re, os, discord, asyncio
from datetime import datetime

#F:\Dropbox\Apps\DiscordTestApp
APP_ABSOLUTE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
APP_DROPBOX_PATH = "/content/uploads"


#running in the background
async def check_date_and_time(client):
    await client.wait_until_ready()
    while not client.is_closed():
        now = datetime.now()
        today_date = now.date().isoformat()
        
        folder = os.path.join(APP_ABSOLUTE_PATH, "content\\uploads", now.strftime('%Y-%m'))
        
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
                                    
                                    await post_content(client, today_date)
                                    
                                    data["content"][today_date]["posted"] = True
                                
                                    # Save the updated JSON data back to the file
                                    with open(f"{folder}.json", 'w') as json_file:
                                        json.dump(data, json_file, indent=4)
                                        
                                    print(f"Discord bot post from json: {today_date}")
                                    
        # Wait for 60 seconds before checking again
        print(f"Discord bot async update at: {now.strftime('%Y-%m-%d %H:%M')}")
        await asyncio.sleep(60*60)


async def post_content(client, date, channel_id = None):
    
    absolute_path = f"{APP_ABSOLUTE_PATH}\\content\\uploads\\{date[:7]}"
    dropbox_path = f"{APP_DROPBOX_PATH}/{date[:7]}"
    
    try:
        with open(f'{absolute_path}.json', 'r') as json_file:
            data = json.load(json_file)
        
        #video files MUST be send seperately
        pattern = re.compile("(?<=\.)mp4+$")
        
        if date in data['content']:
            json_data = data['content'][date]
            
            channel = client.get_channel(channel_id) if channel_id else client.get_channel(json_data["channel"])
            
            if json_data["header"]:
                await channel.send(json_data["header"])
                
            message = ""
            
            for file_key, files in json_data["files"].items():
                extension = pattern.search(file_key)
                
                # video files from dropbox
                if extension:
                    filename = dropbox_path+f"/{file_key}"
                    message += f"\n{files['description']}\n{get_or_create_shared_link(filename)}"
                    
                #image files
                else:
                    image_path = os.path.join(absolute_path, file_key)
                
                    with open(image_path, 'rb') as image_file:
                        image = discord.File(image_file)
                        await channel.send(content=files['description'], file=image)
                    
            message += f"\n\n{json_data['footer']}"
                
            if message:
                await channel.send(message)
        else:
            raise KeyError(f"Content for date '{date}' not found.")
        
    except Exception as err:
        raise Exception(f"(post_content) ERROR: {err}")