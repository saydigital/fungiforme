# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging

from discord import File as DiscordFile
from discord_buttons_plugin import ButtonsClient

from bot.bot import BaseBot


logger = logging.getLogger(__name__)


class Fungiforme(BaseBot):
    """
    Fungiforme bot implementation.
    """
    def __init__(self, config, description=None, **options):
        super().__init__(config, description, **options)
        self.buttons = ButtonsClient(self)

    async def send_channel_message(self, channel, msg_type='text', content=""):
        """
        Sends a message to a discord channel.

        :param channel: Discord channel
        :param str msg_type: Type of the message to send. Can be: embed, gif, button or simple text
        :param content: Content to send
        """
        if msg_type == 'embed':
            await channel.send(embed=content)
        elif msg_type == 'gif':
            await channel.send(file=DiscordFile(f"assets/gifs/{content}.gif"))
        elif msg_type == 'button':
            await self.buttons.send(channel=channel.id, components=content)
        else:
            await channel.send(content)

    async def get_original_message(self, channel, message):
        """
        Recorvers the original message linked to a reply message from a channel.

        :param channel: Discord channel
        :param message: Discord reply message

        :returns the original message
        """
        original_message = None
        if message.reference:
            # If user replies to another user's message,
            # # and the original message is deleted,
            # # Discord doesn't show the message state.
            try:
                original_message = await channel.fetch_message(
                    message.reference.message_id)
            except:
                original_message = None
        return original_message

    async def get_history_messages(self, channel, after_date=None, before_date=None):
        """
        Returns a list of discord messages between a timestamp range.

        :param channel: Fungiforme game channel
        :param datetime after_date: Oldest message timestamp
        :param datetime before_date: Newest message timestamp

        :returns a list of discord messages
        """
        return await channel.history(
            limit=500,
            oldest_first=False,
            after=after_date,
            before=before_date,
        ).flatten()

    async def get_reaction_user(self, reaction):
        """
        Returns the users who added a certain reaction.

        :param reaction: Discord reaction

        :returns a list of users
        """
        return await reaction.users().flatten()

    async def add_message_reaction(self, message, reaction):
        """
        Adds a reaction to a message.

        :param message: Discord message
        :param reaction: Discord reaction
        """
        await message.add_reaction(reaction)

    async def message_reply(self, message, msg_type='text', content=""):
        """
        Sends a message as a reply to another message.

        :param message: Discord message
        :param str msg_type: Type of the message to send. Can be: embed, gif, or simple text
        :param content: Content to send
        """
        if msg_type == 'embed':
            await message.reply(embed=content)
        elif msg_type == 'gif':
            await message.reply(file=DiscordFile(f"assets/gifs/{content}.gif"))
        else:
            await message.reply(content)
