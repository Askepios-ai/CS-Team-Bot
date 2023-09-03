import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import has_permissions


class AdminHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="load",
        description="Load a module.",
    )
    @has_permissions(administrator=True)
    async def load(self, interaction: discord.Interaction, module: str):
        try:
            await self.bot.load_extension(f"cogs.{module}")
        except commands.ExtensionError as e:
            await interaction.response.send_message(
                f"Error loading {module}: {e}", ephemeral=True
            )
        else:
            await interaction.response.send_message(f"Loaded {module}.", ephemeral=True)

    @app_commands.command(
        name="unload",
        description="Unload a module.",
    )
    @has_permissions(administrator=True)
    async def unload(self, interaction: discord.Interaction, module: str):
        try:
            await self.bot.unload_extension(f"cogs.{module}")
        except commands.ExtensionError as e:
            await interaction.response.send_message(
                f"Error loading {module}: {e}", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"Unloaded {module}.", ephemeral=True
            )

    @app_commands.command(
        name="reload_extension",
        description="Reload an extension.",
    )
    @has_permissions(administrator=True)
    async def reload(self, interaction: discord.Interaction, module: str):
        try:
            await self.bot.reload_extension(f"cogs.{module}")
        except commands.ExtensionError as e:
            await interaction.response.send_message(
                f"Error loading {module}: {e}", ephemeral=True
            )
        else:
            await interaction.response.send_message(f"Loaded {module}.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(AdminHandler(bot), guild=discord.Object(id=bot.config.server_ID))
