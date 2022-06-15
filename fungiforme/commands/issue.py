# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging

from discord.ext import commands
from fungiforme.fungiforme import register_extension
from urllib import parse
from discord_buttons_plugin import ActionRow, Button, ButtonType
from fungiforme.utils import ISSUE_NEW_URL


logger = logging.getLogger(__name__)


class IssueHandler:
    def __init__(self, bot):
        self.bot = bot
    
    async def handle(self, ctx):
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
            await self.bot.message_reply(message, content="You need to reply to a message to create an issue.")
    

class Issue(commands.Cog):
    def __init__(self, bot, handler):
        self.bot = bot
        self.handler = handler

    @commands.command()
    async def issue(self, ctx):
        """Sends the complete issue link prepared for Github. Must be used in reply to a message."""
        await self.handler.handle(ctx)


def setup(bot):
    command_handler = IssueHandler(bot)
    command = Issue(bot, command_handler)
    bot.add_cog(command)


register_extension(__name__)
