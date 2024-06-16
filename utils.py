import logging
from datetime import datetime
from discord import Embed
from typing import Dict, Tuple
from dateutil.relativedelta import relativedelta
import re


class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        form = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        form = form.replace("(black)", self.black + self.bold)
        form = form.replace("(reset)", self.reset)
        form = form.replace("(levelcolor)", log_color)
        form = form.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(form, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


def to_title_case(s: str) -> str | None:
    if not s:
        return s
    return s.title()


def capitalize_first_letter(s: str) -> str | None:
    if not s:
        return s
    return s[0].upper() + s[1:]


def current_month_year():
    now = datetime.now()
    formatted_date = now.strftime("%m/%y")
    return formatted_date


def next_month_year():
    now = datetime.now()
    next_month = now + relativedelta(months=1)
    formatted_date = next_month.strftime("%m/%y")
    return formatted_date


def get_embed_from_suggestion(s: dict, author: str) -> Embed:
    embed = Embed(
        title=to_title_case(s['title']),
        color=0xA7A7A7,
    )

    if 'description' in s and s['description']:
        embed.description = capitalize_first_letter(s['description'])

    fields: Dict[str, Tuple[str | None, bool]] = {
        'author': (to_title_case(s.get('author')), False),
        'genre': (to_title_case(s.get('genre')), False),
        'date': (to_title_case(s.get('date')), False),
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


def clean_string_before_parsing(s: str) -> str:
    pattern = r"([*_`]+)([^\:]{0,10}?)\:([^\:]*?)\1"

    def replace_colon(match):
        style = match.group(1)
        left = match.group(2)
        right = match.group(3)
        return f'{style}{left}{style}:{right}'

    return re.sub(pattern, replace_colon, s)


def clean_text_after_parsing(s: str) -> str:
    pattern = r"(?<!\.\.)(\.\s+?)(?!(?:http(?:s)?)|www|[^\s]+?\.(?:com|dev|org))([a-z])"

    def replace_colon(match):
        dot_and_space = match.group(1)
        letter = match.group(2).upper()
        return f"{dot_and_space}{letter}"

    return re.sub(pattern, replace_colon, s)
