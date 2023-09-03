import discord
import requests
import pickle
from discord import app_commands
from discord.ext import commands
from constants import Permissions, ranks
from cachetools import TTLCache, cached
from player import Player
from helperfunctions import DiscordString, load_state, persist_state
from csgo import get_active_duty


class MemberHandler(commands.Cog):
    @load_state
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.registration_message = None

    def store_state(self):
        with open(self.bot.config.persist_file, "wb") as f:
            pickle.dump(self.players, f)

    @app_commands.command(
        name="start_registration_season",
        description="Send a message to start the registration process for a new season.",
    )
    async def start_registration(self, interaction: discord.Interaction):
        if not self.bot.is_member(interaction.user):
            return
        if self.registration_message:
            return
        await self.reset_state()
        await interaction.response.send_message(
            "@everyone Welcome to a new season of bedriftsligaen! Please react to this message to sign up."
        )
        self.registration_message = await interaction.original_response()
        await self.registration_message.add_reaction("✅")

    async def reset_state(self):
        if self.registration_message:
            await self.registration_message.delete()
            self.registration_message = None
        for id in self.players:
            member = self.bot.get_member(id)
            if member:
                await member.remove_roles(
                    discord.Object(id=self.bot.config.team_role_ID),
                    reason="Registration",
                )
        self.players = {}
        self.store_state()

    @app_commands.command(
        name="cancel_registration_season",
        description="Cancel the registration process for a season.",
    )
    async def cancel_registration(self, interaction: discord.Interaction):
        if not self.bot.is_member(interaction.user):
            return
        if not self.registration_message:
            return
        await self.reset_state()
        await interaction.response.send_message(
            "Registration cancelled.", ephemeral=True
        )

    @app_commands.command(
        name="end_registration_season",
        description="End the registration process for a season.",
    )
    async def end_registration(self, interaction: discord.Interaction):
        if not self.bot.is_member(interaction.user):
            return
        if not self.registration_message:
            return
        await self.registration_message.edit(content="Registration is now closed.")
        self.registration_message = None
        await interaction.response.send_message("Registration closed.", ephemeral=True)

    @persist_state
    async def add_member(self, member):
        await member.add_roles(
            discord.Object(id=self.bot.config.team_role_ID),
            reason="Registration",
        )
        self.players[member.id] = Player(member.id, member.name, member.display_name)
        await member.send(f"You are now registered as a member of the team.")

    @persist_state
    async def remove_member(self, member):
        await member.remove_roles(
            discord.Object(id=self.bot.config.team_role_ID),
            reason="Registration",
        )
        try:
            del self.players[member.id]
        except KeyError:
            pass
        await member.send(
            f"You have been removed from the member list. Please react to the registration message to rejoin."
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction: discord.RawReactionActionEvent):
        if reaction.member.id == self.bot.user.id:
            return
        if (
            not self.registration_message
            or reaction.message_id != self.registration_message.id
        ):
            return
        self.bot.log.debug(f"Raw reaction add from {reaction.user_id}")
        reaction.member = self.bot.get_member(reaction.user_id)
        if not reaction.member:
            return
        await self.add_member(reaction.member)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction: discord.RawReactionActionEvent):
        if reaction.user_id == self.bot.user.id:
            return
        if (
            not self.registration_message
            or reaction.message_id != self.registration_message.id
        ):
            return
        self.bot.log.debug(f"Raw reaction remove from: {reaction.user_id}")
        reaction.member = self.bot.get_member(reaction.user_id)
        if not reaction.member:
            return
        await self.remove_member(reaction.member)

    @app_commands.command(
        name="add_member",
        description="Add a member to the member list.",
    )
    async def add_member_command(
        self, interaction: discord.Interaction, member_id: str
    ):
        if not self.bot.is_member(interaction.user):
            return
        member = self.bot.get_member(int(member_id))
        await self.add_member(member)
        await interaction.response.send_message(
            f"Added {member.name} to the member list."
        )

    @app_commands.command(
        name="remove_member",
        description="Remove a member from the member list.",
    )
    async def remove_member_command(
        self, interaction: discord.Interaction, member_id: str
    ):
        if not self.bot.is_member(interaction.user):
            return
        member = self.bot.get_member(int(member_id))
        await self.remove_member(member)
        await interaction.response.send_message(
            f"Removed {member.name} from the member list."
        )

    @app_commands.command(
        name="list_members",
        description="List all members.",
    )
    async def list_members_command(self, interaction: discord.Interaction):
        if not self.bot.is_member(interaction.user):
            return
        discord_string = DiscordString("Members | Banorder:\n")
        for player in self.players.values():
            discord_string += DiscordString(f"{player.display_name} {player.title}\n")
            discord_string += DiscordString(f"{player.map_order()}").to_code_inline()
        await interaction.response.send_message(f"{discord_string}")

    @app_commands.command(
        name="add_maps",
        description="Add map preference, from most to least wanter.",
    )
    async def add_maps(
        self,
        interaction: discord.Interaction,
        m1: str,
        m2: str,
        m3: str,
        m4: str,
        m5: str,
        m6: str,
        m7: str,
    ):
        if not self.bot.is_member(interaction.user):
            return
        await interaction.response.send_message(
            f"Maps: {m1} {m2} {m3} {m4} {m5} {m6} {m7}"
        )
        choices = await interaction.original_response()
        uniques = set(choices.content.split(" ")[1:])
        if len(uniques) != len(get_active_duty()):
            await choices.edit(content="Please select 7 different maps.")

        for map in uniques:
            if map not in get_active_duty():
                await choices.edit(
                    content="Please select maps from the active duty pool."
                )
                return
        self.players[interaction.user.id].update_maps(
            list(choices.content.split(" ")[1:])
        )
        await interaction.response.send_message("Maps added.", ephemeral=True)
        self.store_state()

    @add_maps.autocomplete("m1")
    @add_maps.autocomplete("m2")
    @add_maps.autocomplete("m3")
    @add_maps.autocomplete("m4")
    @add_maps.autocomplete("m5")
    @add_maps.autocomplete("m6")
    @add_maps.autocomplete("m7")
    async def add_maps_autocomplete(
        self, interaction: discord.Interaction, map: str
    ) -> list[app_commands.Choice[str]]:
        map_pool = get_active_duty()
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in map_pool
            if map.lower() in choice.lower()
        ]

    @app_commands.command(
        name="set_rank",
        description="Set your rank.",
    )
    async def set_rank(self, interaction: discord.Interaction, rank: str):
        if not self.bot.is_member(interaction.user):
            return
        self.players[interaction.user.id].set_rank(rank)
        await interaction.response.send_message(f"Rank set to {rank}")
        self.store_state()

    @set_rank.autocomplete("rank")
    async def set_rank_autocomplete(
        self, interaction: discord.Interaction, rank: str
    ) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=choice, value=choice) for choice in ranks.values()
        ]


async def setup(bot):
    await bot.add_cog(MemberHandler(bot), guild=discord.Object(id=bot.config.server_ID))
