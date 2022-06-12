import os
import logging

from discord.ext.commands import Bot
from discord import File as DiscordFile

logger = logging.getLogger(__name__)


class Fungiforme(Bot):
    def __init__(self, config, description=None, **options):
        self.config = config
        command_prefix = config['DISCORD']['CommandPrefix']
        super().__init__(command_prefix, description=description, **options)

    def run(self):
        token = self.config['DISCORD']['Token']
        super().run(token)

    def load_extensions(self, root_pkg):
        root_pkg_path = root_pkg.replace('.', os.sep)
        
        if root_pkg.endswith('.'):
            root_pkg = root_pkg[:-1]

        for dir_name, _, file_list in os.walk(root_pkg_path):
            for file in file_list:
                extension_pkg = self._get_extension_pkg(root_pkg, dir_name, file)
                if extension_pkg:
                    logger.debug(f"Loading extension {extension_pkg} of root package {root_pkg}")
                    super().load_extension(extension_pkg, package=root_pkg)
    
    async def send_channel_message(self, channel, msg_type='text', content=""):
        if msg_type == 'embed':
            await channel.send(embed=content)
        elif msg_type == 'gif':
            await channel.send(file=DiscordFile(f"assets/gifs/{content}.gif"))
        else:
            await channel.send(content)

    async def get_original_message(self, channel, message):
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
        return await channel.history(
            limit=500,
            oldest_first=False,
            after=after_date,
            before=before_date,
        ).flatten()

    async def get_reaction_user(self, reaction):
        return await reaction.users().flatten()

    async def add_message_reaction(self, message, reaction):
        await message.add_reaction(reaction)
        
    def _get_extension_pkg(self, root_pkg, dir_name, file):
        if file.endswith('.py') and not file.startswith('__'):
            file_name = os.path.join(dir_name, file[:-3])
            pkg_name = file_name.replace(os.sep, '.')
            return pkg_name.replace(root_pkg, '')
        else:
            return None
