import pypresence
import requests
import textwrap
import warnings
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
from aiohttp import ClientSession
from colorama import Fore, Style
from discord.ext import commands
from notifypy import Notify
from discord import File
from io import BytesIO

warnings.filterwarnings("ignore", category=DeprecationWarning)

os.system("pip install Pillow==9.4.0")

os.system("cls")

def prettyprint(text):
    print(f"[{Fore.LIGHTMAGENTA_EX}{time.strftime('%H:%M:%S')}{Style.RESET_ALL}] {text}")


class Config:
    def __init__(self):
        self.token = ""
        self.prefix = ""
        self.mode = "image"
        self.delete_after = 15
        self.logging = "console"
        self.rpc = True
        self.notify = True
        self.log = {
            "ghostping": True,
            "ping": True
        }
        self.embed = {
            "image": "",
            "footer": ""
        }

    def check(self):
        if not os.path.exists("config.json") or os.stat("config.json").st_size == 0:
            y = """
{
    "token": "",
    "prefix": "",
    "mode": "image",
    "delete_after": 15,
    "logging": "channel",
    "rpc": true,
    "notify": true,
    "log": {
        "ghostping": true,
        "ping": true
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

    def setk(self, key, value):
        with open("config.json", "r") as f:
            data = json.load(f)
        data[key] = value
        with open("config.json", "w") as f:
            json.dump(data, f, indent=4)

config = Config()
config.check()

class Notif:
    def __init__(self):
        self.title = "Velt"

    def send(self, message):
        if config.notify == True:
            notification = Notify()
            notification.title = self.title
            notification.application_name = self.title
            notification.message = message
            notification.icon = "assets/icon.ico"
            notification.audio = "assets/notif.mp3"
            notification.send()

def downloadAssets():
    assets = [
        "https://raw.githubusercontent.com/VeltBot/assets/main/velt_big.png",
        "https://raw.githubusercontent.com/VeltBot/assets/main/icon.ico",
        "https://raw.githubusercontent.com/VeltBot/assets/main/notif.mp3"
    ]
    for asset in assets:
        name = asset.split("/")[-1]
        os.makedirs('assets', exist_ok=True)
        if not os.path.exists(f"assets/{name}"):
            with open(f"assets/{name}", "wb") as f:
                prettyprint(f"Downloading {name}")
                f.write(requests.get(asset).content)

downloadAssets()

notif = Notif()

velt = commands.Bot(command_prefix=config.prefix, self_bot=True, chunk_guilds_at_startup=False, request_guilds=False, help_command=None)

@velt.event
async def on_ready():
    os.system("title Velt")
    notif.send("Logged in")
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
    url = "https://discord.com/api/v10/users/@me/relationships"
    r = requests.get(url, headers={"Authorization": config.token})
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
[-] Prefix: {Fore.LIGHTMAGENTA_EX}{config.prefix}{Style.RESET_ALL}
[-] Started at: {Fore.LIGHTMAGENTA_EX}{time.strftime('%H:%M:%S')}{Style.RESET_ALL}
""".replace("[-]", f"[{Fore.LIGHTMAGENTA_EX}-{Style.RESET_ALL}]")
    start_time = time.time()
    print(Fore.LIGHTMAGENTA_EX)
    print(pystyle.Center.XCenter(banner))
    print(Style.RESET_ALL)
    print(zamn)
    cmds = len(velt.commands)
    rpc = pypresence.AioPresence("1185652637966811146")
    await rpc.connect()
    prettyprint("RPC connected")
    await rpc.update(details=str(cmds) + " commands", large_image="velt", large_text="Velt", start=start_time)
    prettyprint(f"Logged in as {velt.user.name} ({Fore.LIGHTMAGENTA_EX}{velt.user.id}{Style.RESET_ALL})")

@velt.event
async def on_command(ctx):
    global rpc
    last_command = ctx.message.content[1:].split(" ")[0]
    await rpc.update(state="Last command used: " + last_command, details=str(len(velt.commands)) + " commands", large_image="velt", large_text="Velt", start=start_time)
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
    if config.logging == "console":
        prettyprint(f"{error}")
    elif config.logging == "channel":
        await veltSend(ctx, "Error", f"{error}")

