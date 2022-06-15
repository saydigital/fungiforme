# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging

from os.path import exists
from discord.ext import commands
from fungiforme.fungiforme import register_extension


logger = logging.getLogger(__name__)


class RulesHandler:
    def __init__(self, bot):
        self.bot = bot
    
    async def handle(self, ctx):
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
    def __init__(self, bot, handler):
        self.bot = bot
        self.handler = handler

    @commands.command()
    async def rules(self, ctx):
        """Sends the complete rules text to the channel."""
        await self.handler.handle(ctx)


def setup(bot):
    command_handler = RulesHandler(bot)
    command = Rules(bot, command_handler)
    bot.add_cog(command)


register_extension(__name__)
