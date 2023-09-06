import os
import logging
from typing import Optional
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from configuration import Configuration
from constants import Permissions


class CSBot(commands.Bot):
    def __init__(self, config):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        self.config = config
        self.handlers = [
            "cogs.member",
            "cogs.match",
            "cogs.admin",
            "cogs.masterblaster",
        ]

    def setup_logging(self):
        log_format = "%(levelname)s %(name)s %(asctime)s - %(message)s"
        formatter = logging.Formatter(log_format)
        normal_handler = logging.FileHandler(f"{self.__class__.__name__}.log", mode="w")
        normal_handler.setFormatter(formatter)
        normal_handler.setLevel(logging.WARNING)

        debug_handler = logging.FileHandler(
            f"{self.__class__.__name__}.debug.log", mode="w"
        )
        debug_handler.setFormatter(formatter)
        debug_handler.setLevel(logging.DEBUG)

        self.log = logging.getLogger()
        self.log.setLevel(logging.DEBUG)
        self.log.propagate = False
        self.log.addHandler(normal_handler)
        self.log.addHandler(debug_handler)

    def get_member(self, id) -> discord.member.Member:
        member = None
        for m in self.get_all_members():
            if m.id == id:
                member = m
                break

        return member

    async def setup_hook(self) -> None:
        for handler in self.handlers:
            await self.load_extension(handler)
        await self.tree.sync(guild=discord.Object(id=self.config.server_ID))

    async def on_ready(self):
        self.setup_logging()
        for channel in self.get_all_channels():
            if channel.name == self.config.broadcast_channel:
                self.broadcast_channel = channel

    def is_member(self, id):
        if id:
            if self.broadcast_channel.permissions_for(id).administrator:
                return True
            elif self.broadcast_channel.permissions_for(id).manage_roles:
                return True
        return False

    async def get_permissions(self, member):
        if self.broadcast_channel.permissions_for(member).administrator:
            self.log.debug(f"Admin: {member.name}")
            return Permissions.admin
        elif self.broadcast_channel.permissions_for(member).manage_roles:
            self.log.debug(f"Member: {member.name}")
            return Permissions.member
        else:
            self.log.debug(f"Unknown: {member.name}")
            return Permissions.restricted

    async def unload_all(self):
        for c in self.handlers:
            await self.unload_extension(c)


if __name__ == "__main__":
    load_dotenv()
    client = CSBot(Configuration())
    client.run(os.getenv("DISCORD_TOKEN"))