@velt.event
async def on_message_delete(message):
    if config.log["ghostping"] == True:
        if message.mentions:
            if message.mentions.__contains__(velt.user):
                prettyprint(f"{message.author.name} ghost pinged you in {message.guild.name} ({message.guild.id})")
                notif.send(f"{message.author.name} ghost pinged you in {message.guild.name} ({message.guild.id})")

@velt.event
async def on_message(message):
    if config.log["ping"] == True:
        if message.mentions:
            if message.mentions.__contains__(velt.user):
                prettyprint(f"{message.author.name} pinged you in {message.guild.name} ({message.guild.id})")
                notif.send(f"{message.author.name} pinged you in {message.guild.name} ({message.guild.id})")
    await velt.process_commands(message)


def generate_image(title, description, footer):
    colors = {
        'text': (255, 255, 255),
        'background': (25, 25, 25),
        'primary': (255,188,207),
        'secondary': (10, 10, 10),
        'accent': (158, 41, 74)
    }

    image_width = 600
    image_height = 800
    title_padding = 45
    description_padding = 7.5  # reduced padding between lines
    footer_padding = 20
    corner_radius = 50
    border_width = 5

    image = Image.new('RGB', (image_width, image_height), colors['background'])
    draw = ImageDraw.Draw(image)

    #small_image = Image.open(requests.get(config.embed["image"], stream=True).raw)
    #small_image = small_image.resize((int(image_width * 0.2), int(image_width * 0.2)))

    #mask = Image.new('L', small_image.size, 0)
    #draw_mask = ImageDraw.Draw(mask)
    #draw_mask.ellipse((0, 0) + small_image.size, fill=255)

    #small_image = ImageOps.fit(small_image, mask.size, centering=(0.5, 0.5))
    #small_image.putalpha(mask)

    #image.paste(small_image, (image_width - small_image.size[0] - 25, 15), small_image)

    title_font_size = int(image_width * 0.089)
    title_font = ImageFont.truetype(f'Metropolis-Bold.otf', title_font_size)

    description_font_size = int(image_width * 0.0525)
    description_font = ImageFont.truetype(f'Metropolis-Regular.otf', description_font_size)

    footer_font_size = int(image_width * 0.05)
    footer_font = ImageFont.truetype(f'Metropolis-Regular.otf', footer_font_size)

    description_lines = []
    for line in description.split('\n'):
        description_lines.extend(textwrap.wrap(line, width=30))

    title_height = draw.textsize(title, font=title_font)[1]
    footer_height = footer_font_size + footer_padding
    description_height = sum(draw.textsize(line, font=description_font)[1] for line in description_lines)

    available_height = image_height - title_height - footer_height - 6 * title_padding

    if description_height > available_height:
        description_font_size = int(description_font_size * available_height / description_height)
        description_font = ImageFont.truetype('Metropolis-Regular.otf', description_font_size)

    description_start_y = title_height + 3 * title_padding

    title_x = title_padding
    title_y = title_padding
    draw.text((title_x, title_y), title, font=title_font, fill=colors['text'])

    line_y = title_y + title_height + title_padding
    draw.line([(title_x, line_y), (image_width - title_x, line_y)], fill=colors['accent'], width=border_width)

    description_x = title_padding
    for line in description_lines:
        draw.text((description_x, description_start_y), line, font=description_font, fill=colors['text'])
        description_start_y += draw.textsize(line, font=description_font)[1] + description_padding

    footer_box_width = image_width - 2 * title_padding
    footer_box_height = footer_height
    footer_box_x = title_padding
    footer_box_y = image_height - title_padding - footer_box_height

    draw.rounded_rectangle(
        [(footer_box_x, footer_box_y), (footer_box_x + footer_box_width, footer_box_y + footer_box_height)],
        fill=colors['secondary'],
        outline=colors['accent'],
        width=border_width,
        radius=corner_radius
    )

    footer_text_width, footer_text_height = draw.textsize(footer, font=footer_font)
    footer_text_x = footer_box_x + (footer_box_width - footer_text_width) // 2
    footer_text_y = footer_box_y + (footer_box_height - footer_text_height) // 2

    draw.text((footer_text_x, footer_text_y), footer, font=footer_font, fill=colors['text'])

    mask = Image.new('L', image.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle((0, 0, image_width, image_height), fill=255, radius=corner_radius)
    image.putalpha(mask)
    image_bytes = BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    return image_bytes


async def veltSend(ctx, title, description):
    config.check()
    footer = config.embed["footer"]
    mode = "image"
    mode = config.mode
    if mode not in ["image", "text"]:
        mode = "image"
    if mode.lower() == "image":
        try:
            image_bytes = generate_image(title, description, footer)
            msg = await ctx.send(file=File(image_bytes, filename="image.png"), delete_after=config.delete_after)
            return msg
        except Exception as e:
            logging.error(f"Error sending message: {e}")
    if mode == "text":
        line1 = f"[{title}]"
        line2 = f"{description}"
        line3 = f"[{footer}]"
        msg = await ctx.send(f"```ini\n{line1}\n```\n`{line2}`\n\n```ini\n{line3}\n```", delete_after=config.delete_after)
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
    discord_api = "https://discord.com/api/v10/gateway"
    r1 = requests.get(google)
    r2 = requests.get(discord_api)
    r1 = r1.elapsed.total_seconds()
    r2 = r2.elapsed.total_seconds()
    r1 = round(r1 * 1000)
    r2 = round(r2 * 1000)
    await veltSend(ctx, "Ping", f"> Velt: {ping}ms\n> Google: {r1}ms\n> Discord API: {r2}ms")


def format_uptime(uptime):
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

@velt.command(brief="utility")
async def uptime(ctx):
    uptime_seconds = int(time.time() - start_time)
    formatted_uptime = format_uptime(uptime_seconds)
    await veltSend(ctx, "Uptime", f"> {formatted_uptime}")

@velt.command(brief="utility")
async def info(ctx):
    cmds = len(velt.commands)
    await veltSend(ctx, "Info", f"""Name: {velt.user.name}
ID: {velt.user.id}
Uptime: {format_uptime(int(time.time() - start_time))}
Prefix: {config.prefix}
Mode: {config.mode}
Commands: {cmds}
""")
    
# :::::::::   ::::::::  ::::::::::: 
# :+:    :+: :+:    :+:     :+:     
# +:+    +:+ +:+    +:+     +:+     
# +#++:++#+  +#+    +:+     +#+     
# +#+    +#+ +#+    +#+     +#+     
# #+#    #+# #+#    #+#     #+#     
# #########   ########      ###     


@velt.command(brief="bot")
async def prefix(ctx, prefix):
    config.setk("prefix", prefix)
    await veltSend(ctx, "Success", f"Prefix set to {prefix}")


@velt.command(brief="bot")
async def textmode(ctx):
    config.setk("mode", "text")
    await veltSend(ctx, "Success", "Mode set to text")


@velt.command(brief="bot")
async def imagemode(ctx):
    config.setk("mode", "image")
    await veltSend(ctx, "Success", "Mode set to image")


@velt.command(brief="bot")
async def restart(ctx):
    await ctx.message.delete()
    os.execv(sys.executable, ['python'] + sys.argv)

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
        command_strings = [f"> - {name}" for name, description, category in sorted(matches)]
        num_pages = math.ceil(len(command_strings) / 13)
        page = 1
        start_index = (page - 1) * 13
        end_index = start_index + 13
        success_message = "\n".join(command_strings[start_index:end_index])
        success_message += f"\n\nPage {page}/{num_pages}"
        await veltSend(ctx, query, success_message)
    else:
        await veltSend(ctx, query, "No matches found")


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
            category_strings.append(f"> {category}")
        success_message = "\n".join(category_strings)
        await veltSend(ctx, "Categories", success_message)
    elif input in categories:
        command_strings = [f"> {name}" for name, description in sorted(categories[input])]
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
> Aliases: {', '.join(command.aliases) if command.aliases else 'No aliases'}"""
            await veltSend(ctx, "Success", success_message)


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
    velt.run(config.token, log_handler=None)
except discord.errors.LoginFailure:
    prettyprint("Invalid token. Set it below.")
    config.setk("token", input("> "))