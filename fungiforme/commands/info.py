# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging

from discord.ext import commands
from discord_buttons_plugin import ActionRow, Button, ButtonType
from fungiforme.utils import CODE_BASE_URL, ISSUE_BASE_URL


logger = logging.getLogger(__name__)


class InfoHandler:
    """
    Info Command Handler.
    """
    def __init__(self, bot):
        self.bot = bot

    async def handle(self, ctx):
        """
        Info Command Handler entrypoint.

        :param ctx: command context
        """
        with open("VERSION", encoding="UTF-8") as version_file:
            version_text = version_file.read().replace("\n", "")
            info_text = f"**Fungiforme** *v{version_text}*"
            await self.bot.send_channel_message(ctx.message.channel, content=info_text)
            await self.bot.send_channel_message(
                ctx.message.channel,
                msg_type='button',
                content=[
                    ActionRow([
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
                    ])
                ]
            )


class Info(commands.Cog):
    """
    Info Command.
    """
    def __init__(self, bot):
        self.bot = bot
        self.handler = InfoHandler(bot)

    @commands.command()
    async def info(self, ctx):
        """Sends the complete information about the BOT to the channel."""
        await self.handler.handle(ctx)


def setup(bot):
    """
    Command setup function.

    :param bot: Fungiforme bot
    """
    command = Info(bot)
    bot.add_cog(command)
