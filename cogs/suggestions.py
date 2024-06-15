from discord.ext import commands
from discord.ext.commands import Context

import asyncio
from tinydb import TinyDB, Query
import datetime
from main import get_embed_from_suggestion
import re


class Suggestions(commands.Cog, name="suggestions"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.database = self.database = TinyDB("db.json")
        self.month_translation = {
            'janeiro': 'January',
            'fevereiro': 'February',
            'março': 'March',
            'abril': 'April',
            'maio': 'May',
            'junho': 'June',
            'julho': 'July',
            'agosto': 'August',
            'setembro': 'September',
            'outubro': 'October',
            'novembro': 'November',
            'dezembro': 'December'
        }

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
        description="Shows the suggestions made by a user in a specific month. Defaults to the current month and the "
                    "current user. Optional arguments: month (English or Portuguese) and user (mention), in any order. "
                    "Example: !s june @rudrigu.",
    )
    async def s(self, context: Context, arg1=None, arg2=None) -> None:
        await self.add_server_if_not_exists(context.guild.id, context.guild.name)
        mention_pattern = re.compile(r"<@!?(\d+)>")
        if arg1 is None:  # no arguments
            user_id = str(context.author.id)  # current user
            month = datetime.datetime.now().strftime("%B")  # current month
        elif arg2 is None:  # one argument : month or user
            match = mention_pattern.match(arg1)
            if match:
                user_id = match.group(1)
                month = datetime.datetime.now().strftime("%B")
            else:
                user_id = str(context.author.id)
                arg1 = arg1.lower()
                month = self.month_translation[arg1] if arg1 in self.month_translation else arg1[0].upper() + arg1[1:]
        else:  # two arguments : month and user
            match_arg1 = mention_pattern.match(arg1)
            if match_arg1:
                user_id = match_arg1.group(1)
                arg2 = arg2.lower()
                month = self.month_translation[arg2] if arg2 in self.month_translation else arg2[0].upper() + arg2[1:]
            else:
                match_arg2 = mention_pattern.match(arg2)
                if match_arg2:
                    user_id = match_arg2.group(1)
                    arg1 = arg1.lower()
                    month = self.month_translation[arg1] if arg1 in self.month_translation else arg1[0].upper() + arg1[1:]
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
                        embed = get_embed_from_suggestion(suggestion, context.author.name)
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
        for month_data in result[0]['months'].values():
            suggestions = month_data.get(user_id)
            if suggestions:
                for suggestion in suggestions:
                    if suggestion['id'] == uuid:
                        suggestions.remove(suggestion)
                        await loop.run_in_executor(None, self.database.update, {
                            'months': result[0]['months']
                        }, server.server_id == context.guild.id)
                        await context.send("Suggestion removed.")
                        return

        await context.send("Suggestion not found / Insufficient permissions.")

    @commands.hybrid_command(
        name="month",
        description="Shows all the suggestions made in a specific month. Defaults to the current month. "
                    "Optional argument: month (English or Portuguese). Example: !month june.",
    )
    async def month(self, context: Context, arg=None) -> None:
        if arg is None:
            month = datetime.datetime.now().strftime("%B")
        else:
            arg = arg.lower()
            month = self.month_translation[arg] if arg in self.month_translation else arg[0].upper() + arg[1:]

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


async def setup(bot) -> None:
    await bot.add_cog(Suggestions(bot))
