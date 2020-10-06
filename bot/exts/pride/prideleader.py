import json
import logging
import random
from pathlib import Path

import discord
from discord.ext import commands
from fuzzywuzzy import fuzz

from bot.constants import Colours
log = logging.getLogger(__name__)


class PrideLeader(commands.Cog):
    """Gives information about Pride Leaders."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.pride = self.load_json()

    @staticmethod
    def load_json() -> dict:
        """Loads pride leader information from static json resource."""
        explanation_file = Path("bot/resources/pride/prideleader.json")
        with explanation_file.open(encoding="utf8") as json_data:
            pride = json.load(json_data)

        return pride

    def name_verifier(self, leader_name: str) -> str:
        """Verify leader name wether it is present in json or not."""
        leader_name = leader_name.split(" ")
        leader_name = ' '.join(name.capitalize() for name in leader_name)
        if leader_name in self.pride:
            log.trace("Got Valid name.")
            return leader_name

    def invalid_embed_generate(self, pride_leader: str) -> discord.Embed:
        """Genrates Invalid Embed."""
        embed = discord.Embed()
        embed.color = Colours.soft_red
        valid_name = []
        pride_leader = pride_leader.split(" ")
        pride_leader = ' '.join(name.capitalize() for name in pride_leader)
        for name in self.pride.keys():
            if fuzz.ratio(pride_leader, name) >= 40:
                valid_name.append(name)

        if len(valid_name) == 0:
            valid_name = ", ".join([name for name in self.pride.keys()])
            error_msg = "Sorry your input didn't match any name which i know,here is the list whom i know"
        else:
            valid_name = "\n".join([name for name in valid_name])
            error_msg = "Did you mean?"
        embed.description = f"{error_msg}\n```{valid_name}```"
        return embed

    def embed_builder(self, leader_name: str) -> discord.Embed:
        """Genrate Embed with pride leader info."""
        embed = discord.Embed()
        embed.color = Colours.blue
        embed.title = f'__{leader_name}__'
        embed.description = self.pride[leader_name]["About"]
        embed.add_field(name="__Known for__", value=self.pride[leader_name]["Known for"], inline=False)
        embed.add_field(name="__D.O.B and Birth place__", value=self.pride[leader_name]["Born"], inline=False)
        embed.add_field(name="__Awards and honors__", value=self.pride[leader_name]["Awards"], inline=False)
        embed.set_thumbnail(url=self.pride[leader_name]["url"])
        return embed

    @commands.command(name="prideleader", aliases=['pl'])
    async def pl(self, ctx: commands.Context, *, pride_leader_name: str = None) -> None:
        """Provides info about pride leader randomly without taking any args or by taking name."""
        if pride_leader_name is None:
            log.trace("Name not provided by the user so selecting random from json.")
            name_list = [name for name in self.pride.keys()]
            pride_leader_name = random.choice(name_list)
        leader = self.name_verifier(pride_leader_name)
        if leader is None:
            log.trace("Got invalid name.")
            final_embed = self.invalid_embed_generate(pride_leader_name)
        else:
            final_embed = self.embed_builder(leader)
        await ctx.send(embed=final_embed)


def setup(bot: commands.Bot) -> None:
    """Cog loader for drag queen name generator."""
    bot.add_cog(PrideLeader(bot))
