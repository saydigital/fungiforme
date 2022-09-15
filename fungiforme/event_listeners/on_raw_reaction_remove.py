# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging

from discord.ext import commands
from discord import Embed, Color
# pylint: disable=no-name-in-module
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
            channel = self.bot.get_channel(payload.channel_id)
            message = await self.bot.get_channel_message(channel, payload.message_id)
            original_message = await self.bot.get_original_message(channel, message)
            if utils.is_valid_reply_gif(message, original_message):
                today_game_start, today_game_end = self.bot.get_game_time_interval()
                if today_game_start <= message.created_at <= today_game_end:
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
                        icon_url=user.display_avatar.url,
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


async def setup(bot):
    """
    Event setup function.

    :param bot: Fungiforme bot
    """
    event = OnRawReactionRemove(bot)
    await bot.add_cog(event)
