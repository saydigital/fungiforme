# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging

from os.path import exists
from discord.ext import commands


logger = logging.getLogger(__name__)


class RulesHandler:
    """
    Rules Command Handler.
    """
    def __init__(self, bot):
        self.bot = bot

    async def handle(self, ctx):
        """
        Rules Command Handler entrypoint.

        :param ctx: command context
        """
        rules_text = (
            "No rules defined!\n"
            "> What is an anarchist? "
            "One who, choosing, accepts the responsibility of choice."
        )
        if exists("RULES.md"):
            with open("RULES.md", encoding="UTF-8") as rule_file:
                rules_text = rule_file.read()
        await self.bot.send_channel_message(ctx.message.channel, content=rules_text)


class Rules(commands.Cog):
    """
    Rules Command.
    """
    def __init__(self, bot):
        self.bot = bot
        self.handler = RulesHandler(bot)

    @commands.command()
    async def rules(self, ctx):
        """Sends the complete rules text to the channel."""
        await self.handler.handle(ctx)


def setup(bot):
    """
    Command setup function.

    :param bot: Fungiforme bot
    """
    command = Rules(bot)
    bot.add_cog(command)
