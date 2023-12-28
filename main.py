import pypresence
import threading
import requests
import textwrap
import warnings
import datetime
import asyncio
import difflib
import logging
import discord
import pystyle
import random
import math
import time
import json
import sys
import os
import re

from PIL import Image, ImageDraw, ImageFont, ImageOps
if os.name == "nt":
    from win11toast import toast_async as toast
else:
    from notify import notification
    import playsound
from aiohttp import ClientSession
from colorama import Fore, Style
from discord.ext import commands
from discord import File
from io import BytesIO

warnings.filterwarnings("ignore", category=DeprecationWarning)

#negawat?
#os.system("pip install Pillow==9.4.0")

def prettyprint(text):
    print(f"[{Fore.LIGHTMAGENTA_EX}{time.strftime('%H:%M:%S')}{Style.RESET_ALL}] {text}")

def clear():
    os.system("cls") if os.name == "nt" else os.system("clear")

clear()

global state
state = False

class Config:
    def __init__(self):
        self.token = ""
        self.prefix = ""
        self.mode = "image"
        self.delete_after = 15
        self.logging = "console"
        self.notify = True
        self.log = {
            "ghostping": True,
            "ping": True,
            "messages": True
        }
        self.rpc = {
            "enabled": True,
            "id"
            "name": "Velt",
            "details": "",
            "large_image": "velt",
            "large_text": "Velt",
            "small_image": "",
            "small_text": "",
            "buttons": [
                {
                    "label": "Discord",
                    "url": "https://discord.gg/dQ96PhfqNq"
                }
            ]
        }
        self.embed = {
            "image": "",
            "footer": ""
        }

    def check(self):
        if not os.path.exists("scripts"):
            os.makedirs("scripts")
        if not os.path.exists("config.json") or os.stat("config.json").st_size == 0:
            y = """
{
    "token": "",
    "prefix": "",
    "mode": "image",
    "delete_after": 15,
    "logging": "channel",
    "notify": true,
    "log": {
        "ghostping": true,
        "ping": true,
        "messages:": true
    },
    "rpc": {
        "enabled": true,
        "id": "1185652637966811146",
        "state": "best!?",
        "name": "Velt",
        "details": "",
        "large_image": "velt",
        "large_text": "Velt",
        "small_image": "",
        "small_text": "",
        "buttons": [
            {
                "label": "Discord",
                "url": "https://discord.gg/dQ96PhfqNq"
            }
        ]
    },
    "embed": {
        "footer": "Velt"
    }
}
"""
            with open("config.json", "w") as f:
                f.write(y)
        else:
            with open("config.json", "r") as f:
                data = json.load(f)
        for key, value in data.items():
            if value == "":
                prettyprint(f"{key} is not set, set it below.")
                data[key] = input("> ")
                with open("config.json", "w") as f:
                    json.dump(data, f, indent=4)
                setattr(self, key, value)
            else:
                setattr(self, key, value)

    def setk(self, key_path, value):
        if value == "true":
            value = True
        elif value == "false":
            value = False
        keys = key_path.split('.')
        with open("config.json", "r") as f:
            data = json.load(f)
        temp = data
        for key in keys[:-1]:
            temp = temp.get(key, {})
        temp[keys[-1]] = value
        with open("config.json", "w") as f:
            json.dump(data, f, indent=4)

    def get(self):
        with open("config.json", "r") as f:
            data = json.load(f)
        return data

cfg = Config()
cfg.check()



class Notif:
    def __init__(self):
        self.title = "Velt"

    async def send(self, message):
        if cfg.notify == True:
            if os.name == "nt":
                # do nothing on dismiss
                await toast(title=self.title, body=message, icon=os.path.abspath("assets/velt_big.png"), audio=os.path.abspath("assets/notif.wav"), app_id="Velt", on_dismissed=lambda reason: None)
            else:
                playsound.playsound(os.path.abspath("assets/notif.wav"), block=False)
                notification(summary=self.title, message=message, timeout=5000, app_name="Velt", image=os.path.abspath("assets/velt_big.png"))
                

def downloadAssets():
    assets = [
        "https://raw.githubusercontent.com/VeltBot/assets/main/velt_big.png",
        "https://raw.githubusercontent.com/VeltBot/assets/main/icon.ico",
        "https://raw.githubusercontent.com/VeltBot/assets/main/notif.wav",
        "https://raw.githubusercontent.com/VeltBot/assets/main/Metropolis-Regular.otf",
        "https://raw.githubusercontent.com/VeltBot/assets/main/Metropolis-Bold.otf"
    ]
    for asset in assets:
        name = asset.split("/")[-1]
        os.makedirs('assets', exist_ok=True)
        if not os.path.exists(f"assets/{name}"):
            with open(f"assets/{name}", "wb") as f:
                prettyprint(f"Downloading {name}")
                f.write(requests.get(asset).content)

