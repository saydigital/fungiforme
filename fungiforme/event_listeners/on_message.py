# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging


from discord.ext import commands
from discord import Embed, Color
# pylint: disable=no-name-in-module
from fungiforme import utils


logger = logging.getLogger(__name__)


class OnMessageHandler:
    """
    on_message Event Handler.
    """
    def __init__(self, bot):
        self.bot = bot
        self.contest_channel_id = bot.config['DISCORD'].getint('Channel')

    async def handle(self, message):
        """
        on_message Event Handler entrypoint.

        :param message: discord message
        """
        today_game_start, today_game_end = self.bot.get_game_time_interval()
        original_message = await self.bot.get_original_message(message.channel, message)
        if (
            not message.author.bot
            and message.channel.id == self.contest_channel_id
            and utils.has_gif_element(message)
            and today_game_start <= message.created_at < today_game_end
            and (
                not utils.is_valid_reply_gif(message, original_message)
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
            await self.bot.send_channel_message(
                message.channel,
                msg_type='embed',
                content=embed_var
            )


class OnMessage(commands.Cog):
    """
    on_message Event.
    """
    def __init__(self, bot):
        self.bot = bot
        self.handler = OnMessageHandler(bot)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Execute code when a message is sent."""
        await self.handler.handle(message)


def setup(bot):
    """
    Event setup function.

    :param bot: Fungiforme bot
    """
    event = OnMessage(bot)
    bot.add_cog(event)
