# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging

from urllib import parse

from discord import app_commands, Object, Interaction, ButtonStyle
from discord.ext import commands
from discord.ui import View, Button
# pylint: disable=no-name-in-module
from fungiforme.utils import ISSUE_NEW_URL


logger = logging.getLogger(__name__)


class IssueHandler:
    """
    Issue Command Handler.
    """
    def __init__(self, bot):
        self.bot = bot

    async def handle(self, interaction: Interaction, message_link: str):
        """
        Issue Command Handler entrypoint.

        :param interaction: command interaction
        :param message_link: link of the message to report
        """
        try:
            message_id = int(message_link.split('/')[-1])
            original_message = await self.bot.get_channel_message(
                interaction.channel, message_id
            )
        except ValueError:
            original_message = None

        if original_message:
            data = {
                "id": original_message.id,
                "channel": original_message.channel.id,
                "author": original_message.author.id,
                "content": original_message.content,
                "created_at": original_message.created_at.isoformat(),
                "HOUR_START": self.bot.config['DATE']['HourStart'],
                "HOUR_END": self.bot.config['DATE']['HourEnd'],
                "TIMEZONE_HOURS_DELAY": self.bot.config["DATE"].getint("TimezoneHoursDelay"),
            }
            params = {
                "labels": "bug",
                "title": f"Bug on message {original_message.id}",
                "body": data,
            }
            url_params = parse.urlencode(params)
            view = View()
            view.add_item(
                Button(
                    label="Create the issue on github",
                    style=ButtonStyle.link,
                    url=f"{ISSUE_NEW_URL}{url_params}",
                )
            )
            await self.bot.send_interaction_response(interaction, view=view)
        else:
            await self.bot.send_interaction_response(
                interaction,
                content="You need to provide a valid message link to create an issue."
            )


class Issue(commands.Cog):
    """
    Issue Command.
    """
    def __init__(self, bot):
        self.bot = bot
        self.handler = IssueHandler(bot)

    @app_commands.command()
    async def issue(self, interaction: Interaction, message_link: str):
        """Sends the complete issue link prepared for Github."""
        await self.handler.handle(interaction, message_link)

    @app_commands.command()
    async def debug(self, interaction: Interaction, message_id: str):
        """Sends a message with relevant information about a message."""
        channel = self.bot.get_channel(
            self.bot.config['DISCORD'].getint('Channel'))
        msg = await self.bot.get_channel_message(channel, message_id)
        data =[
            f"* **ID**: {msg.id}",
            f"* **Channel**: {msg.channel}",
            f"* **Author**: {msg.author}",
            f"* **Content**: {msg.content}",
            f"* **Reference**: {msg.reference}",
            f"* **Reference Message**: "
            f"{msg.reference.message_id if msg.reference else None}",
            f"* **Embeds**: {msg.embeds if msg.embeds else None}",
            f"* **Embed 0 Type**: "
            f"{msg.embeds[0].type if msg.embeds else None}",
            f"* **Attachments**: "
            f"{msg.attachments if msg.attachments else None}",
            f"* **Attachment 0 Filename**: "
            f"{msg.attachments[0].filename if msg.attachments else None}",
        ]
        await self.bot.send_interaction_response(interaction, content="\n".join(data))


async def setup(bot):
    """
    Command setup function.

    :param bot: Fungiforme bot
    """
    command = Issue(bot)
    my_guild = Object(bot.config['DISCORD']['GuildId'])
    await bot.add_cog(command, guilds=[my_guild])
