# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import logging

from datetime import datetime, timedelta
from discord.ext import commands, tasks


logger = logging.getLogger(__name__)


class SendMatchMessagesHandler:
    """
    on_ready Event Handler.
    """
    def __init__(self, bot):
        self.bot = bot
        self.valid_days = [
            int(vd) for vd in bot.config["DATE"].get("ValidDays", "1,2,3,4,5").split(",")
        ]
        self.contest_channel_id = bot.config['DISCORD'].getint('Channel')
        self.hour_start = bot.config['DATE']['HourStart']
        self.hour_end = bot.config['DATE']['HourEnd']
        self.timezone = bot.config['DATE']['TimeZone']

    def _get_tz_aware_now(self):
        try:
            sign = "-" if self.timezone[0] == "-" else "+"
            hours_str = f"{sign}{self.timezone[1:3]}"
            minutes_str = f"{sign}{self.timezone[3:]}"

            hours_td = int(hours_str)
            minutes_td = int(minutes_str)
            return datetime.utcnow() + timedelta(hours=hours_td, minutes=minutes_td)
        except (IndexError, TypeError, ValueError):
            return datetime.utcnow()

    async def handle(self):
        """
        on_ready Event Handler entrypoint.

        :param payload: raw event payload data
        """
        now = self._get_tz_aware_now()
        string_now = f"{now.hour:02}:{now.minute:02}:00"
        day = now.isoweekday()
        if day in self.valid_days and string_now == self.hour_start:
            logger.info("Auto Start match for %s", string_now)
            channel = self.bot.get_channel(self.contest_channel_id)
            await self.bot.send_channel_message(channel, msg_type='gif', content="begin")
        elif day in self.valid_days and string_now == self.hour_end:
            logger.info("Auto End match for %s", string_now)
            channel = self.bot.get_channel(self.contest_channel_id)
            gif_message = await self.bot.send_channel_message(
                channel,
                msg_type='gif',
                content="end"
            )
            logger.info("Auto invoke winner command")
            ctx = await self.bot.get_context(gif_message)
            await self.bot.auto_invoke_cog_command(ctx, "Winner")


class SendMatchMessages(commands.Cog):
    """
    Send match messages Task.
    """
    def __init__(self, bot):
        self.bot = bot
        self.handler = SendMatchMessagesHandler(bot)
        # pylint: disable=no-member
        self.send_match_messages.start()

    async def cog_unload(self):
        """
        Hook for cog class unload
        """
        # pylint: disable=no-member
        self.send_match_messages.cancel()

    @tasks.loop(minutes=1.0)
    async def send_match_messages(self):
        """
        Sends match messages (start and stop) to the channel.
        """
        await self.handler.handle()

    @send_match_messages.before_loop
    async def before_send_match_messages(self):
        """
        Waits for bot to be ready before starting loop
        """
        await self.bot.wait_until_ready()


async def setup(bot):
    """
    Event setup function.

    :param bot: Fungiforme bot
    """
    event = SendMatchMessages(bot)
    await bot.add_cog(event)
