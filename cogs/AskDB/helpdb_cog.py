import discord
from discord.ext import commands
from utils.mongo_db import MongoDBHandler
from discord_bot.logger import log_debug, log_error, log_info
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord_bot.bot import Bot

sys.path.append("../")
handler = MongoDBHandler("database")
embed_color = discord.Color.brand_green()


class HelpDBCog(commands.Cog):
    """
    Cog for handling HelpDBCog commands.
    """

    def __init__(self, bot: "Bot"):
        """
        Initializes the HelpDBCog class.
        Args:
          bot (Bot): The bot instance.
        """
        self.bot = bot

    @commands.hybrid_command()
    async def helpdb(self, ctx: commands.Context):
        """
        Sends a help message for the helpdb commands.
        Args:
          ctx (commands.Context): The context of the command.
        Returns:
          None
        Side Effects:
          Sends a help message to the user.
        Notes:
          The command is only available in the AI text-chat category.
        Examples:
          >>> helpdb
          Sends a help message for the helpdb commands.
        """
        channel = ctx.channel
        if channel.category.id != self.bot.chatbot_category_id:
            await ctx.send(
                "Please use this command in the 'AI' text-chat category.",
                ephemeral=True,
            )
            return
        log_debug(self.bot, f"Helpdb command used by user: {ctx.author.id}")
        await ctx.defer(ephemeral=True)
        embed = discord.Embed(title="Chatbot db Help", color=embed_color)
        embed.set_author(
            name="GitHub [Click Here]",
            url="https://github.com/AntonOsika/gpt-engineer",
            icon_url="https://cdn.discordapp.com/attachments/1114412425115086888/1114413065933439058/25231.png",
        )
        embed.add_field(name="/helpdb", value="This help message.", inline=True)
        embed.add_field(
            name="/ingestdb",
            value="Ingest a readthedb.io documentation website.",
            inline=True,
        )
        embed.add_field(
            name="/listdb",
            value="View a list of your ingested documentation websites.",
            inline=True,
        )
        embed.add_field(
            name="/deletedb",
            value="Delete an ingested documentation website from the list.",
            inline=True,
        )
        embed.add_field(
            name="/askdb",
            value="Ask about an ingested documentation website.",
            inline=True,
        )
        await ctx.send(embed=embed, ephemeral=True)


async def setup(bot: "Bot") -> None:
    """Loads the cog."""
    try:
        await bot.add_cog(HelpDBCog(bot))
        log_debug(bot, "HelpDBCog loaded.")
    except Exception as e:
        log_error(bot, f"Error loading HelpDBCog: {e}")