def loadscripts():
    for filename in os.listdir("scripts"):
        if filename.endswith(".py"):
            name = filename[:-3]
            velt.load_extension(f"scripts.{name}")
            prettyprint(f"Loaded {name}")

downloadAssets()

notif = Notif()

velt = commands.Bot(command_prefix=cfg.prefix, self_bot=True, chunk_guilds_at_startup=False, request_guilds=False, help_command=None)
deleted_messages = []

@velt.event
async def on_ready():
    if os.name == "nt":
        os.system("title Velt")
    asyncio.create_task(notif.send("Logged in"))
    banner = """                                           
.sSSS s.    .sSSSSs.    SSSSS       .sSSSSSSSSSSSSSs. 
S SSS SSSs. S SSSSSSSs. S SSS       SSSSS S SSS SSSSS 
S  SS SSSSS S  SS SSSS' S  SS       SSSSS S  SS SSSSS 
S..SS SSSSS S..SS       S..SS       `:S:' S..SS `:S:' 
 S::S SSSS  S:::SSSS    S:::S             S:::S       
  S;S SSS   S;;;S       S;;;S             S;;;S       
   SS SS    S%%%S SSSSS S%%%S SSSSS       S%%%S       
    SsS     SSSSSsSS;:' SSSSSsSS;:'       SSSSS       
"""
    global start_time
    global rpc
    ################## thanks HannahHaven
    url = "https://discord.com/api/v9/users/@me/relationships"
    r = requests.get(url, headers={"Authorization": cfg.token})
    decode = r.json()
    friends = [user for user in decode if user.get('type') == 1]
    pending = [user for user in decode if user.get('type') == 4]
    blocked = [user for user in decode if user.get('type') == 2]
    txtf = f"{Fore.GREEN}{len(friends)}{Style.RESET_ALL}/{Fore.YELLOW}{len(pending)}{Style.RESET_ALL}/{Fore.RED}{len(blocked)}{Style.RESET_ALL}"
    ##################
    guilds = len(velt.guilds)
    txtg = f"{Fore.LIGHTMAGENTA_EX}{guilds}{Style.RESET_ALL}"
    zamn = f"""
[-] Friend count: {txtf}
[-] Guild count: {txtg}
[-] Prefix: {Fore.LIGHTMAGENTA_EX}{cfg.prefix}{Style.RESET_ALL}
[-] Started at: {Fore.LIGHTMAGENTA_EX}{time.strftime('%H:%M:%S')}{Style.RESET_ALL}
""".replace("[-]", f"[{Fore.LIGHTMAGENTA_EX}-{Style.RESET_ALL}]")
    start_time = time.time()
    print(Fore.LIGHTMAGENTA_EX)
    print(pystyle.Center.XCenter(banner))
    print(Style.RESET_ALL)
    print(zamn)
    cmds = len(velt.commands)
    if cfg.rpc["enabled"] == True:
        rpc = pypresence.AioPresence(cfg.rpc["id"])
        buttons = cfg.rpc["buttons"]
        await rpc.connect()
        prettyprint("RPC connected")
        await rpc.update(state=cfg.rpc["state"] ,details=cfg.rpc["details"], large_image=cfg.rpc["large_image"], large_text=cfg.rpc["large_text"], start=start_time, buttons=buttons)
        prettyprint(f"{cfg.rpc['state']} | {cfg.rpc['details']}")
    prettyprint(f"Logged in as {velt.user.name} ({Fore.LIGHTMAGENTA_EX}{velt.user.id}{Style.RESET_ALL})")

@velt.event
async def on_command(ctx):
    prettyprint(f"Command: {ctx.message.content[1:]}")
    try:
        await ctx.message.delete()
    except:
        pass

@velt.event
async def on_command_error(ctx, error):
    try:
        await ctx.message.delete()
    except:
        pass
    if cfg.logging == "console":
        prettyprint(f"{error}")
    elif cfg.logging == "channel":
        await veltSend(ctx, "Error", f"{error}")

@velt.event
async def on_message_delete(message):
    if cfg.log["ghostping"] == True:
        if message.mentions:
            if message.mentions.__contains__(velt.user):
                prettyprint(f"{message.author.name} ghost pinged you in {message.guild.name} ({message.guild.id})")
                asyncio.create_task(notif.send(f"{message.author.name} ghost pinged you in {message.guild.name} ({message.guild.id})"))
    if cfg.log["messages"] == True:
        msg_object = {
            "content": message.content,
            "author": message.author.name,
            "channel": message.channel.id,
            #"guild": message.guild.id
        }
        global deleted_messages
        deleted_messages.append(msg_object)

