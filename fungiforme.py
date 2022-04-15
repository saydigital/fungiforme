# Invite URL
# https://discord.com/api/oauth2/authorize?client_id=964498743451856938&permissions=2147697728&scope=bot

import configparser
from datetime import datetime, timedelta
from discord.ext import commands


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
async def winner(ctx, date=None, start=None, end=None):
    if not date:
        date = datetime.today().strftime(DATE_FORMAT)
    if not start:
        start = HOUR_START
    if not end:
        end = HOUR_END
    channel = fungiforme.get_channel(CHANNEL_ID)
    await channel.send('Let me check...')
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
            for reaction in message.reactions:
                users = await reaction.users().flatten()
                if message.author in users:
                    autovote_users.append(message.author)
                else:
                    message_reaction += len(users)
            if message_reaction >= MINIMUM_GIF_REACTIONS:
                gifs[message] = message_reaction
    if gifs:
        gifs = dict(sorted(
            gifs.items(),
            key=lambda item: item[1],
            reverse=True))
    winner_message = [f'Winner(s) for Fun-Gif-Orme {date} {start} - {end}', '']
    for message in gifs:
        tmp_winner = ' | '.join([
            str(gifs[message]), message.author.name, message.jump_url])
        winner_message.append(tmp_winner)
    winner_message = '\n'.join(winner_message)
    await channel.send(winner_message)


fungiforme.run(TOKEN)
