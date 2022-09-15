# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import importlib
import os
import logging

from os.path import basename, join, isfile
from discord.ext.commands import Bot
from discord import Intents, Object


logger = logging.getLogger(__name__)


class BaseBot(Bot):
    """
    Generic Bot Implementation
    """

    def __init__(self, config, description=None, **options):
        self.config = config
        command_prefix = config['DISCORD']['CommandPrefix']
        intents = options.pop('intents', Intents.all())
        intents.presences = False
        intents.members = False
        super().__init__(command_prefix, description=description, intents=intents, **options)

    def run(self, *args, **kwargs):
        """
        Starts bot.
        """
        token = self.config['DISCORD']['Token']
        super().run(token, *args, **kwargs)

    async def setup_hook(self):
        my_guild = Object(self.config['DISCORD']['GuildId'])
        await self.load_extensions()
        await self.tree.sync(guild=my_guild)

    async def load_extensions(self):
        """
        Loads all extensions
        """
        for extension in self._get_extensions():
            logger.info("Loading extension: %s", extension)
            await super().load_extension(extension)

    def _get_extensions(self):
        modules_to_load = self._get_default_extensions()
        if self.config.has_section("EXTENSIONS"):
            ext_modules = self.config['EXTENSIONS']['modules']
            if ext_modules:
                modules_to_load.update(ext_modules.split(','))
        extensions = []
        for module in modules_to_load:
            submodules = self._get_submodules(module.strip())
            extensions += submodules
        return extensions

    def _get_submodules(self, module):
        submodules = []
        module_spec = importlib.util.find_spec(module)
        if not module_spec:
            return submodules
        for directory in module_spec.submodule_search_locations:
            for item in os.listdir(directory):
                file_path = join(directory, item)
                if isfile(file_path) and not item.startswith('__'):
                    submodule_name = basename(item)[:-3]
                    submodules.append(f"{module}.{submodule_name}")
        return submodules

    def _get_default_extensions(self):
        current_module_path = self.__class__.__module__.split('.')
        current_module_path = '.'.join(current_module_path[:-1])
        return set([
            f"{current_module_path}.commands",
            f"{current_module_path}.event_listeners",
            f"{current_module_path}.tasks",
        ])
