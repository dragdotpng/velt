import pypresence
import threading
import requests
import textwrap
import warnings
import datetime
import secrets
import asyncio
import difflib
import logging
import discord
import pystyle
import random
import base64
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
from colorama import Fore, Style
from discord.ext import commands
from discord import File
from io import BytesIO

warnings.filterwarnings("ignore", category=DeprecationWarning)

#negawat?
#os.system("pip install Pillow==9.4.0")

def prettyprint(text):
    print(f"[{Fore.LIGHTMAGENTA_EX}{time.strftime('%H:%M:%S')}{Style.RESET_ALL}] {text}")

def cls():
    os.system("cls") if os.name == "nt" else os.system("clear")

cls()

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
        self.protection = {
            "gc": False,
            "delallmessages": False
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
            ex = """
@velt.command()
async def yee(ctx):
    await ctx.send("yuh")"""
            with open("scripts/example.py", "w") as f:
                f.write(ex)
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
    "protection": {
        "gc": false,
        "delallmessages": false
    },
    "rpc": {
        "enabled": true,
        "id": "1185652637966811146",
        "state": "best!?",
        "name": "Velt",
        "details": null,
        "large_image": "velt",
        "large_text": "Velt",
        "small_image": null,
        "small_text": null,
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

    async def send(self, message, on_click=None):
        if cfg.notify == True:
            if os.name == "nt":
                await toast(title=self.title, body=message, icon=os.path.abspath("assets/velt_big.png"), audio=os.path.abspath("assets/notif.wav"), app_id="Velt", on_dismissed=lambda reason: None, on_click=on_click)
            else:
                playsound.playsound(os.path.abspath("assets/notif.wav"), block=False)
                notification(summary=self.title, message=message, timeout=5000, app_name="Velt", image=os.path.abspath("assets/velt_big.png"))
                

def downloadAssets():
    assets = [
        "https://raw.githubusercontent.com/VeltBot/assets/main/velt_big.png",
        "https://raw.githubusercontent.com/VeltBot/assets/main/icon.ico",
        "https://raw.githubusercontent.com/VeltBot/assets/main/notif.wav",
        "https://raw.githubusercontent.com/VeltBot/assets/main/Metropolis-Regular.otf",
        "https://raw.githubusercontent.com/VeltBot/assets/main/Metropolis-Bold.otf",
        "https://raw.githubusercontent.com/VeltBot/assets/main/Metropolis-SemiBoldItalic.otf"
    ]
    for asset in assets:
        name = asset.split("/")[-1]
        os.makedirs('assets', exist_ok=True)
        if not os.path.exists(f"assets/{name}"):
            with open(f"assets/{name}", "wb") as f:
                prettyprint(f"Downloading {name}")
                f.write(requests.get(asset).content)

async def loadscripts():
    for scriptf in os.listdir("scripts"):
        if scriptf.endswith(".py"):
            with open(f"scripts/{scriptf}") as f:
                script_code = f.read()
            exec(script_code)
            prettyprint(f"Loaded scripts.{scriptf[:-3]}")
    cls()

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
    if cfg.rpc["enabled"] == True:
        rpc = pypresence.AioPresence(1185652637966811146)
        buttons = cfg.rpc["buttons"]
        await rpc.connect()
        prettyprint("RPC connected")
        await rpc.update(state=cfg.rpc["state"], details=cfg.rpc["details"], large_image=cfg.rpc["large_image"], large_text=cfg.rpc["large_text"], start=start_time, buttons=buttons)
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

def goto_message(message_id, channel_id, guild_id=None):
    if os.name == "nt":
        if guild_id == None:
            url = f"discord://-/channels/@me/{channel_id}/{message_id}"
        else:
            url = f"discord://-/channels/{guild_id}/{channel_id}/{message_id}"
        os.system("explorer.exe " + url)
    else:
        pass # Fire code
    

@velt.event
async def on_message_delete(message):
    if cfg.log["ghostping"] == True:
        if message.mentions:
            if message.mentions.__contains__(velt.user):
                if message.author == velt.user:
                    return
                prettyprint(f"{message.author.name} ghost pinged you in {message.guild.name} ({message.guild.id})")
                asyncio.create_task(notif.send(f"{message.author.name} ghost pinged you in {message.guild.name} ({message.guild.id})", lambda *args: goto_message(message.id, message.channel.id, message.guild.id)))

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
    if cfg.protection["delallmessages"] == True:
        if message.author == velt.user:
            asyncio.sleep(cfg.delete_after)
            await message.delete()
    if cfg.log["ping"] == True:
        if message.mentions:
            if message.mentions.__contains__(velt.user):
                if message.author == velt.user:
                    return
                prettyprint(f"{message.author.name} pinged you in {message.guild.name} ({message.guild.id})")
                asyncio.create_task(notif.send(f"{message.author.name} pinged you in {message.guild.name} ({message.guild.id})", lambda *args: goto_message(message.id, message.channel.id, message.guild.id)))
    await velt.process_commands(message)

@velt.event
async def on_group_join(channel, user):
    if cfg.protection["gc"] == True:
        if user == velt.user:
            prettyprint(f"Protection: Left group ({channel.id})")
            await channel.leave()

@velt.event
async def on_private_channel_create(channel):
    if cfg.protection["gc"] == True:
        if channel.type == discord.ChannelType.group:
            if channel.owner == velt.user:
                pass
            else:
                prettyprint(f"Protection: Left group ({channel.id})")
                await channel.leave()


def generate_image(title, description, footer):
    def round_rectangle(draw, xy, corner_radius, fill=None, outline=None):
        upper_left_point = xy[0]
        bottom_right_point = xy[1]
        draw.rectangle(
            [
                (upper_left_point[0], upper_left_point[1] + corner_radius),
                (bottom_right_point[0], bottom_right_point[1] - corner_radius)
            ],
            fill=fill,
            outline=fill
        )
        draw.rectangle(
            [
                (upper_left_point[0] + corner_radius, upper_left_point[1]),
                (bottom_right_point[0] - corner_radius, bottom_right_point[1])
            ],
            fill=fill,
            outline=fill
        )
        draw.pieslice(
            [upper_left_point, (upper_left_point[0] + corner_radius * 2, upper_left_point[1] + corner_radius * 2)],
            180,
            270,
            fill=fill,
            outline=fill
        )
        draw.pieslice(
            [(bottom_right_point[0] - corner_radius * 2, bottom_right_point[1] - corner_radius * 2), bottom_right_point],
            0,
            90,
            fill=fill,
            outline=fill
        )
        draw.pieslice(
            [(upper_left_point[0], bottom_right_point[1] - corner_radius * 2), (upper_left_point[0] + corner_radius * 2, bottom_right_point[1])],
            90,
            180,
            fill=fill,
            outline=fill
        )
        draw.pieslice(
            [(bottom_right_point[0] - corner_radius * 2, upper_left_point[1]), (bottom_right_point[0], upper_left_point[1] + corner_radius * 2)],
            270,
            360,
            fill=fill,
            outline=fill
        )

    title_font = ImageFont.truetype("assets/Metropolis-Bold.otf", 40)
    description_font = ImageFont.truetype("assets/Metropolis-Regular.otf", 30)
    footer_font = ImageFont.truetype("assets/Metropolis-SemiBoldItalic.otf", 25)

    def draw_wrapped_text(image, draw, font, text, pos, col):
        margin, offset = pos
        max_width = image.width - 2*margin
        lines = []

        paragraphs = text.split("\n")

        for paragraph in paragraphs:
            words = paragraph.split(' ')

            current_line = words.pop(0)

            for word in words:
                if draw.textlength(' '.join([current_line, word]), font=font) <= max_width:
                    current_line = ' '.join([current_line, word])
                else:
                    lines.append(current_line)
                    current_line = word

            lines.append(current_line)

        for line in lines:
            draw.text((margin, offset), line, font=font, fill=col)
            left, top, right, bottom = font.getbbox("line")
            _, height = right - left, bottom - top
            offset += height + 10

        return image

    def draw_title(draw, text):
        draw_wrapped_text(image, draw, title_font, text, (20, 20), "white")

    def draw_description(draw, text):
        draw_wrapped_text(image, draw, description_font, text, (20, 100), "white")

    def draw_footer(draw, text):
        draw_wrapped_text(image, draw, footer_font, text, (20, 470), "grey")

    def draw_line(draw, color, xy):
        draw.line(
            xy,
            fill=color,
            width=8
        )
    
    image = Image.new("RGB", (600, 500), (32, 34, 37))
    draw = ImageDraw.Draw(image)
    #round_rectangle(draw, [(15, 65), (550, 450)], 20, fill=(54, 57, 63)) spent so long and it looks ass xddd
    draw_title(draw, title)
    draw_description(draw, description)
    draw_footer(draw, footer)
    draw_line(draw, "purple", [(0, 0), (0, 500)])
    image_bytes = BytesIO()
    image.save(image_bytes, format="PNG")
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
    try:
        for device in r.json()["devices"]:
            if device["is_active"] == True:
                id = device["id"]
                break
    except:
        return None, None
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
    footer = cfg.embed["footer"] + " | " + footer if footer != None else cfg.embed["footer"]
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
        msg = await ctx.send(f"""```ini\n{line1}\n```\n`{line2}`\n\n```ini\n{line3}\n```""", delete_after=cfg.delete_after)
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
async def snipe(ctx, channel_id: int = None, page: int = None):
    global deleted_messages
    if channel_id == None:
        channel_id = ctx.channel.id
    msgs = []
    for msg in deleted_messages:
        if msg["channel"] == channel_id:
            msgs.append(f"Author: {msg['author']}\nContent: {msg['content']}")
    latest = msgs[-1]
    await veltSend(ctx, "Snipe", latest)

@velt.command(brief="utility")
async def snipeall(ctx, channel_id: int = None, page: int = 1):
    global deleted_messages
    if channel_id == None:
        channel_id = ctx.channel.id
    msgs = []
    for msg in deleted_messages:
        if msg["channel"] == channel_id:
            msgs.append(f"Author: {msg['author']}\nContent: {msg['content']}")
    num_pages = math.ceil(len(msgs) / 13)
    if page > num_pages or page < 1:
        await veltSend(ctx, "Snipe", "Invalid page number")
        return
    start_index = (page - 1) * 13
    end_index = start_index + 13
    snipeall_message = "\n\n".join(msgs[start_index:end_index])
    await veltSend(ctx, "Snipe", snipeall_message, f"Page {page}/{num_pages}")

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
async def config(ctx, key_path = None, value = None):
    if key_path == None:
        # send config without token
        data = cfg.get()
        data = json.dumps(data, indent=4)
        data = data.replace(cfg.token, "You not get")
        await ctx.send(f"# Config\n```json\n{data}\n```")
        return
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


@velt.command(brief="fun", aliases=["penis"])
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
async def tts(ctx, *, text):
    headers = {
        'Content-Type': 'application/json',
    }

    json_data = {
        'text': text,
        'voice': 'en_us_001',
    }

    response = requests.post('https://tiktok-tts.weilnet.workers.dev/api/generation', headers=headers, json=json_data)
    data = response.json()
    audio = data['data']
    audio = base64.b64decode(audio)
    filename = secrets.token_hex(16) + ".mp3"
    with open(filename, 'wb') as f:
        f.write(audio)
    await ctx.send(file=discord.File(filename))
    os.remove(filename)

@velt.command(brief="fun")
async def quote(ctx):
    url = "https://inspirobot.me/api?generate=true"
    r = requests.get(url)
    await ctx.send(r.text)

@velt.command(brief="fun")
async def dog(ctx):
    url = "https://api.thedogapi.com/v1/images/search"
    keys = ["live_yL41nnFF0U8TtCuyMemFxKWWMnejHRXL9PDt1coakRYqhooZWtXXHPpVZlNEqVUC"]
    headers = {
        "x-api-key": random.choice(keys)
    }
    r = requests.get(url, headers=headers)
    await ctx.send(r.json()[0]["url"])

@velt.command(brief="fun")
async def catfact(ctx):
    url = "https://catfact.ninja/fact"
    r = requests.get(url)
    await veltSend(ctx, "catfact", r.json()["fact"])

@velt.command(brief="fun")
async def dogfact(ctx):
    url = "https://dogapi.dog/api/v2/facts"
    r = requests.get(url)
    await veltSend(ctx, "dogfact", r.json()["data"][0]["attributes"]["body"])

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
        await veltSend(ctx, query, success_message, f"Page {page}/{num_pages}")
    else:
        await veltSend(ctx, query, "No matches found")


# ::::    ::::   ::::::::  :::::::::  
# +:+:+: :+:+:+ :+:    :+: :+:    :+: 
# +:+ +:+:+ +:+ +:+    +:+ +:+    +:+ 
# +#+  +:+  +#+ +#+    +:+ +#+    +:+ 
# +#+       +#+ +#+    +#+ +#+    +#+ 
# #+#       #+# #+#    #+# #+#    #+# 
# ###       ###  ########  #########  
        

@velt.command(brief="moderation", aliases=["fastclear", "fc"])
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

@velt.command(brief="moderation", aliases=["spurge", "sp"])
async def selfpurge(ctx, amount: int = 15):
    messages = []
    amount = amount + 1
    async for message in ctx.channel.history(limit=amount):
        if message.author == velt.user:
            messages.append(message)
        else:
            amount += 1
    # check if channel is not groupchannel
    if ctx.channel.type == discord.ChannelType.group:
        for message in messages:
            await message.delete(delay=0.5)
    else:
        await ctx.channel.purge(limit=amount, check=lambda m: m.author == velt.user, delay=0.5)

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
async def unban(ctx, user: discord.User):
    if not ctx.author.guild_permissions.ban_members:
        await veltSend(ctx, "unban", "You do not have permission to ban members")
        return
    await ctx.guild.unban(user)
    await veltSend(ctx, "unban", f"{user.name} has been unbanned")

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
    cmds = len(velt.commands)
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
        await veltSend(ctx, "Categories", success_message, f"{cmds} commands")
    elif input in categories:
        command_strings = [f"{name}" for name, description in sorted(categories[input])]
        num_pages = math.ceil(len(command_strings) / 13)
        if page < 1 or page > num_pages:
            await veltSend(ctx, "Error", "Invalid page number")
            return
        start_index = (page - 1) * 13
        end_index = start_index + 13
        success_message = "\n".join(command_strings[start_index:end_index])
        await veltSend(ctx, "Commands", success_message, f"Page {page}/{num_pages}")
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

try:
    cfg.check()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(loadscripts())
    velt.run(cfg.token, log_handler=None)
except discord.errors.LoginFailure:
    prettyprint("Invalid token. Set it below.")
    cfg.setk("token", input("> "))