import discord
from discord.ext import commands
from utils.mongo_db import MongoDBHandler
from utils.logger import log_error, log_debug
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord_bot.bot import Bot

sys.path.append("../")
handler = MongoDBHandler("database")
embed_color = discord.Color.brand_green()


class HelpDocsCog(commands.Cog):
    """
    Cog for handling helpdocs commands.
    """

    def __init__(self, bot: "Bot"):
        """
        Initializes the HelpDocsCog class.
        Args:
          bot (Bot): The bot instance.
        """
        self.bot = bot

    @commands.hybrid_command()
    async def helpdocs(self, ctx: commands.Context):
        """
        Sends a help message for the helpdocs commands.
        Args:
          ctx (commands.Context): The context of the command.
        Returns:
          None
        Side Effects:
          Sends a help message to the user.
        Notes:
          The command is only available in the AI text-chat category.
        Examples:
          >>> helpdocs
          Sends a help message for the helpdocs commands.
        """
        channel = ctx.channel
        if channel.category.id != self.bot.chatbot_category_id:
            await ctx.send(
                "Please use this command in the 'AI' text-chat category.",
                ephemeral=True,
            )
            return
        log_debug(self.bot, f"HelpDocs command used by user: {ctx.author.id}")
        await ctx.defer(ephemeral=True)
        embed = discord.Embed(title="Chatbot Docs Help", color=embed_color)
        embed.set_author(
            name="GitHub [Click Here]",
            url="https://github.com/AntonOsika/gpt-engineer",
            icon_url="https://cdn.discordapp.com/attachments/1114412425115086888/1114413065933439058/25231.png",
        )
        embed.add_field(name="/helpdocs", value="This help message.", inline=True)
        embed.add_field(
            name="/ingestdocs",
            value="Ingest a readthedocs.io documentation website.",
            inline=True,
        )
        embed.add_field(
            name="/listdocs",
            value="View a list of your ingested documentation websites.",
            inline=True,
        )
        embed.add_field(
            name="/deletedocs",
            value="Delete an ingested documentation website from the list.",
            inline=True,
        )
        embed.add_field(
            name="/askdocs",
            value="Ask about an ingested documentation website.",
            inline=True,
        )
        embed.add_field(
            name="**Note:**",
            value="All command messages are set to private.",
            inline=False,
        )
        await ctx.send(embed=embed, ephemeral=True)


async def setup(bot: "Bot") -> None:
    """Loads the cog."""
    try:
        await bot.add_cog(HelpDocsCog(bot))
        log_debug(bot, "HelpDocsCog loaded.")
    except Exception as e:
        log_error(bot, f"Error loading HelpDocsCog: {e}")
