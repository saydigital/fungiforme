# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging

from datetime import datetime
from discord import File as DiscordFile
from discord.utils import MISSING

from bot.bot import BaseBot


logger = logging.getLogger(__name__)


class Fungiforme(BaseBot):
    """
    Fungiforme bot implementation.
    """

    def get_game_time_interval(self, date=None, start_hour=None, end_hour=None):
        """
        Returns the time interval for the game considering time delta.
        """
        date_format = self.config['DATE']['DateFormat']
        datetime_format = self.config['DATE']['DatetimeFormat']
        timezone = self.config['DATE']['TimeZone']
        if not date:
            date = datetime.today().strftime(date_format)
        if not start_hour:
            start_hour = self.config['DATE']['HourStart']
        if not end_hour:
            end_hour = self.config['DATE']['HourEnd']

        start_datetime = datetime.strptime(f"{date} {start_hour}{timezone}", datetime_format)
        end_datetime = datetime.strptime(f"{date} {end_hour}{timezone}", datetime_format)

        return start_datetime, end_datetime

    async def send_channel_message(self, channel, msg_type='text', content=""):
        """
        Sends a message to a discord channel.

        :param channel: Discord channel
        :param str msg_type: Type of the message to send. Can be: embed, gif, button or simple text
        :param content: Content to send
        """
        if msg_type == 'embed':
            return await channel.send(embed=content)
        if msg_type == 'gif':
            return await channel.send(file=DiscordFile(f"assets/gifs/{content}.gif"))
        if msg_type == 'button':
            return await self.buttons.send(channel=channel.id, components=content)

        return await channel.send(content)

    async def send_interaction_response(self, interaction, content="", view=MISSING):
        """
        Sends a interaction response.

        :param interaction: Discord interaction
        :param content: Content to send
        :param view: View object to send in message
        """
        return await interaction.response.send_message(content, view=view)

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
        return [message async for message in channel.history(
            limit=500,
            oldest_first=False,
            after=after_date,
            before=before_date,
        )]

    async def get_reaction_user(self, reaction):
        """
        Returns the users who added a certain reaction.

        :param reaction: Discord reaction

        :returns a list of users
        """
        return [user async for user in reaction.users()]

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

    async def get_payload_user(self, payload):
        """
        Returns the user associated to a payload

        :param payload: raw event payload data

        returns: discord user
        """
        return await self.fetch_user(payload.user_id)

    async def get_channel_message(self, channel, message_id):
        """
        Returns a message with the message_id sent on a discord channel

        :param channel: discord channel
        :param message_id: discord message id

        returns: discord message
        """
        return await channel.fetch_message(message_id)

    async def auto_invoke_cog_command(self, ctx, cog_name):
        """
        Auto invokes a bot command.

        :param ctx: context
        :param str command_name: command name to invoke
        """
        command_handler = self.get_cog(cog_name).handler
        await command_handler.handle(ctx.channel)

    # async method get_context must be overridden for test purpouses

    # method get_channel must be overridden for test purpouses