@velt.event
async def on_message(message):
    if cfg.log["ping"] == True:
        if message.mentions:
            if message.mentions.__contains__(velt.user):
                prettyprint(f"{message.author.name} pinged you in {message.guild.name} ({message.guild.id})")
                asyncio.create_task(notif.send(f"{message.author.name} pinged you in {message.guild.name} ({message.guild.id})"))
    await velt.process_commands(message)


def generate_image(title, description, footer):
    colors = {
        'text': (255, 255, 255),
        'background': (25,25,25),
        'primary': (255,188,207),
        'secondary': (10, 10, 10),
        'accent': (158, 41, 74)
    }

    image_width = 750
    image_height = 850
    title_padding = 35
    description_padding = 6.5
    footer_padding = 20
    corner_radius = 50

    image = Image.new('RGB', (image_width, image_height), colors['background'])
    draw = ImageDraw.Draw(image)

    title_font_size = int(image_width * 0.089)
    title_font = ImageFont.truetype(f'assets/Metropolis-Bold.otf', title_font_size)

    description_font_size = int(image_width * 0.0515)
    description_font = ImageFont.truetype(f'assets/Metropolis-Regular.otf', description_font_size)

    footer_font_size = int(image_width * 0.06)
    footer_font = ImageFont.truetype(f'assets/Metropolis-Bold.otf', footer_font_size)
    footer_width, footer_height = draw.textsize(footer, font=footer_font)

    description_lines = []
    for line in description.split('\n'):
        description_lines.extend(textwrap.wrap(line, width=35))

    title_height = draw.textsize(title, font=title_font)[1]
    footer_height = footer_font_size + footer_padding
    description_height = sum(draw.textsize(line, font=description_font)[1] for line in description_lines)

    available_height = image_height - title_height - footer_height - 6 * title_padding

    if description_height > available_height:
        description_font_size = int(description_font_size * available_height / description_height)
        description_font = ImageFont.truetype('assets/Metropolis-Regular.otf', description_font_size)

    description_start_y = title_height + 3 * title_padding

    title_x = title_padding
    title_y = title_padding
    title_width, title_height = draw.textsize(title, font=title_font)

    title_background_color = (50, 50, 50)
    rectangle_padding = int(image_width * 0.03)
    rectangle_x1 = title_x - rectangle_padding
    rectangle_y1 = title_y - rectangle_padding
    rectangle_x2 = title_x + title_width + rectangle_padding
    rectangle_y2 = title_y + title_height + rectangle_padding

    title_background_color = (50, 50, 50)
    draw.rounded_rectangle(
        [(rectangle_x1, rectangle_y1), (rectangle_x2, rectangle_y2)],
        fill=title_background_color,
        radius=corner_radius
    )

    draw.text((title_x, title_y), title, font=title_font, fill=colors['text'])

    description_x = title_padding
    description_y = title_height + 3 * title_padding
    description_width = image_width - 2 * title_padding

    description_height = sum(draw.textsize(line, font=description_font)[1] + description_padding for line in description_lines)

    rectangle_padding = int(image_width * 0.025)
    rectangle_x1 = description_x - rectangle_padding
    rectangle_y1 = description_y - rectangle_padding
    rectangle_x2 = description_x + description_width + rectangle_padding
    rectangle_y2 = description_y + description_height + rectangle_padding

    description_background_color = (50, 50, 50)
    draw.rounded_rectangle(
        [(rectangle_x1, rectangle_y1), (rectangle_x2, rectangle_y2)],
        fill=description_background_color,
        radius=corner_radius
    )

    for line in description_lines:
        draw.text((description_x, description_start_y), line, font=description_font, fill=colors['text'])
        description_start_y += draw.textsize(line, font=description_font)[1] + description_padding

    footer_x = title_padding
    footer_y = image_height - footer_height - footer_padding
    footer_width = image_width - 2 * title_padding
    footer_text_height = draw.textsize(footer, font=footer_font)[1]

    rectangle_padding = int(image_width * 0.03)
    rectangle_x1 = footer_x - rectangle_padding
    rectangle_y1 = footer_y - rectangle_padding
    rectangle_x2 = footer_x + footer_width + rectangle_padding
    rectangle_y2 = footer_y + footer_text_height + rectangle_padding
    
    footer_background_color = (50, 50, 50)
    draw.rounded_rectangle(
        [(rectangle_x1, rectangle_y1), (rectangle_x2, rectangle_y2)],
        fill=footer_background_color,
        radius=corner_radius
    )

    draw.text((footer_x, footer_y), footer, font=footer_font, fill=colors['text'])

    mask = Image.new('L', image.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle((0, 0, image_width, image_height), fill=255, radius=corner_radius)
    image.putalpha(mask)
    image_bytes = BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    return image_bytes

def spotifhelp():
    url = "https://discord.com/api/v9/users/@me/connections"
    r = requests.get(url, headers={"Authorization": cfg.token})
    response = r.json()
    spotify_access_token = None
    id = None
    for connection in response:
        if connection['type'] == 'spotify':
            spotify_access_token = connection['access_token']
            break
    url = "https://api.spotify.com/v1/me/player/devices"
    headers = {
        "Authorization": f"Bearer {spotify_access_token}"
    }
    r = requests.get(url, headers=headers)
    for device in r.json()["devices"]:
        if device["is_active"] == True:
            id = device["id"]
            break
    return id, spotify_access_token

def find_song(song_name):
    url = f"https://api.spotify.com/v1/search?q={song_name}&type=track&limit=1"
    id, auth = spotifhelp()
    if id == None:
        return None
    headers = {
        "Authorization": f"Bearer {auth}"
    }
    r = requests.get(url, headers=headers)
    response = r.json()
    try:
        track_id = response["tracks"]["items"][0]["id"]
        songname = response["tracks"]["items"][0]["name"]
        artist = response["tracks"]["items"][0]["artists"][0]["name"]
        album = response["tracks"]["items"][0]["album"]["name"]
        return track_id, songname, artist, album, auth
    except:
        return None


async def veltSend(ctx, title, description, footer=None):
    cfg.check()
    if footer == None:
        footer = cfg.embed["footer"]
    mode = "image"
    mode = cfg.mode
    if not ctx.guild == None:
        permissions = ctx.channel.permissions_for(ctx.guild.me)
        if not permissions.attach_files:
            mode = "text"
            
    if mode not in ["image", "text"]:
        mode = "image"
    if mode.lower() == "image":
        try:
            image_bytes = generate_image(title, description, footer)
            msg = await ctx.send(file=File(image_bytes, filename="image.png"), delete_after=cfg.delete_after)
            return msg
        except Exception as e:
            logging.error(f"Error sending message: {e}")
    if mode == "text":
        line1 = f"[{title}]"
        line2 = f"{description}"
        line3 = f"[{footer}]"
        msg = await ctx.send(f"```ini\n{line1}\n```\n`{line2}`\n\n```ini\n{line3}\n```", delete_after=cfg.delete_after)
        return msg

# :::    ::: ::::::::::: ::::::::::: :::        
# :+:    :+:     :+:         :+:     :+:        
# +:+    +:+     +:+         +:+     +:+        
# +#+    +:+     +#+         +#+     +#+        
# +#+    +#+     +#+         +#+     +#+        
# #+#    #+#     #+#         #+#     #+#        
#  ########      ###     ########### ########## 

@velt.command(brief="utility")
async def ping(ctx):
    ping = velt.latency.__round__(3)
    ping = round(ping * 1000)
    google = "https://www.google.com"
    discord_api = "https://discord.com/api/v9/gateway"
    r1 = requests.get(google)
    r2 = requests.get(discord_api)
    r1 = r1.elapsed.total_seconds()
    r2 = r2.elapsed.total_seconds()
    r1 = round(r1 * 1000)
    r2 = round(r2 * 1000)
    await veltSend(ctx, "Ping", f"Velt: {ping}ms\nGoogle: {r1}ms\nDiscord API: {r2}ms")


def format_uptime(uptime):
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

@velt.command(brief="utility")
async def uptime(ctx):
    uptime_seconds = int(time.time() - start_time)
    formatted_uptime = format_uptime(uptime_seconds)
    await veltSend(ctx, "Uptime", f"{formatted_uptime}")

@velt.command(brief="utility")
async def info(ctx):
    cmds = len(velt.commands)
    await veltSend(ctx, "Info", f"""Name: {velt.user.name}
ID: {velt.user.id}
Uptime: {format_uptime(int(time.time() - start_time))}
Prefix: {cfg.prefix}
Mode: {cfg.mode}
Commands: {cmds}
""")
    

@velt.command(brief="utility")
async def snipe(ctx, channel_id: int = None):
    if channel_id == None:
        channel_id = ctx.channel.id
    msgs = []
    for msg in deleted_messages:
        if msg["channel"] == channel_id:
            msgs.append(f"Author: {msg['author']}\nContent: {msg['content']}")
    latest = msgs[-1]
    await veltSend(ctx, "Snipe", latest)

@velt.command(brief="utility")
async def snipeall(ctx, channel_id: int = None):
    if channel_id == None:
        channel_id = ctx.channel.id
    msgs = []
    for msg in deleted_messages:
        if msg["channel"] == channel_id:
            msgs.append(f"Author: {msg['author']}\nContent: {msg['content']}")
    if msgs:
        await veltSend(ctx, "Snipe", "\n\n".join(msgs))
            

# :::::::::   ::::::::  ::::::::::: 
# :+:    :+: :+:    :+:     :+:     
# +:+    +:+ +:+    +:+     +:+     
# +#++:++#+  +#+    +:+     +#+     
# +#+    +#+ +#+    +#+     +#+     
# #+#    #+# #+#    #+#     #+#     
# #########   ########      ###     


@velt.command(brief="bot")
async def prefix(ctx, prefix):
    cfg.setk("prefix", prefix)
    await veltSend(ctx, "Prefix", f"Prefix set to {prefix}")


@velt.command(brief="bot")
async def textmode(ctx):
    cfg.setk("mode", "text")
    await veltSend(ctx, "Textmode", "Mode set to text")


@velt.command(brief="bot")
async def imagemode(ctx):
    cfg.setk("mode", "image")
    await veltSend(ctx, "Imagemode", "Mode set to image")


@velt.command(brief="bot")
async def restart(ctx):
    await ctx.message.delete()
    os.execv(sys.executable, ['python'] + sys.argv)

@velt.command(brief="bot")
async def config(ctx, key_path, value):
    cfg.setk(key_path, value)
    await veltSend(ctx, "Config", f"Set {key_path} to {value}")
    cfg.check()
    

# :::::::::: :::    ::: ::::    ::: 
# :+:        :+:    :+: :+:+:   :+: 
# +:+        +:+    +:+ :+:+:+  +:+ 
# :#::+::#   +#+    +:+ +#+ +:+ +#+ 
# +#+        +#+    +#+ +#+  +#+#+# 
# #+#        #+#    #+# #+#   #+#+# 
# ###         ########  ###    #### 


@velt.command(brief="fun")
async def iq(ctx, user: discord.User):
    iq = random.randint(40, 160)
    await veltSend(ctx, "IQ", f"{user.name} has an IQ of {iq}")


@velt.command(brief="fun")
async def dick(ctx, user: discord.User):
    size = random.randint(1,12)
    pp = "8" + "=" * size + "D"
    await veltSend(ctx, "dick", f"{user.name}'s dick is {size} inches long\n{pp}")

@velt.command(brief="fun")
async def cat(ctx):
    url = "https://api.thecatapi.com/v1/images/search"
    keys = ["live_34iyZhLvb3QtsUMXR7fQBHZeZlwqmAo9CqUrrXOwsgXL75vXGgY8HESwCzm1NYXz", "live_Jzh4OOisuIePhKMvWRG4lsAAzh5jYHZSRqdOwxpWUVYYvaz19BchYbubwudQGUof"]
    headers = {
        "x-api-key": random.choice(keys)
    }
    r = requests.get(url, headers=headers)
    await ctx.send(r.json()[0]["url"])

@velt.command(brief="fun")
async def dog(ctx):
    url = "https://api.thedogapi.com/v1/images/search"
    keys = ["live_yL41nnFF0U8TtCuyMemFxKWWMnejHRXL9PDt1coakRYqhooZWtXXHPpVZlNEqVUC"]
    headers = {
        "x-api-key": random.choice(keys)
    }
    r = requests.get(url, headers=headers)
    await ctx.send(r.json()[0]["url"])

#  ::::::::  :::::::::   ::::::::  ::::::::::: ::::::::::: :::::::::: :::   ::: 
# :+:    :+: :+:    :+: :+:    :+:     :+:         :+:     :+:        :+:   :+: 
# +:+        +:+    +:+ +:+    +:+     +:+         +:+     +:+         +:+ +:+  
# +#++:++#++ +#++:++#+  +#+    +:+     +#+         +#+     :#::+::#     +#++:   
#        +#+ +#+        +#+    +#+     +#+         +#+     +#+           +#+    
# #+#    #+# #+#        #+#    #+#     #+#         #+#     #+#           #+#    
#  ########  ###         ########      ###     ########### ###           ###    


@velt.command(brief="spotify")
async def resume(ctx):
    id, token = spotifhelp()
    if id == None:
        await veltSend(ctx, "spotify", "Auth token expired, try again later.")
        return
    url = f"https://api.spotify.com/v1/me/player/play?device_id={id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.put(url, headers=headers)
    if r.status_code == 204:
        await veltSend(ctx, "spotify", "Resumed")
    else:
        await veltSend(ctx, "spotify", "Error")

@velt.command(brief="spotify")
async def pause(ctx):
    id, token = spotifhelp()
    if id == None:
        await veltSend(ctx, "spotify", "Auth token expired, try again later.")
        return
    url = f"https://api.spotify.com/v1/me/player/pause?device_id={id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.put(url, headers=headers)
    if r.status_code == 204:
        await veltSend(ctx, "spotify", "Paused")
    else:
        await veltSend(ctx, "spotify", "Error")

@velt.command(brief="spotify", aliases=["vol"])
async def volume(ctx, vol: int):
    id, token = spotifhelp()
    if id == None:
        await veltSend(ctx, "spotify", "Auth token expired, try again later.")
        return
    url = f"https://api.spotify.com/v1/me/player/volume?volume_percent={vol}&device_id={id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.put(url, headers=headers)
    if r.status_code == 204:
        await veltSend(ctx, "spotify", f"Volume set to {vol}")
    else:
        await veltSend(ctx, "spotify", "Error")

@velt.command(brief="spotify", aliases=["skip"])
async def next(ctx):
    id, token = spotifhelp()
    if id == None:
        await veltSend(ctx, "spotify", "Auth token expired, try again later.")
        return
    url = f"https://api.spotify.com/v1/me/player/next?device_id={id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.post(url, headers=headers)
    if r.status_code == 204:
        await veltSend(ctx, "spotify", "Playing next song")
    else:
        await veltSend(ctx, "spotify", "Error")

@velt.command(brief="spotify")
async def previous(ctx):
    id, token = spotifhelp()
    if id == None:
        await veltSend(ctx, "spotify", "Auth token expired, try again later.")
        return
    url = f"https://api.spotify.com/v1/me/player/previous?device_id={id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.post(url, headers=headers)
    if r.status_code == 204:
        await veltSend(ctx, "spotify", "Playing previous song")
    else:
        await veltSend(ctx, "spotify", "Error")

@velt.command(brief="spotify")
async def shuffle(ctx):
    global state
    state = not state
    id, token = spotifhelp()
    if id == None:
        await veltSend(ctx, "spotify", "Auth token expired, try again later.")
        return
    url = f"https://api.spotify.com/v1/me/player/shuffle?state={state}&device_id={id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.put(url, headers=headers)
    if r.status_code == 204:
        await veltSend(ctx, "spotify", f"Shuffle set to {state}")
    else:
        await veltSend(ctx, "spotify", "Error")

@velt.command(brief="spotify")
async def nowplaying(ctx):
    id, token = spotifhelp()
    if id == None:
        await veltSend(ctx, "spotify", "Auth token expired, try again later.")
        return
    url = f"https://api.spotify.com/v1/me/player/currently-playing?device_id={id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        response = r.json()
        artist = response["item"]["artists"][0]["name"]
        song = response["item"]["name"]
        await veltSend(ctx, "spotify", f"Artist: {artist}\nSong: {song}")
    else:
        await veltSend(ctx, "spotify", "Error")

@velt.command(brief="spotify")
async def play(ctx, *, song):
    id, token = spotifhelp()
    if id == None:
        await veltSend(ctx, "spotify", "Auth token expired, try again later.")
        return

    # Check if song is a Spotify URL
    spotify_url_pattern = r"https?://open\.spotify\.com/(track|playlist|album)/([a-zA-Z0-9]+)"
    match = re.match(spotify_url_pattern, song)
    if match:
        spotify_type, spotify_id = match.groups()
        if spotify_type == "track":
            url = f"https://api.spotify.com/v1/me/player/play?device_id={id}"
            headers = {"Authorization": f"Bearer {token}"}
            data = {"uris": [f"spotify:track:{spotify_id}"]}
            r = requests.put(url, headers=headers, json=data)
            if r.status_code == 204:
                await veltSend(ctx, "spotify", f"Playing song from link")
            else:
                await veltSend(ctx, "spotify", "Error")
        elif spotify_type == "playlist":
            url = f"https://api.spotify.com/v1/me/player/play?device_id={id}"
            headers = {"Authorization": f"Bearer {token}"}
            playlist_id = re.search(r"https?://open\.spotify\.com/playlist/([a-zA-Z0-9]+)", song).group(1)
            data = {"context_uri": f"spotify:playlist:{playlist_id}"}
            r = requests.put(url, headers=headers, json=data)
            if r.status_code == 204:
                await veltSend(ctx, "spotify", f"Playing playlist")
            else:
                await veltSend(ctx, "spotify", "Error")
            pass
        elif spotify_type == "album":
            url = f"https://api.spotify.com/v1/me/player/play?device_id={id}"
            headers = {"Authorization": f"Bearer {token}"}
            album_id = re.search(r"https?://open\.spotify\.com/album/([a-zA-Z0-9]+)", song).group(1)
            data = {"context_uri": f"spotify:album:{album_id}"}
            r = requests.put(url, headers=headers, json=data)
            if r.status_code == 204:
                await veltSend(ctx, "spotify", f"Playing album")
            else:
                await veltSend(ctx, "spotify", "Error")
            pass
    else:
        track_id, songname, artist, album, auth = find_song(song)
        if track_id == None:
            await veltSend(ctx, "spotify", "Song not found")
            return
        url = f"https://api.spotify.com/v1/me/player/play?device_id={id}"
        headers = {"Authorization": f"Bearer {auth}"}
        data = {"uris": [f"spotify:track:{track_id}"]}
        r = requests.put(url, headers=headers, json=data)
        if r.status_code == 204:
            await veltSend(ctx, "spotify", f"Playing {songname} by {artist}")
        else:
            await veltSend(ctx, "spotify", "Error")

@velt.command(brief="spotify")
async def ssearch(ctx, *, song):
    id, token = spotifhelp()
    if id == None:
        await veltSend(ctx, "spotify", "Auth token expired, try again later.")
        return
    url = f"https://api.spotify.com/v1/search?q={song}&type=track&limit=5"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        response = r.json()
        tracks = response["tracks"]["items"]
        songs = []
        for track in tracks:
            songname = track["name"]
            artist = track["artists"][0]["name"]
            songs.append(f"{songname} by {artist}")
        await veltSend(ctx, "spotify", "\n".join(songs))
    else:
        await veltSend(ctx, "spotify", "Error")

@velt.command(brief="spotify")
async def seek(ctx, pos: int):
    id, token = spotifhelp()
    pos = pos * 1000 
    if id == None:
        await veltSend(ctx, "spotify", "Auth token expired, try again later.")
        return
    url = f"https://api.spotify.com/v1/me/player/seek?position_ms={pos}&device_id={id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.put(url, headers=headers)
    if r.status_code == 204:
        await veltSend(ctx, "spotify", f"Seeked to {pos/1000}s")
    else:
        await veltSend(ctx, "spotify", "Error")



#  ::::::::  :::::::::: ::::    ::: 
# :+:    :+: :+:        :+:+:   :+: 
# +:+        +:+        :+:+:+  +:+ 
# :#:        +#++:++#   +#+ +:+ +#+ 
# +#+   +#+# +#+        +#+  +#+#+# 
# #+#    #+# #+#        #+#   #+#+# 
#  ########  ########## ###    #### 


@velt.command(brief="general")
async def search(ctx, query):
    commands = [(command.name, command.description, command.brief) for command in velt.walk_commands() if
                command.brief is not None]
    matches = []
    for name, description, category in commands:
        if query in name or query in description:
            matches.append((name, description, category))
    if matches:
        command_strings = [f"- {name}" for name, description, category in sorted(matches)]
        num_pages = math.ceil(len(command_strings) / 13)
        page = 1
        start_index = (page - 1) * 13
        end_index = start_index + 13
        success_message = "\n".join(command_strings[start_index:end_index])
        success_message += f"\n\nPage {page}/{num_pages}"
        await veltSend(ctx, query, success_message)
    else:
        await veltSend(ctx, query, "No matches found")

# ::::    ::::   ::::::::  :::::::::  
# +:+:+: :+:+:+ :+:    :+: :+:    :+: 
# +:+ +:+:+ +:+ +:+    +:+ +:+    +:+ 
# +#+  +:+  +#+ +#+    +:+ +#+    +:+ 
# +#+       +#+ +#+    +#+ +#+    +#+ 
# #+#       #+# #+#    #+# #+#    #+# 
# ###       ###  ########  #########  

@velt.command(brief="moderation", aliases=["fastclear"])
async def fclear(ctx, channel: discord.TextChannel):
    if not ctx.author.guild_permissions.manage_channels:
        await veltSend(ctx, "fclear", "You do not have permission to manage channels")
        return
    channelpos = channel.position
    new = await channel.clone(reason="fclear")
    await channel.delete(reason="fclear")
    await new.edit(position=channelpos, reason="fclear")

@velt.command(brief="moderation", aliases=["purge"])
async def clear(ctx, amount: int = 100):
    if not ctx.author.guild_permissions.manage_messages:
        await veltSend(ctx, "clear", "You do not have permission to manage messages")
        return
    await ctx.channel.purge(limit=amount)

@velt.command(brief="moderation")
async def kick(ctx, user: discord.Member, *, reason: str = None):
    if not ctx.author.guild_permissions.kick_members:
        await veltSend(ctx, "kick", "You do not have permission to kick members")
        return
    await user.kick(reason=reason)
    await veltSend(ctx, "kick", f"{user.name} has been kicked")

@velt.command(brief="moderation")
async def ban(ctx, user: discord.Member, *, reason: str = None):
    if not ctx.author.guild_permissions.ban_members:
        await veltSend(ctx, "ban", "You do not have permission to ban members")
        return
    await user.ban(reason=reason)
    await veltSend(ctx, "ban", f"{user.name} has been banned")

@velt.command(brief="moderation")
async def mute(ctx, user: discord.Member, *, reason: str = None):
    if not ctx.author.guild_permissions.manage_roles:
        await veltSend(ctx, "mute", "You do not have permission to manage roles")
        return
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False)
    await user.add_roles(role, reason=reason)
    await veltSend(ctx, "mute", f"{user.name} has been muted")

