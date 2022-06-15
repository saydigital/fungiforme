# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging

from discord.ext import commands
from discord import Embed, Color
from datetime import datetime, timedelta
from fungiforme import utils
from fungiforme.fungiforme import register_extension


logger = logging.getLogger(__name__)


class WinnerHandler:
    def __init__(self, bot):
        self.bot = bot
        self.contest_channel_id = bot.config['DISCORD'].getint('Channel')
        self.valid_emoji = bot.config['FUNGIFORME'].get('ValidEmoji', '')
        self.date_format = bot.config['DATE']['DateFormat']
        self.datetime_format = bot.config['DATE']['DatetimeFormat']
        self.timezone_hours_delay = bot.config['DATE'].getint(
            'TimezoneHoursDelay'
        )
        self.minimum_gif_reactions = bot.config['FUNGIFORME'].getint('MinimumGifReactions')
    
    def _prepare_date_params(self, date=None, hour_start=None, hour_end=None):
        """
        Prepares date and time parameters handling default values if not specified.

        :param date date: Day when a fungiforme game occurred
        :param time hour_start: Start hour of a fungiforme game
        :param time hour_end: End hour of a fungiforme game

        :returns a tuple with date, start hour and end hour of a Fungiforme game
        """
        date_result = date
        hour_start_result = hour_start
        hour_end_result = hour_end
        
        if not date_result:
            date_result = datetime.today().strftime(self.date_format)
        if not hour_start_result:
            hour_start_result = self.bot.config['DATE']['HourStart']
        if not hour_end_result:
            hour_end_result = self.bot.config['DATE']['HourEnd']
        
        return date_result, hour_start_result, hour_end_result

    def _get_ordered_votes_and_gifs(self, gifs):
        """
        Returns a list of GIFS sorted by descending reaction count and
        a list of the top 3 votes.

        :param list gifs: List of info dict about gifs

        :returns a tuple of orderd votes and gifs
        """
        ordered_votes = set()
        ordered_gifs = {}
        if gifs:
            ordered_gifs = dict(sorted(
                gifs.items(),
                key=lambda item: item[1]["reactions"],
                reverse=True)
            )
            for message in gifs:
                ordered_votes.add(gifs[message]["reactions"])
            ordered_votes = sorted(ordered_votes, reverse=True)[:3]
        return ordered_votes, ordered_gifs

    async def _get_valid_messages_to_compute(self, contest_channel, after_date, before_date):
        """
        Returns a list of discord messages, containing GIFS and reaction, 
        which are eligible for victory.

        :param contest_channel: Fungiforme game channel
        :param datetime after_date: Oldest message timestamp
        :param datetime before_date: Newest message timestamp

        :returns a list of valid gifs info dicts
        """
        gifs = {}
        autovote_users = []
        messages = await self.bot.get_history_messages(
            contest_channel, after_date, before_date
        )
        for message in messages:
            # Get only messages with GIF and reactions
            original_message = await self.bot.get_original_message(contest_channel, message)
            if utils.is_valid_gif_message(message, original_message) \
                and after_date <= original_message.created_at < before_date:
                message_reaction = 0
                voted_by = []
                for reaction in message.reactions:
                    # If a valid emoji is defined, use it to filter reactions
                    if self.valid_emoji and reaction.emoji != self.valid_emoji:
                        continue
                    users = await self.bot.get_reaction_user(reaction)
                    if message.author in users:
                        autovote_users.append(message.author)
                    else:
                        message_reaction += len(users)
                        voted_by.extend([user for user in users])
                if message_reaction >= self.minimum_gif_reactions:
                    gifs[message] = {
                        "reactions": message_reaction,
                        "users": voted_by,
                        "original_message": original_message,
                    }
        return gifs

    async def _show_final_game_rank(self, response_channel, gifs, ordered_votes):
        """
        Creates game rank and sends it to discord channel.

        :param response_channel: Fungiforme game response channel
        :param dict gifs: Gifs info dict
        :param dict ordered_votes: List of the top 3 votes
        """
        # Gold, silver, and bronze
        colors = [Color.gold(), Color.dark_gray(), Color.from_rgb(184, 115, 51)]
        default_color = Color.blue()
        user_showed = []
        for message in gifs:
            if message.author in user_showed:
                continue
            votes = gifs[message]["reactions"]
            if votes in ordered_votes:
                vote_index = ordered_votes.index(votes)
                vote_position = vote_index + 1
                color = colors[vote_index]
            else:
                color = default_color
                vote_position = 0
            original_message = gifs[message]["original_message"]
            voted_by = ', '.join([user.name for user in gifs[message]["users"]])
            gif_points = self.bot.config['FUNGIFORME'].getfloat(
            f'PointsForPosition{vote_position}', 0)
            # Show only gifs with valid points
            if gif_points > 0:
                gif_points_message = f" (+{gif_points} points)"
            else:
                continue
            message_points = self.bot.config['FUNGIFORME'].getfloat(
                f'PointsForOriginalMessagePosition{vote_position}', 0)
            if message_points > 0:
                message_points_message = f" (+{message_points} points)"
            else:
                message_points_message = ""
            embedVar = Embed(
                title=f"{str(votes)} votes{gif_points_message}",
                description=f"Voted by *{voted_by}*",
                color=color,
                url=message.jump_url
            )
            embedVar.set_author(
                name=message.author.display_name,
                icon_url=message.author.avatar_url,
            )
            embedVar.set_thumbnail(url=utils.get_message_gif_url(message))
            embedVar.add_field(
                name="As reply to",
                value=f"{original_message.content}\n"
                f"- {original_message.author.name}{message_points_message} -",
                inline=True,
            )
            user_showed.append(message.author)
            # Add medal reaction
            if vote_position > 0:
                medal = self.bot.config['FUNGIFORME'].get(
                    f'MedalPosition{vote_position}', '')
                if medal:
                    # Discord has a limit for the reaction on every message.
                    # If we add more than the limit, the bot will not be able
                    # to add the medal.
                    try:
                        await self.bot.add_message_reaction(message, medal)
                    except Exception as e:
                        logger.error(e, exec_info=True)
            
            await self.bot.send_channel_message(
                response_channel, 
                msg_type='embed', 
                content=embedVar
            )

    async def handle(self, ctx, date=None, hour_start=None, hour_end=None):
        date, hour_start, hour_end = self._prepare_date_params(date, hour_start, hour_end)
        contest_channel = self.bot.get_channel(self.contest_channel_id)
        response_channel = ctx.message.channel
        await self.bot.send_channel_message(
            response_channel, 
            content='Let me check...'
        )
        await self.bot.send_channel_message(
            response_channel, 
            msg_type='gif', 
            content='confused'
        )
        after_date = datetime.strptime(
            f'{date} {hour_start}', self.datetime_format
        ) - timedelta(hours=self.timezone_hours_delay)
        before_date = datetime.strptime(
            f'{date} {hour_end}', self.datetime_format
        ) - timedelta(hours=self.timezone_hours_delay)

        
        gifs = await self._get_valid_messages_to_compute(contest_channel, after_date, before_date)
        ordered_votes, ordered_gifs = self._get_ordered_votes_and_gifs(gifs)
        
        await self._show_final_game_rank(response_channel, ordered_gifs, ordered_votes)
        await self.bot.send_channel_message(
            response_channel, 
            msg_type='gif', 
            content='done'
        )
    

class Winner(commands.Cog):
    def __init__(self, bot, handler):
        self.bot = bot
        self.handler = handler

    @commands.command()
    async def winner(self, ctx, date=None, hour_start=None, hour_end=None):
        """Sends messages for the winners of the game.
        
        :param date date: Day when a fungiforme game occurred
        :param time hour_start: Start hour of a fungiforme game
        :param time hour_end: End hour of a fungiforme game
        """
        await self.handler.handle(ctx, date, hour_start, hour_end)


def setup(bot):
    command_handler = WinnerHandler(bot)
    command = Winner(bot, command_handler)
    bot.add_cog(command)


register_extension(__name__)
