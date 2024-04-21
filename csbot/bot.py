import asyncio
import os
import logging
from typing import Optional
import discord
from dotenv import load_dotenv, find_dotenv
from discord.ext import commands
from discord import app_commands
from configuration import Configuration
from constants import Permissions


class CSBot(commands.Bot):
    def __init__(self, config):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        self.log = None
        self.setup_logging()
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
        normal_handler = logging.FileHandler(
            f"{self.__class__.__name__}.log", mode="a", encoding="utf-8"
        )
        normal_handler.setFormatter(formatter)
        normal_handler.setLevel(logging.WARNING)

        debug_handler = logging.FileHandler(
            f"{self.__class__.__name__}.debug.log", mode="a", encoding="utf-8"
        )
        debug_handler.setFormatter(formatter)
        debug_handler.setLevel(logging.DEBUG)

        self.log = logging.getLogger(self.__class__.__qualname__)
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
        try:
            for handler in self.handlers:
                await self.load_extension(handler)
        except Exception as e:
            self.log.error("Error loading %s: %s", handler, e)
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
        """
        Get the permissions of a member
        """
        if self.broadcast_channel.permissions_for(member).administrator:
            self.log.debug("Admin: %s", member.name)
            return Permissions.admin
        elif self.broadcast_channel.permissions_for(member).manage_roles:
            self.log.debug("Member: %s", member.name)
            return Permissions.member
        else:
            self.log.debug("Unknown: %s", member.name)
            return Permissions.restricted

    async def unload_all(self):
        """
        Unload all cogs
        """
        for c in self.handlers:
            await self.unload_extension(c)


if __name__ == "__main__":
    load_dotenv(os.getenv("ENV_FILE"))
    client = CSBot(Configuration())
    client.run(os.getenv("DISCORD_TOKEN"))
