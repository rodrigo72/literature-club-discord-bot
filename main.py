import os
import sys
import json
import random
import discord
import logging
import platform
import datetime
import uuid

from suggestion_yacc import parser
from dotenv import load_dotenv

from discord.ext import commands, tasks
from discord.ext.commands import Context

import asyncio
from tinydb import TinyDB, Query

from utils import LoggingFormatter

"""CONFIG"""

if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json") as file:
        config = json.load(file)

intents = discord.Intents.default()
intents.message_content = True

"""LOGGER"""

logger = logging.getLogger('bot')
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())

# File handler
file_handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)


def get_embed_from_suggestion(s: dict, author: str) -> discord.Embed:
    embed = discord.Embed(
        title=s['title'],
        color=0xA7A7A7,
    )

    if 'description' in s and s['description']:
        embed.description = s['description']

    fields = {
        'author': (s.get('author'), False),
        'genre': (s.get('genre'), False),
        'date': (s.get('date'), False),
        'notes': (s.get('notes'), False),
        'reviews': (s.get('reviews'), False),
        'links': (s.get('links'), False),
        'download': (s.get('download'), False),
        'pages': (s.get('pages'), False),
        'goodreads': (s.get('goodreads'), False),
        'wikipedia': (s.get('wikipedia'), False),
        'quotes': (s.get('quotes'), False),
    }

    for name, value in fields.items():
        if value[0]:
            embed.add_field(name=name.capitalize(), value=value[0], inline=value[1])

    embed.set_footer(text=f"Suggested by {author} \nUUID: {s['id']}")
    return embed


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=config["prefix"],
            intents=intents,
            help_command=None,
        )
        self.logger = logger
        self.config = config
        self.database = TinyDB("db.json")

    async def load_cogs(self) -> None:
        for f in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if f.endswith(".py"):
                extension = f[:-3]
                try:
                    await self.load_extension_with_db(f"cogs.{extension}")
                    self.logger.info(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(
                        f"Failed to load extension {extension}\n{exception}"
                    )

    async def load_extension_with_db(self, name: str) -> None:
        module = __import__(name, fromlist=['setup'])
        await module.setup(self, self.database)

    @tasks.loop(minutes=1.0)
    async def status_task(self) -> None:
        if random.randint(0, 1) == 0:
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Three-Body Problem"))
        else:
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="male manipulator music"))

    @status_task.before_loop
    async def before_status_task(self) -> None:
        await self.wait_until_ready()

    async def setup_hook(self) -> None:
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        self.logger.info("-------------------")
        await self.load_cogs()
        self.status_task.start()

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user or message.author.bot:
            return
        if message.content.startswith(config["prefix"]):
            await self.process_commands(message)
        else:
            try:
                result = parser.parse(message.content.lower())
                await self.send_parser_result(message, result)
            except Exception as e:
                pass

    async def add_server_if_not_exists(self, server_id: int, server_name: str) -> None:
        server = Query()
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self.database.search, server.server_id == server_id)
        if not result:
            await loop.run_in_executor(None, self.database.insert, {
                'server_id': server_id,
                'server_name': server_name,
                'months': {},
            })
            self.logger.info(f"Added server {server_name} to the database.")
        else:
            self.logger.info(f"Server {server_name} already exists in the database.")

    async def send_parser_result(self, message: discord.Message, result: list) -> None:
        await self.add_server_if_not_exists(message.guild.id, message.guild.name)

        server = Query()
        loop = asyncio.get_running_loop()
        result_db = await loop.run_in_executor(None, self.database.search, server.server_id == message.guild.id)

        if not result_db:  # impossible
            self.logger.error(f"Server {message.guild.name} not found in the database.")
            return

        user_id = str(message.author.id)
        current_month = datetime.datetime.now().strftime("%B")
        months = result_db[0]['months']

        if months.get(current_month) is None:
            months[current_month] = {}
            months[current_month][user_id] = []
        elif months[current_month].get(user_id) is None:
            months[current_month][user_id] = []

        suggestions = []
        for item in result:
            obj = {}
            for key, value in item:
                if isinstance(value, list):
                    obj[key] = ' '.join(value)
                else:
                    obj[key] = value
            if obj != {}:
                suggestions.append(obj)

        for s in suggestions:
            s['id'] = str(uuid.uuid4())
            months[current_month][user_id].append(s)
            embed = get_embed_from_suggestion(s, message.author.name)
            await message.channel.send(embed=embed)

        await loop.run_in_executor(
            None, self.database.update, {'months': months}, server.server_id == message.guild.id
        )

    async def on_command_completion(self, context: Context) -> None:
        full_command_name = context.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        if context.guild is not None:
            self.logger.info(
                f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})"
            )
        else:
            self.logger.info(
                f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs"
            )

    async def on_command_error(self, context: Context, error) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            hours = hours % 24
            embed = discord.Embed(
                description=f"**Please slow down** - You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.NotOwner):
            embed = discord.Embed(
                description="You are not the owner of the bot!", color=0xE02B2B
            )
            await context.send(embed=embed)
            if context.guild:
                self.logger.warning(
                    f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the guild" 
                    f"{context.guild.name} (ID: {context.guild.id}), but the user is not an owner of the bot."
                )
            else:
                self.logger.warning(
                    f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the bot's "
                    f"DMs, but the user is not an owner of the bot."
                )
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                description="You are missing the permission(s) `"
                            + ", ".join(error.missing_permissions)
                            + "` to execute this command!",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                description="I am missing the permission(s) `"
                            + ", ".join(error.missing_permissions)
                            + "` to fully perform this command!",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Error!",
                description=str(error).capitalize(),
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        else:
            raise error


if __name__ == '__main__':
    load_dotenv()
    bot = DiscordBot()
    bot.run(os.getenv("TOKEN"))
