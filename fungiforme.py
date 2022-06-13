# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from os.path import exists
import configparser
from datetime import datetime, timedelta
import logging
from urllib import parse
from discord.ext import commands, tasks
from discord import Embed, Color, File as DiscordFile
from discord_buttons_plugin import ButtonsClient, ActionRow, Button, ButtonType
import logsetup


config = configparser.ConfigParser()
config.read("fungiforme.ini", encoding="UTF-8")

logsetup.setup(config)
logger = logging.getLogger("fungiforme")

TOKEN = config["DISCORD"]["Token"]
COMMAND_PREFIX = config["DISCORD"]["CommandPrefix"]
CHANNEL_ID = config["DISCORD"].getint("Channel")
VALID_EMOJI = config["FUNGIFORME"].get("ValidEmoji", "")
MINIMUM_GIF_REACTIONS = config["FUNGIFORME"].getint("MinimumGifReactions")
DATETIME_FORMAT = config["DATE"]["DatetimeFormat"]
DATE_FORMAT = config["DATE"]["DateFormat"]
HOUR_START = config["DATE"]["HourStart"]
HOUR_END = config["DATE"]["HourEnd"]
TIMEZONE_HOURS_DELAY = config["DATE"].getint("TimezoneHoursDelay")
VALID_DAYS = [
    int(vd) for vd in config["DATE"].get("ValidDays", "1,2,3,4,5").split(",")
]

CODE_BASE_URL = "https://github.com/saydigital/fungiforme"
ISSUE_BASE_URL = f"{CODE_BASE_URL}/issues"
ISSUE_NEW_URL = f"{ISSUE_BASE_URL}/new?"


fungiforme = commands.Bot(command_prefix=COMMAND_PREFIX)
buttons = ButtonsClient(fungiforme)


def has_gif_element(message):
    """
    Returns True if the message has a gif element (embed or attach).
    """
    if message.embeds and message.embeds[0].type == "gifv":
        has_embed_gif = True
    else:
        has_embed_gif = False

    if message.attachments and message.attachments[0].filename.lower().endswith(
        ".gif"
    ):
        has_attachment_gif = True
    else:
        has_attachment_gif = False

    return has_embed_gif or has_attachment_gif


def get_game_time_interval(date=None, start_hour=None, end_hour=None):
    """
    Returns the time interval for the game considering time delta.
    """
    if not date:
        date = datetime.today().strftime(DATE_FORMAT)
    if not start_hour:
        start_hour = HOUR_START
    if not end_hour:
        end_hour = HOUR_END

    start_datetime = datetime.strptime(
        f"{date} {start_hour}", DATETIME_FORMAT
    ) - timedelta(hours=TIMEZONE_HOURS_DELAY)

    end_datetime = datetime.strptime(
        f"{date} {end_hour}", DATETIME_FORMAT
    ) - timedelta(hours=TIMEZONE_HOURS_DELAY)

    return start_datetime, end_datetime


def is_valid_reply_gif(message, original_message):
    """
    Returns True if the message is a valid GI reply to an original message.
    """
    valid = False
    if (
        has_gif_element(message)
        and message.reference
        and original_message
        and message.reference.message_id == original_message.id
    ):
        if has_gif_element(original_message):
            # users cannot reply to another GIF
            valid =  False
        elif original_message.author == message.author:
            # users cannot reply to their own messages
            valid =  False
        else:
            valid =  True
    else:
        valid =  False
    return valid


def is_valid_gif_message(message, original_message):
    """
    Returns True if the message is a valid GIF message.
    """
    if is_valid_reply_gif(message, original_message) and message.reactions:
        return True
    return False


def get_message_gif_url(message):
    """
    Returns the GIF URL of the message.
    """
    object_url = Embed.Empty
    if message.embeds and message.embeds[0].type == "gifv":
        object_url = message.embeds[0].thumbnail.url
    elif message.attachments and message.attachments[
        0
    ].filename.lower().endswith(".gif"):
        object_url = message.attachments[0].url
    return object_url


async def get_original_message(channel, message):
    """
    Returns the original message of the message.
    """
    original_message = None
    if message.reference:
        # If user replies to another user's message,
        # and the original message is deleted,
        # Discord doesn't show the message state.
        try:
            original_message = await channel.fetch_message(
                message.reference.message_id
            )
        except:
            original_message = None
    return original_message


async def send_gif(channel, gif):
    """
    Sends a GIF from the assets to the channel.
    """
    message = await channel.send(file=DiscordFile(f"assets/gifs/{gif}.gif"))
    return message


