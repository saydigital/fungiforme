# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging

from urllib import parse

from discord.ext import commands
from discord_buttons_plugin import ActionRow, Button, ButtonType
# pylint: disable=no-name-in-module
from fungiforme.utils import ISSUE_NEW_URL


logger = logging.getLogger(__name__)


class IssueHandler:
    """
    Issue Command Handler.
    """
    def __init__(self, bot):
        self.bot = bot

    async def handle(self, ctx):
        """
        Issue Command Handler entrypoint.

        :param ctx: command context
        """
        message = ctx.message
        original_message = await self.bot.get_original_message(ctx.message.channel, message)
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
            await self.bot.send_channel_message(
                ctx.message.channel,
                msg_type='button',
                content=[
                    ActionRow([
                        Button(
                            label="Create the issue on github",
                            style=ButtonType().Link,
                            url=f"{ISSUE_NEW_URL}{url_params}",
                        )
                    ])
                ]
            )
        else:
            await self.bot.message_reply(
                message,
                content="You need to reply to a message to create an issue."
            )


class Issue(commands.Cog):
    """
    Issue Command.
    """
    def __init__(self, bot):
        self.bot = bot
        self.handler = IssueHandler(bot)

    @commands.command()
    async def issue(self, ctx):
        """Sends the complete issue link prepared for Github. Must be used in reply to a message."""
        await self.handler.handle(ctx)

    @commands.command()
    async def debug(self, ctx, message_id=None):
        """Sends a message with relevant information about a message."""
        channel = self.bot.get_channel(
            self.bot.config['DISCORD'].getint('Channel'))
        msg = await channel.fetch_message(message_id)
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
        await ctx.message.channel.send("\n".join(data))


def setup(bot):
    """
    Command setup function.

    :param bot: Fungiforme bot
    """
    command = Issue(bot)
    bot.add_cog(command)
