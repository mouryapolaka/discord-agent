import discord
from discord.ext import commands
from functions import *
import os

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def hey(ctx):
    """Says hello"""
    await ctx.send('Hello!')

@bot.command()
async def docs(ctx):
    """Returns list of commands"""
    commands_list = []
    for command in bot.commands:
        if command.callback.__doc__ and command.name != 'help':
            commands_list.append(f'`.{command.name}: {command.callback.__doc__}`')
        elif command.name != 'help':
            commands_list.append(f'`.{command.name}: No description provided`')

    # Sort the commands_list alphabetically by command name
    sorted_commands_list = sorted(commands_list, key=lambda x: x.split(":")[0].lower())
    
    output_message = '\n\n'.join(sorted_commands_list)
    await ctx.send(output_message)

@bot.command()
async def example(ctx):
    """Shows an example of the commands"""
    await ctx.send('Example')

discord_bot_token = os.environ.get('DISCORD_BOT_TOKEN')
bot.run(discord_bot_token)