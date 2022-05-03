# Invite URL
# https://discord.com/api/oauth2/authorize?client_id=964498743451856938&permissions=2147697728&scope=bot

from os.path import exists
import configparser
from datetime import datetime, timedelta
from discord.ext import commands
from discord import Embed, Color


config = configparser.ConfigParser()
config.read('fungiforme.ini')


TOKEN = config['DISCORD']['Token']
CHANNEL_ID = config['DISCORD'].getint('Channel')
MINIMUM_GIF_REACTIONS = config['FUNGIFORME'].getint('MinimumGifReactions')
DATETIME_FORMAT = config['DATE']['DatetimeFormat']
DATE_FORMAT = config['DATE']['DateFormat']
HOUR_START = config['DATE']['HourStart']
HOUR_END = config['DATE']['HourEnd']
TIMEZONE_HOURS_DELAY = config['DATE'].getint('TimezoneHoursDelay')


fungiforme = commands.Bot(command_prefix='!')


@fungiforme.command()
async def rules(ctx):
    rules = \
        "No rules defined!\n" \
        "> What is an anarchist? " \
        "One who, choosing, accepts the responsibility of choice."
    if exists('RULES.md'):
        with open('RULES.md') as f:
            rules = f.read()
    await ctx.message.channel.send(rules)


@fungiforme.command()
async def winner(ctx, date=None, start=None, end=None):
    if not date:
        date = datetime.today().strftime(DATE_FORMAT)
    if not start:
        start = HOUR_START
    if not end:
        end = HOUR_END
    channel = fungiforme.get_channel(CHANNEL_ID)
    await ctx.message.channel.send('Let me check...')
    autovote_users = []
    gifs = {}
    after_date = datetime.strptime(
        f'{date} {HOUR_START}', DATETIME_FORMAT
        ) - timedelta(hours=TIMEZONE_HOURS_DELAY)
    before_date = datetime.strptime(
        f'{date} {HOUR_END}', DATETIME_FORMAT
        ) - timedelta(hours=TIMEZONE_HOURS_DELAY)
    messages = await channel.history(
        limit=200,
        oldest_first=False,
        after=after_date,
        before=before_date,
        ).flatten()
    for message in messages:
        # Get only messages with GIF and reactions
        if message.embeds \
                and message.embeds[0].type == 'gifv' \
                and message.reactions:
            message_reaction = 0
            voted_by = []
            for reaction in message.reactions:
                users = await reaction.users().flatten()
                if message.author in users:
                    autovote_users.append(message.author)
                else:
                    message_reaction += len(users)
                    voted_by.extend([user for user in users])
            if message_reaction >= MINIMUM_GIF_REACTIONS:
                gifs[message] = {
                    "reactions": message_reaction,
                    "users": voted_by,
                    }
    if gifs:
        gifs = dict(sorted(
            gifs.items(),
            key=lambda item: item[1]["reactions"],
            reverse=True))
        ordered_points = set()
        for message in gifs:
            ordered_points.add(gifs[message]["reactions"])
        ordered_points = sorted(ordered_points, reverse=True)[:3]
    # Gold, silver, and bronze
    colors = [Color.gold(), Color.dark_gray(), Color.from_rgb(184, 115, 51)]
    default_color = Color.blue()
    user_showed = []
    for message in gifs:
        if message.author in user_showed:
            continue
        points = gifs[message]["reactions"]
        if points in ordered_points:
            color = colors[ordered_points.index(points)]
        else:
            color = default_color
        original_message = await channel.fetch_message(
            message.reference.message_id)
        voted_by = ', '.join([user.name for user in gifs[message]["users"]])
        embedVar = Embed(
            title=f"{str(points)} points",
            description=f"Voted by *{voted_by}*",
            color=color,
            url=message.jump_url
            )
        embedVar.set_author(
            name=message.author.display_name,
            icon_url=message.author.avatar_url,
            )
        embedVar.set_thumbnail(url=message.embeds[0].thumbnail.url)
        embedVar.add_field(
            name="As reply to",
            value=f"{original_message.content}\n"
            f"- {original_message.author.name} -",
            inline=True,
            )
        user_showed.append(message.author)
        await ctx.message.channel.send(embed=embedVar)
    await ctx.message.channel.send('Done!')


fungiforme.run(TOKEN)