@velt.command(brief="moderation")
async def unmute(ctx, user: discord.Member, *, reason: str = None):
    if not ctx.author.guild_permissions.manage_roles:
        await veltSend(ctx, "unmute", "You do not have permission to manage roles")
        return
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        await veltSend(ctx, "unmute", "This user is not muted")
        return
    await user.remove_roles(role, reason=reason)
    await veltSend(ctx, "unmute", f"{user.name} has been unmuted")


@velt.command()
async def help(ctx, input: str = None, page: int = 1):
    commands = [(command.name, command.description, command.brief) for command in velt.walk_commands() if
                command.brief is not None]
    categories = {}
    for name, description, category in commands:
        category = category.lower() if category is not None else category
        if category not in categories:
            categories[category] = []
        categories[category].append((name, description))

    input = input.lower() if input is not None else input

    if input is None:
        category_strings = []
        for category in categories.keys():
            category_strings.append(f"{category}")
        success_message = "\n".join(category_strings)
        await veltSend(ctx, "Categories", success_message)
    elif input in categories:
        command_strings = [f"{name}" for name, description in sorted(categories[input])]
        num_pages = math.ceil(len(command_strings) / 13)
        if page < 1 or page > num_pages:
            await veltSend(ctx, "Error", "Invalid page number")
            return
        start_index = (page - 1) * 13
        end_index = start_index + 13
        success_message = "\n".join(command_strings[start_index:end_index])
        success_message += f"\n\nPage {page}/{num_pages}"
        await veltSend(ctx, "Commands", success_message)
    else:
        matches = difflib.get_close_matches(input, [command[0] for command in commands])
        if matches:
            command = velt.get_command(matches[0])
            success_message = f"""Command: {command.name}
Aliases: {', '.join(command.aliases) if command.aliases else 'No aliases'}"""
            await veltSend(ctx, "Success", success_message)

