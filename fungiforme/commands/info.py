# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging

from discord import app_commands, Interaction, Object, ButtonStyle
from discord.ext import commands
from discord.ui import View, Button
# pylint: disable=no-name-in-module
from fungiforme.utils import CODE_BASE_URL, ISSUE_BASE_URL


logger = logging.getLogger(__name__)


class InfoHandler:
    """
    Info Command Handler.
    """
    def __init__(self, bot):
        self.bot = bot

    async def handle(self, interaction: Interaction):
        """
        Info Command Handler entrypoint.

        :param interaction: command interaction
        """
        with open("VERSION", encoding="UTF-8") as version_file:
            version_text = version_file.read().replace("\n", "")
            info_text = f"**Fungiforme** *v{version_text}*"
            view = View()
            view.add_item(
                Button(
                    label="Homepage",
                    style=ButtonStyle.link,
                    url=CODE_BASE_URL,
                )
            )
            view.add_item(
                Button(
                    label="Issues",
                    style=ButtonStyle.link,
                    url=ISSUE_BASE_URL,
                )
            )
            await self.bot.send_interaction_response(interaction, content=info_text, view=view)


class Info(commands.Cog):
    """
    Info Command.
    """
    def __init__(self, bot):
        self.bot = bot
        self.handler = InfoHandler(bot)

    @app_commands.command()
    async def info(self, interaction: Interaction):
        """Sends the complete information about the BOT to the channel."""
        await self.handler.handle(interaction)


async def setup(bot):
    """
    Command setup function.

    :param bot: Fungiforme bot
    """
    Info.GUILD_ID = bot.config['DISCORD']['GuildId']
    command = Info(bot)
    my_guild = Object(bot.config['DISCORD']['GuildId'])
    await bot.add_cog(command, guilds=[my_guild])
