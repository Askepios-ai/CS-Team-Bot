import os
import discord
import json
from discord.ext import commands
from discord import app_commands, Embed
import requests

MASTERBLASTER_URL = "https://app.masterblaster.gg/"
PUBLIC_API = "api/external/v1/"
INTERNAL_API = "api/"
TEAMS = "team/"
RESULT = "results/"
STANDING = "standings/"
MATCH = "match/"
ORGANIZAITON = "organization/"
PLAYERS = "players/"


class GameAccount:
    def __init__(self, id, nick, avatarUrl, gameId) -> None:
        self.id = id
        self.nick = nick
        self.avatar_url = avatarUrl
        self.gameId = gameId

    def from_json(json: str):
        return GameAccount(json["id"], json["nick"], json["avatarUrl"], json["gameId"])


class MBPlayer:
    def __init__(self, id, name, avatarUrl, gameAccounts) -> None:
        self.id = id
        self.name = name
        self.avatarUrl = avatarUrl
        self.gameAccounts = self.parse_game_accounts(gameAccounts)

    def parse_game_accounts(self, gameAccounts):
        return [GameAccount.from_json(game_account) for game_account in gameAccounts]

    def from_json(json: str):
        return MBPlayer(
            json["id"], json["nickName"], json["avatarUrl"], json["gameAccounts"]
        )


class MasterblasterHandler(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="get_players",
        description="Get the players in organisation",
    )
    async def get_players(self, interaction: discord.Interaction):
        await interaction.response.send_message("Getting players", ephemeral=True)
        response = requests.get(
            f"{MASTERBLASTER_URL}{INTERNAL_API}{ORGANIZAITON}{self.bot.config.mb_organization_id}/{PLAYERS}"
        ).json()
        embed = discord.Embed(title="Players", color=0x00FF00)
        for player in response:
            mb_player = MBPlayer.from_json(player)
            embed.add_field(name=mb_player.name, value=mb_player.id, inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)
        # for player in response:
        #     mb_player = MBPlayer.from_json(player)
        #     await interaction.followup.send(mb_player.name, ephemeral=True)
        #     for game_account in mb_player.gameAccounts:
        #         await interaction.followup.send(game_account.nick, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(
        MasterblasterHandler(bot), guild=discord.Object(id=bot.config.server_ID)
    )