@velt.command()
async def test(ctx):
    url = "https://discord.com/api/v9/users/@me/connections"
    r = requests.get(url, headers={"Authorization": cfg.token})
    response = r.json()
    print(response)
    spotify_access_token = None
    for connection in response:
        if connection['type'] == 'spotify':
            spotify_access_token = connection['access_token']
            break
    print(spotify_access_token)
    url = "https://api.spotify.com/v1/me/player/devices"
    headers = {
        "Authorization": f"Bearer {spotify_access_token}"
    }
    r = requests.get(url, headers=headers)
    print(r.text)
    for device in r.json()["devices"]:
        print(device["name"])
        if device["is_active"] == True:
            print(device["id"])
            break

# Monkey patching...
og = discord.utils._get_build_number
async def gbn(session: ClientSession) -> int:  # Thank you Discord-S.C.U.M
    """Fetches client build number"""
    try:
        login_page_request = await session.get('https://discord.com/login', timeout=7)
        login_page = await login_page_request.text()
        build_url = 'https://discord.com/assets/' + re.compile(r'assets/+([a-z0-9\.]+)\.js').findall(login_page)[-2] + '.js'
        build_request = await session.get(build_url, timeout=7)
        build_file = await build_request.text()
        build_index = build_file.find('buildNumber') + 24
        build_number_str = build_file[build_index : build_index + 6]

        if build_number_str.isnumeric():
            return int(build_number_str)
        else:
            # Check for 'Build Number' format
            build_index = build_file.find('Build Number') + 25
            build_number_str = build_file[build_index : build_index + 6]

            if build_number_str.isnumeric():
                return int(build_number_str)
            else:
                return 9999  # Return a default value
    except asyncio.TimeoutError:
        prettyprint('Could not fetch client build number. Falling back to hardcoded value...')
        return 9999
discord.utils._get_build_number = gbn

try:
    cfg.check()
    velt.run(cfg.token, log_handler=None)
except discord.errors.LoginFailure:
    prettyprint("Invalid token. Set it below.")
    cfg.setk("token", input("> "))