@tasks.loop(minutes=1.0)
async def send_match_messages():
    """
    Sends match messages (start and stop) to the channel.
    """
    now = datetime.now()
    string_now = f"{now.hour:02}:{now.minute:02}:00"
    day = now.isoweekday()
    if day in VALID_DAYS and string_now == HOUR_START:
        logger.info("Auto Start match for %s", string_now)
        channel = fungiforme.get_channel(CHANNEL_ID)
        await send_gif(channel, "begin")
    elif day in VALID_DAYS and string_now == HOUR_END:
        logger.info("Auto End match for %s", string_now)
        channel = fungiforme.get_channel(CHANNEL_ID)
        gif_message = await send_gif(channel, "end")
        logger.info("Auto invoke winner command")
        ctx = await fungiforme.get_context(gif_message)
        await ctx.invoke(fungiforme.get_command("winner"))


@fungiforme.listen()
async def on_ready():
    """
    Execute code when the bot is ready.
    """
    send_match_messages.start()


@fungiforme.event
async def on_raw_reaction_remove(payload):
    """
    Execute code when a reaction is removed.
    """
    if (
        VALID_EMOJI
        and payload.emoji.name == VALID_EMOJI
        and payload.channel_id == CHANNEL_ID
    ):
        channel = fungiforme.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        original_message = await get_original_message(channel, message)
        if is_valid_reply_gif(message, original_message):
            date = datetime.today().strftime(DATE_FORMAT)
            after_date = datetime.strptime(
                f"{date} {HOUR_START}", DATETIME_FORMAT
            ) - timedelta(hours=TIMEZONE_HOURS_DELAY)
            before_date = datetime.strptime(
                f"{date} {HOUR_END}", DATETIME_FORMAT
            ) - timedelta(hours=TIMEZONE_HOURS_DELAY)
            if after_date <= message.created_at <= before_date:
                user = await fungiforme.fetch_user(payload.user_id)
                embed_var = Embed(
                    title=f"Warning! {user.name} has been warned!",
                    description="You were caught removing your vote "
                    "from a valid GIF. "
                    "Very soon this behavior will be banned.",
                    color=Color.red(),
                    url=message.jump_url,
                )
                embed_var.set_author(
                    name=user.display_name,
                    icon_url=user.avatar_url,
                )
                await channel.send(embed=embed_var)


@fungiforme.event
async def on_message(message):
    """
    Execute code when a message is sent.
    """
    today_game_start, today_game_end = get_game_time_interval()
    original_message = None
    if message.reference:
        original_message = await message.channel.fetch_message(
            message.reference.message_id
        )
    if (
        not message.author.bot
        and message.channel.id == CHANNEL_ID
        and has_gif_element(message)
        and today_game_start <= message.created_at < today_game_end
        and (
            not is_valid_reply_gif(message, original_message)
            or original_message.created_at < today_game_start
        )
    ):
        embed_var = Embed(
            title=f"Warning! {message.author.name} has been warned!",
            description="Your GIF wasn't a valid reply "
            "to another user's text message of today's game.\n"
            "Any reaction added to this GIF will be ignored.",
            color=Color.red(),
            url=message.jump_url,
        )
        embed_var.set_author(
            name=message.author.display_name,
            icon_url=message.author.avatar_url,
        )
        await message.channel.send(embed=embed_var)
    else:
        await fungiforme.process_commands(message)


@fungiforme.command()
async def issue(ctx):
    """
    Sends the complete issue link prepared for Github.
    """
    message = ctx.message
    original_message = None
    if message.reference:
        # If user replies to another user's message,
        # and the original message is deleted,
        # Discord doesn't show the message state.
        try:
            original_message = await ctx.message.channel.fetch_message(
                message.reference.message_id
            )
        except:
            original_message = None
    if original_message:
        data = {
            "id": original_message.id,
            "channel": original_message.channel.id,
            "author": original_message.author.id,
            "content": original_message.content,
            "created_at": original_message.created_at.isoformat(),
            "HOUR_START": HOUR_START,
            "HOUR_END": HOUR_END,
            "TIMEZONE_HOURS_DELAY": TIMEZONE_HOURS_DELAY,
        }
        params = {
            "labels": "bug",
            "title": f"Bug on message {original_message.id}",
            "body": data,
        }
        url_params = parse.urlencode(params)
        await buttons.send(
            channel=ctx.message.channel.id,
            components=[
                ActionRow(
                    [
                        Button(
                            label="Create the issue on github",
                            style=ButtonType().Link,
                            url=f"{ISSUE_NEW_URL}{url_params}",
                        )
                    ]
                )
            ],
        )
    else:
        await message.reply(
            "You need to reply to a message to create an issue."
        )


