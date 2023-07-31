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
embed_color = discord.Color.blurple()


class ListDBCog(commands.Cog):
    """
    Cog for listing documents.
    """

    def __init__(self, bot: "Bot"):
        """
        Initializes the ListDBCog class.
        Args:
          bot (Bot): The bot instance.
        """
        self.bot = bot

    @commands.hybrid_command()
    async def listdb(self, ctx: commands.Context):
        """
        Lists all documents for a user.
        Args:
          ctx (commands.Context): The context of the command.
        Returns:
          None
        Side Effects:
          Sends an embed with the list of documents.
        Notes:
          The command must be used in the chatbot category.
        Examples:
          >>> listdb
          Sends an embed with the list of documents.
        """
        channel = ctx.channel
        if channel.category.id != self.bot.chatbot_category_id:
            await ctx.send(
                "Please use this command in the chatbot category.", ephemeral=True
            )
            return
        await ctx.defer()
        db_list = handler.list_db(user_id=str(ctx.author.id))
        embed = discord.Embed(title="db", color=embed_color)
        try:
            log_debug(self.bot, f"Listing DBs: {ctx.author.id}")
            for db in db_list:
                db_name = db["db_name"]
                db_id = db["db_id"]
                ingested_url = db["ingested_url"]
                ingested_time = db["ingested_time"]
                embed.add_field(
                    name=db_name,
                    value=f"{ingested_url}\n**DB ID:** `{db_id}`\n**Time Ingested:** `{ingested_time}`",
                    inline=False,
                )
        except Exception as e:
            embed.add_field(name="Error", value="No DB Found", inline=True)
            log_error(self.bot, e)
        await ctx.send(embed=embed)


async def setup(bot: "Bot") -> None:
    """Loads the cog."""
    try:
        await bot.add_cog(ListDBCog(bot))
        log_debug(bot, "ListDBCog loaded.")
    except Exception as e:
        log_error(bot, f"Error loading ListDBCog: {e}")
