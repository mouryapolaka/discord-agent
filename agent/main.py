import discord
from discord.ext import commands, tasks
from functions import *
import json
from datetime import datetime
from llm import LLM
import os
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

model = LLM('')

with open("settings.json", "r") as file:
    settings = json.load(file)

channel_id = os.environ.get("CHANNEL_ID")
bot_token = os.environ.get("BOT_TOKEN")

bot = commands.Bot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    check_reminders.start()

@bot.command()
async def getstarted(ctx):
    """Sends the intro message"""
    await ctx.send("Hello! I am your personal chatbot. I am here to help you with your queries. \nYou can ask me anything and I will try my best to answer your questions. \n\nTo get started, type `.docs` to see the list of available commands. \nYou can also type `.docs <command>` to see the detailed description of a specific command. \nHowever, it would be best if you could provide me with some information about yourself. \nFor example `.config name <yourname>` \n\nTo start a natural conversation, make sure to set or update your LLM token. You can do this by typing \n`.config llm_token <token>` \n")

@bot.command()
async def hey(ctx):
    """Says hello"""
    await ctx.send('Hello!')

@bot.command()
async def docs(ctx, command_name: str = None):
    """Returns list of commands or detailed description of a specific command."""
    if command_name:
        # Check if the specified command exists
        command = bot.get_command(command_name)
        if command and command.callback.__doc__:
            await ctx.send(f"`.{command_name}` command: {command.callback.__doc__.strip()}")
        else:
            await ctx.send(f"Command `{command_name}` not found or no description provided.")
    else:
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
async def example(ctx, command_name=None):
    """
    Shows an example of the specified command. If no command is specified, 
    provides examples for all available commands.
    """
    if command_name:
        # Check if the specified command exists
        command = bot.get_command(command_name)
        if command and command.callback.__doc__:
            await ctx.send(f"Example for `{command_name}` command: {command.callback.__doc__.strip()}")
        else:
            await ctx.send(f"Command `{command_name}` not found or no example provided.")
    else:
        # Get examples for all available commands
        examples = []
        for command in bot.commands:
            if command.callback.__doc__ and command.name != 'example':
                examples.append(f"**.{command.name}:** {command.callback.__doc__.strip()}")
        
        examples_message = "\n".join(examples)
        await ctx.send(f"Examples for available commands:\n{examples_message}")

@bot.command()
async def endchat(ctx):
    """Ends the current conversation"""
    model.memory.clear()
    await ctx.send("Chat ended.")

@bot.command()
async def ping(ctx):
    """Returns the latency of the bot"""
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command()
async def reminder(ctx, description, date, time):
    """
    Sets a reminder with description, date, and time.
    
    Example:
    .reminder "Buy groceries" 2021-01-01 12:00
    """
    
    # Combine date and time into a datetime object
    reminder_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

    # Create a reminder dictionary
    reminder_data = {
        "description": description,
        "datetime": reminder_datetime.strftime("%Y-%m-%d %H:%M"),
        "reminder_sent": False,
    }

    # Load existing reminders from JSON file
    try:
        with open("files/reminders.json", "r") as file:
            reminders = json.load(file)
    except FileNotFoundError:
        reminders = []

    # Add the new reminder to the list
    reminders.append(reminder_data)

    # Save updated reminders to JSON file
    with open("files/reminders.json", "w") as file:
        json.dump(reminders, file)

    await ctx.send(f"Reminder set: {description} on {date} at {time}")

@tasks.loop(seconds=60)
async def check_reminders():
    # Open reminders.json file
    with open("files/reminders.json", "r") as file:
        reminders = json.load(file)

    # Get the current time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    channel = bot.get_channel(channel_id)

    # Load old reminders from old_reminders.json file
    try:
        with open("files/old_reminders.json", "r") as old_file:
            old_reminders = json.load(old_file)
    except FileNotFoundError:
        old_reminders = []

    # Iterate through reminders and check if any of them match the current time
    reminders_to_remove = []
    for reminder in reminders:
        if reminder["datetime"] == current_time and channel:
            try:
                await channel.send(f"Reminder: {reminder['description']}")

                # Move the sent reminder to old_reminders list
                old_reminders.append(reminder)
            except Exception as e:
                print(f"Error sending reminder to channel {channel_id}: {e}")
            reminders_to_remove.append(reminder)

    # Remove sent reminders from reminders list
    for reminder in reminders_to_remove:
        reminders.remove(reminder)

    # Save updated reminders to reminders.json file
    with open("files/reminders.json", "w") as file:
        json.dump(reminders, file)

    # Save sent reminders to old_reminders.json file
    with open("files/old_reminders.json", "w") as old_file:
        json.dump(old_reminders, old_file)

@bot.command()
async def config(ctx, setting_name=None, setting_value=None):
    """
    Set or display configuration settings.
    """
    # Load existing settings from JSON file
    try:
        with open("files/config.json", "r") as file:
            settings = json.load(file)
    except FileNotFoundError:
        settings = {}

    # If setting_name is None, display the list of settings
    if setting_name is None:
        await ctx.send("Current settings:")
        for key, value in settings.items():
            await ctx.send(f"`{key}`: `{value}`")
        return
    
    # If setting_value is None, check if the setting_name exists and return its value
    if setting_value is None:
        if setting_name in settings:
            await ctx.send(f"Setting `{setting_name}` is set to `{settings[setting_name]}`")
        else:
            await ctx.send(f"No setting found for `{setting_name}`")
        return
    
    # Special handling for 'llm_token' setting
    if setting_name == 'llm_token':
        # Check if the provided token is valid
        if validate_llm_token(setting_value):
            settings[setting_name] = setting_value
            # Save updated settings to JSON file
            with open("files/config.json", "w") as file:
                json.dump(settings, file)
            await ctx.send(f"Token validated. Setting updated.")
        else:
            await ctx.send("Invalid token. Please enter a valid token.")
    else:
        # For other settings, directly update the dictionary and JSON file
        settings[setting_name] = setting_value
        # Save updated settings to JSON file
        with open("files/config.json", "w") as file:
            json.dump(settings, file)
        await ctx.send(f"Setting `{setting_name}` set to `{setting_value}`")

@bot.event
async def on_message(message):
    # Check if the message sender is not the bot itself
    if message.author != bot.user:
        # Check if the content of the message is 'hello'
        # if it is a command, process command else respond to message
        if message.content.startswith('.'):
            await bot.process_commands(message)
        else:
            # Check if llm_token exists in config.json, if doesn't exist send a message to the user
            with open("files/config.json", "r") as file:
                settings = json.load(file)
            if "llm_token" not in settings:
                await message.channel.send("No LLM token found. Please set it using `.config llm_token <token>`")
            else:
                model.llm_token = settings["llm_token"]
                response = model.converse(message.content)
                await message.channel.send(response)

bot.run(bot_token)