@fungiforme.command()
async def info(ctx):
    """
    Sends the complete information about the BOT to the channel.
    """
    with open("VERSION", encoding="UTF-8") as version_file:
        version_text = version_file.read().replace("\n", "")
    info_text = f"**Fungiforme** *v{version_text}*"
    await ctx.message.channel.send(info_text)
    await buttons.send(
            channel=ctx.message.channel.id,
            components=[
                ActionRow(
                    [
                        Button(
                            label="Homepage",
                            style=ButtonType().Link,
                            url=CODE_BASE_URL,
                        ),
                        Button(
                            label="Issues",
                            style=ButtonType().Link,
                            url=ISSUE_BASE_URL,
                        )
                    ]
                )
            ],
        )


@fungiforme.command()
async def rules(ctx):
    """
    Sends the complete rules text to the channel.
    """
    rules_text = (
        "No rules defined!\n"
        "> What is an anarchist? "
        "One who, choosing, accepts the responsibility of choice."
    )
    if exists("RULES.md"):
        with open("RULES.md", encoding="UTF-8") as rule_file:
            rules_text = rule_file.read()
    await ctx.message.channel.send(rules_text)


@fungiforme.command()
async def winner(ctx, date=None, start=None, end=None):
    """
    Sends messages for the winners of the game.
    """
    if not date:
        date = datetime.today().strftime(DATE_FORMAT)
    if not start:
        start = HOUR_START
    if not end:
        end = HOUR_END
    contest_channel = fungiforme.get_channel(CHANNEL_ID)
    response_channel = ctx.message.channel
    await response_channel.send("Let me check...")
    await send_gif(response_channel, "confused")
    autovote_users = []
    gifs = {}
    after_date = datetime.strptime(
        f"{date} {start}", DATETIME_FORMAT
    ) - timedelta(hours=TIMEZONE_HOURS_DELAY)
    before_date = datetime.strptime(
        f"{date} {end}", DATETIME_FORMAT
    ) - timedelta(hours=TIMEZONE_HOURS_DELAY)
    messages = await contest_channel.history(
        limit=500,
        oldest_first=False,
        after=after_date,
        before=before_date,
    ).flatten()
    for message in messages:
        # Get only messages with GIF and reactions
        original_message = await get_original_message(contest_channel, message)
        if (
            is_valid_gif_message(message, original_message)
            and after_date <= original_message.created_at < before_date
        ):
            message_reaction = 0
            voted_by = []
            for reaction in message.reactions:
                # If a valid emoji is defined, use it to filter reactions
                if VALID_EMOJI and reaction.emoji != VALID_EMOJI:
                    continue
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
                    "original_message": original_message,
                }
    if gifs:
        gifs = dict(
            sorted(
                gifs.items(),
                key=lambda item: item[1]["reactions"],
                reverse=True,
            )
        )
        ordered_votes = set()
        for message in gifs:
            ordered_votes.add(gifs[message]["reactions"])
        ordered_votes = sorted(ordered_votes, reverse=True)[:3]
    # Gold, silver, and bronze
    colors = [Color.gold(), Color.dark_gray(), Color.from_rgb(184, 115, 51)]
    default_color = Color.blue()
    user_showed = []
    for message, element in gifs.items():
        if message.author in user_showed:
            continue
        votes = element["reactions"]
        if votes in ordered_votes:
            vote_index = ordered_votes.index(votes)
            vote_position = vote_index + 1
            color = colors[vote_index]
        else:
            color = default_color
            vote_position = 0
        original_message = element["original_message"]
        voted_by = ", ".join([user.name for user in element["users"]])
        gif_points = config["FUNGIFORME"].getfloat(
            f"PointsForPosition{vote_position}", 0
        )
        # Show only gifs with valid points
        if gif_points > 0:
            gif_points_message = f" (+{gif_points} points)"
        else:
            continue
        message_points = config["FUNGIFORME"].getfloat(
            f"PointsForOriginalMessagePosition{vote_position}", 0
        )
        if message_points > 0:
            message_points_message = f" (+{message_points} points)"
        else:
            message_points_message = ""
        embed_var = Embed(
            title=f"{str(votes)} votes{gif_points_message}",
            description=f"Voted by *{voted_by}*",
            color=color,
            url=message.jump_url,
        )
        embed_var.set_author(
            name=message.author.display_name,
            icon_url=message.author.avatar_url,
        )
        embed_var.set_thumbnail(url=get_message_gif_url(message))
        embed_var.add_field(
            name="As reply to",
            value=f"{original_message.content}\n"
            f"- {original_message.author.name}{message_points_message} -",
            inline=True,
        )
        user_showed.append(message.author)
        # Add medal reaction
        if vote_position > 0:
            medal = config["FUNGIFORME"].get(
                f"MedalPosition{vote_position}", ""
            )
            if medal:
                # Discord has a limit for the reaction on every message.
                # If we add more than the limit, the bot will not be able
                # to add the medal.
                try:
                    await message.add_reaction(medal)
                except:
                    # TODO Log error
                    pass
        await response_channel.send(embed=embed_var)
    await send_gif(response_channel, "done")


fungiforme.run(TOKEN)
