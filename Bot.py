import discord
from discord.ext import commands
import ipaddress
import aiohttp
import json
import ipinfo
import asyncio
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from colorama import init, Fore, Style
from tqdm import tqdm
import os
import pyfiglet
import proxycheck
from PIL import Image
from io import BytesIO

BOT_TOKEN = "Bot_token_here"
CHANNEL_ID = "channel_id_here(Remove the quotes or it won't work)"


client = commands.Bot(command_prefix="!") #If you want to use it for yourself only wirte also self_bot = True and in BOT_TOKEN put your account token. It's against discord Tos and I'm not responsible
# for any violation of those
client.remove_command('help')
last_deleted_message = None

# List of commands to be shown in the custom help command
custom_commands = [
    'clear',
    'esnipe',
    'help',
    'kick',
    'ping',
    'quote',
    'snipe',
    'spam',
    'userinfo',
    'vpn.checker',
    'calculate',
    'avatar'
]

# Custom help command
@client.command(name='help')
async def help_command(ctx):
    # Get the bot's latency
    ping = round(client.latency * 1000)

    # Get the number of servers the bot is in
    num_servers = len(client.guilds)

    # Get the total number of commands
    num_commands = len(client.commands)

    # Format the custom help message
    help_message = (
        "```toml\n"  # Start of a code block with TOML syntax highlighting
        f"[title]\n"  
        f"ping = \"{ping}ms\"\n"  
        f"username = \"{ctx.author}\"\n"
        f"creator = \"{ctx.author}\"\n"
        f"commands = \"{num_commands}\"\n"
        f"servers = \"{num_servers}\"\n\n"
        f"[commands]\n"  
    )
    for command in custom_commands:
        help_message += f"{command} = \"\"  \n"  

    help_message += "```"  # End of the code block

    # Send the custom help message
    await ctx.send(help_message)


@client.command(name='calculate')
async def calculate(ctx, *, expression: str):
    try:
        # Evaluate the expression
        result = eval(expression)

        # Format the result message in a codeblock
        result_message = (
            f"```\n"
            f"Calculation\n"
            f"-----------\n"
            f"Expression : {expression}\n"
            f"Result     : {result}\n"
            f"```"
        )

        # Send the result message
        await ctx.send(result_message)
    except Exception as e:
        # Handle any errors that occur during evaluation
        await ctx.send(f"Error in calculation: {e}")

@client.command(name='avatar')
async def avatar(ctx, member: discord.Member):
    # Get the member's avatar URL
    avatar_url = member.avatar.url
    response = requests.get(avatar_url)
    avatar_image = Image.open(BytesIO(response.content))

    # Resize the avatar image (zoomed in)
    size = (256, 256)  # Specify the desired size
    avatar_image = avatar_image.resize(size, Image.Resampling.LANCZOS)

    # Save the image to a BytesIO object
    with BytesIO() as image_binary:
        avatar_image.save(image_binary, 'PNG')
        image_binary.seek(0)
        # Send the image in the chat
        await ctx.send(file=discord.File(fp=image_binary, filename='avatar.png'))
@client.command(name='ping')
async def ping(ctx):
    await ctx.send(f'{round(client.latency * 1000)}ms')

@client.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'Kicked {member.mention} for reason: {reason}')

@client.command(name='spam')
async def spam(ctx, message: str, count: int):
    async def msg():
        headers = {'Authorization': BOT_TOKEN}
        payload = {'content': message}
        async with aiohttp.ClientSession() as session:
            for _ in range(count):
                async with session.post(f'https://discord.com/api/v9/channels/{ctx.channel.id}/messages', headers=headers, json=payload) as response:
                    if response.status != 200:
                        print(f'Failed to send message in {ctx.channel.id}: {response.status} {response.reason}') # Handling any error that could happen

    tasks = [msg() for _ in range(30)]
    await asyncio.gather(*tasks)      

@client.command(name='vpn.checker')
async def vpnchecker(ctx, ip: str):
    api_key = 'Your_api_key'  # Replace with your proxycheck.io key
    url = f'http://proxycheck.io/v2/{ip}?key={api_key}&vpn=1&asn=1&risk=1&port=1'

    # Send a GET request to the proxycheck.io API
    result = requests.get(url)
    response_data = result.json()  # Assuming the response is in JSON format

    # Format the response
    formatted_response = "```toml\n"
    for key, value in response_data.get(ip, {}).items():
        formatted_response += f"{key} = \"{value}\"\n"
    formatted_response += "```"

    # Send the result back to the Discord channel
    await ctx.send(formatted_response)

@client.event
async def on_message_delete(message):
    global last_deleted_message
    # Store the deleted message and its author
    last_deleted_message = (message.content, message.author)

@client.event
async def on_message_edit(before, after):
    global last_edited_message
    # Store the last edited message and its author
    last_edited_message = (before.content, after.content, before.author)   

@client.command(name='snipe')
async def snipe(ctx):
    global last_deleted_message
    if last_deleted_message is None:
        await ctx.send("There's no message to snipe!")
    else:
        content, author = last_deleted_message
        await ctx.send(f"The last deleted message was:\n**{content}**\nSent by: {author.mention}")
        # Clear the stored deleted message after sniping
        last_deleted_message = None

@client.command(name='esnipe')
async def editsnipe(ctx):
    global last_edited_message
    if last_edited_message is None:
        await ctx.send("There's no message to snipe edits!")
    else:
        before_content, after_content, author = last_edited_message
        await ctx.send(
            f"The last edited message was by {author.mention}:\n"
            f"**Original:** {before_content}\n"
            f"**Edited:** {after_content}"
        )
        # Clear the last edited message after sending it
        last_edited_message = None

@client.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f'Cleared {amount} messages.', delete_after=5)

@client.command(name='quote')
async def quote(ctx):
    # Define the function to fetch JSON data from the API
    def fetch_json(url):
        response = requests.get(url)
        return response.json()
    
    # URL for the Forismatic API
    url = "https://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en"
    response_json = fetch_json(url)
    
    # Extract the quote and author
    quote_text = response_json.get('quoteText', 'No quote found')
    author = response_json.get('quoteAuthor', 'Unknown')

    # Send the result in a code block
    await ctx.send(f"```Quote: {quote_text}\nAuthor: {author}```")



@client.command(name='userinfo')
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [role.name for role in member.roles if role.name != '@everyone']
    roles_str = ', '.join(roles) if roles else 'None'
    joined_at = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")
    created_at = member.created_at.strftime("%Y-%m-%d %H:%M:%S")
    await ctx.send(f"```\nUsername: {member}\nID: {member.id}\nJoined Server: {joined_at}\nAccount Created: {created_at}\nRoles: {roles_str}\n```")
client.run(BOT_TOKEN)
