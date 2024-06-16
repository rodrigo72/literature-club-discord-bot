from discord.ext import commands
from discord.ext.commands import Context

import asyncio
from tinydb import Query
from utils import next_month_year, get_embed_from_suggestion, clean_string_before_parsing
from suggestion_yacc import parser
import re

SCAN_LIMIT = 100


class Suggestions(commands.Cog, name="suggestions"):
    def __init__(self, bot, database) -> None:
        self.bot = bot
        self.database = database

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

    @commands.hybrid_command(
        name="s",
        description="Shows the suggestions made by a user in a specific month. "
                    "Defaults to the next month and the current user. "
                    "Optional arguments: month (MM/YY) and user (mention), in any order. "
                    "Example: !s 06/24 @rudrigu.",
    )
    async def s(self, context: Context, arg1=None, arg2=None) -> None:
        await self.add_server_if_not_exists(context.guild.id, context.guild.name)
        mention_pattern = re.compile(r"<@!?(\d+)>")
        month_pattern = re.compile(r"\d{2}/\d{2}")

        # Default values
        if arg1 is None:
            user_id = str(context.author.id)
            month = next_month_year()

        # One argument : month or user
        elif arg2 is None:
            if match := mention_pattern.match(arg1):
                user_id = match.group(1)
                month = next_month_year()
            elif month_pattern.match(arg1):
                user_id = str(context.author.id)
                month = arg1
            else:
                await context.send("Invalid arguments.")
                return

        # Two arguments : month and user
        else:
            if match := mention_pattern.match(arg1):
                user_id = match.group(1)
                if month_pattern.match(arg2):
                    month = arg2
                else:
                    await context.send("Invalid arguments.")
                    return
            elif month_pattern.match(arg1):
                month = arg1
                if match := mention_pattern.match(arg2):
                    user_id = match.group(1)
                else:
                    await context.send("Invalid arguments.")
                    return
            else:
                await context.send("Invalid arguments.")
                return

        server = Query()
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self.database.search, server.server_id == context.guild.id)

        if result:
            if month not in result[0]['months']:
                await context.send("No suggestions found for this month.")
            else:
                suggestions = result[0]['months'][month]
                if user_id in suggestions:
                    for suggestion in suggestions[user_id]:
                        user = await self.bot.fetch_user(int(user_id))
                        embed = get_embed_from_suggestion(suggestion, user.name)
                        await context.send(embed=embed)
                else:
                    if user_id == str(context.author.id):
                        await context.send("You haven't made any suggestions this month.")
                    else:
                        await context.send("This user hasn't made any suggestions this month.")
        else:
            await context.send("Server not found.")

    @commands.hybrid_command(
        name="rs",
        description="Removes a suggestion made by the user. Example !rs <UUID>",
    )
    async def rs(self, context: Context, uuid=None) -> None:
        if not uuid:
            await context.send("Please provide the suggestion UUID.")
            return

        server = Query()
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self.database.search, server.server_id == context.guild.id)

        if not result:
            await context.send("Server not found.")
            return

        user_id = str(context.author.id)
        for month_key, month_data in result[0]['months'].items():
            suggestions = month_data.get(user_id)
            if suggestions:
                for suggestion in suggestions:
                    if suggestion['id'] == uuid:
                        suggestions.remove(suggestion)

                        if len(suggestions) == 0:
                            result[0]['months'][month_key].pop(user_id, None)
                        if len(result[0]['months'][month_key]) == 0:
                            result[0]['months'].pop(month_key, None)

                        await loop.run_in_executor(None, self.database.update, {
                            'months': result[0]['months']
                        }, server.server_id == context.guild.id)
                        await context.send("Suggestion removed.")
                        return

        await context.send("Suggestion not found / Insufficient permissions.")

    @commands.hybrid_command(
        name="month",
        description="Shows all the suggestions made in a specific month. "
                    "Defaults to the next month. "
                    "Optional argument: month (MM/YY). Example: !month 06/24.",
    )
    async def month(self, context: Context, arg=None) -> None:
        if arg is None:
            month = next_month_year()
        elif re.match(r"\d{2}/\d{2}", arg):
            month = arg
        else:
            await context.send("Invalid argument.")
            return

        server = Query()
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self.database.search, server.server_id == context.guild.id)

        if not result:
            await context.send("Server not found in the database.")
            return

        if month not in result[0]['months']:
            await context.send("No suggestions found for this month.")
            return

        for user in result[0]['months'][month]:
            for suggestion in result[0]['months'][month][user]:
                embed = get_embed_from_suggestion(suggestion, context.author.name)
                await context.author.send(embed=embed)

        await context.send("Suggestions sent to your DMs.")

    @commands.hybrid_command(
        name="scan",
        description="Scans the last N messages in the channel for suggestions. "
                    "Example: !scan 06/24 100",
    )
    async def scan(self, context: Context, month, limit: int = None) -> None:
        if not re.match(r"\d{2}/\d{2}", month):
            await context.send("Please provide a valid month (MM/YY).")
            return

        limit = min(limit, SCAN_LIMIT) if limit else SCAN_LIMIT
        channel = context.channel
        count = 0

        async for message in channel.history(limit=limit):
            message_content = clean_string_before_parsing(message.content).lower()
            result = parser.parse(message_content)
            if result is None:
                continue
            await self.bot.add_result_to_db(message, result, month=month)
            count += 1

        await context.send(f"Added {count} suggestions to the database.")


async def setup(bot, database) -> None:
    await bot.add_cog(Suggestions(bot, database))
