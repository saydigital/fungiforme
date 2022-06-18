# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging

from datetime import datetime, timedelta
from discord.ext import commands
from discord import Embed, Color
from fungiforme import utils


logger = logging.getLogger(__name__)


class OnRawReactionRemoveHandler:
    """
    on_raw_reaction_remove Event Handler.
    """
    def __init__(self, bot):
        self.bot = bot
        self.valid_emoji = bot.config['FUNGIFORME'].get('ValidEmoji', '')
        self.contest_channel_id = bot.config['DISCORD'].getint('Channel')
        self.date_format = bot.config['DATE']['DateFormat']
        self.datetime_format = bot.config['DATE']['DatetimeFormat']
        self.timezone_hours_delay = bot.config['DATE'].getint(
            'TimezoneHoursDelay'
        )
        self.hour_start = bot.config['DATE']['HourStart']
        self.hour_end = bot.config['DATE']['HourEnd']

    async def handle(self, payload):
        """
        on_raw_reaction_remove Event Handler entrypoint.

        :param payload: raw event payload data
        """
        if (
            self.valid_emoji
            and payload.emoji.name == self.valid_emoji
            and payload.channel_id == self.contest_channel_id
        ):
            channel = self.bot.get_payload_channel(payload)
            message = await self.bot.get_channel_message(channel, payload.message_id)
            original_message = await self.bot.get_original_message(channel, message)
            if utils.is_valid_reply_gif(message, original_message):
                date = datetime.today().strftime(self.date_format)
                after_date = datetime.strptime(
                    f"{date} {self.hour_start}", self.datetime_format
                ) - timedelta(hours=self.timezone_hours_delay)
                before_date = datetime.strptime(
                    f"{date} {self.hour_end}", self.datetime_format
                ) - timedelta(hours=self.timezone_hours_delay)
                if after_date <= message.created_at <= before_date:
                    user = await self.bot.get_payload_user(payload)
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
                    await self.bot.send_channel_message(
                        channel,
                        msg_type='embed',
                        content=embed_var
                    )

class OnRawReactionRemove(commands.Cog):
    """
    on_raw_reaction_remove Event.
    """
    def __init__(self, bot):
        self.bot = bot
        self.handler = OnRawReactionRemoveHandler(bot)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Execute code when a reaction is removed."""
        await self.handler.handle(payload)


def setup(bot):
    """
    Event setup function.

    :param bot: Fungiforme bot
    """
    event = OnRawReactionRemove(bot)
    bot.add_cog(event)
