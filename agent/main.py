import discord
from discord.ext import commands, tasks
from functions import *
import os
import json
from datetime import datetime

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)
channel_id = os.environ.get('CHANNEL_ID')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    check_reminders.start()

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
    # Show examples on how to use the commands
    await ctx.send('Example')

@bot.command()
async def ping(ctx):
    """Returns the latency of the bot"""
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command()
async def reminder(ctx, description, date, time):
    """Sets a reminder with description, date, and time."""
    
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
        with open("output_files/reminders.json", "r") as file:
            reminders = json.load(file)
    except FileNotFoundError:
        reminders = []

    # Add the new reminder to the list
    reminders.append(reminder_data)

    # Save updated reminders to JSON file
    with open("output_files/reminders.json", "w") as file:
        json.dump(reminders, file)

    await ctx.send(f"Reminder set: {description} on {date} at {time}")

@tasks.loop(seconds=60)
async def check_reminders():
    # Open reminders.json file
    with open("output_files/reminders.json", "r") as file:
        reminders = json.load(file)

    # Get the current time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    channel = bot.get_channel(channel_id)

    # Load old reminders from old_reminders.json file
    try:
        with open("output_files/old_reminders.json", "r") as old_file:
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
    with open("output_files/reminders.json", "w") as file:
        json.dump(reminders, file)

    # Save sent reminders to old_reminders.json file
    with open("output_files/old_reminders.json", "w") as old_file:
        json.dump(old_reminders, old_file)

discord_bot_token = os.environ.get('BOT_TOKEN')
bot.run(discord_bot_token)