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
embed_color = discord.Color.blurple()


class ListDocsCog(commands.Cog):
    """
    Cog for listing documents.
    """

    def __init__(self, bot: "Bot"):
        """
        Initializes the ListDocsCog class.
        Args:
          bot (Bot): The bot instance.
        """
        self.bot = bot

    @commands.hybrid_command()
    async def listdocs(self, ctx: commands.Context):
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
          >>> listdocs
          Sends an embed with the list of documents.
        """
        channel = ctx.channel
        if channel.category.id != self.bot.chatbot_category_id:
            await ctx.send(
                "Please use this command in the chatbot category.", ephemeral=True
            )
            return
        await ctx.defer()
        docs_list = handler.list_docs(user_id=str(ctx.author.id))
        embed = discord.Embed(title="Docs", color=embed_color)
        try:
            log_debug(self.bot, f"Listing docs for user: {ctx.author.id}")
            for docs in docs_list:
                docs_name = docs["docs_name"]
                docs_id = docs["docs_id"]
                ingested_url = docs["ingested_url"]
                ingested_time = docs["ingested_time"]
                embed.add_field(
                    name=docs_name,
                    value=f"{ingested_url}\n**ID:** `{docs_id}`\n**Time:** `{ingested_time}`",
                    inline=False,
                )
        except Exception as e:
            embed.add_field(name="Error", value="No Docs Found", inline=True)
            log_error(self.bot, e)
        await ctx.send(embed=embed)


async def setup(bot: "Bot") -> None:
    """Loads the cog."""
    try:
        await bot.add_cog(ListDocsCog(bot))
        log_debug(bot, "ListDocsCog loaded.")
    except Exception as e:
        log_error(bot, f"Error loading ListDocsCog: {e}")
