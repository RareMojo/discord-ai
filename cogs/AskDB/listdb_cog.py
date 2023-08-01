import discord
from discord.ext import commands
from utils.mongo_db import MongoDBHandler
from discord_bot.logger import log_debug, log_error, log_info
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord_bot.bot import Bot


embed_color_pending = 0xFD7C42
embed_color_success = discord.Color.brand_green()
embed_color_failure = discord.Color.brand_red()

sys.path.append("../")
handler = MongoDBHandler("askdb")
embed_color = discord.Color.brand_green()


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
        Lists all documents for a specific user.
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
            await ctx.send(embed=discord.Embed(title="Error", color=embed_color_failure, description="Please use this command in the 'AI' text-chat category."), ephemeral=True)
            return
          
        db_list = handler.list_db(user_id=str(ctx.author.id))
        if not db_list:
            await ctx.send(embed=discord.Embed(title="Error", color=embed_color_failure, description="You have no databases."), ephemeral=True)
            return

        try:
            log_debug(self.bot, f"Listing DBs for user: {ctx.author.id}")
            embed = discord.Embed(title="DB", color=embed_color)
            for db in db_list:
                db_name = db["db_name"]
                db_id = db["db_id"]
                ingested_url = db["ingested_url"]
                ingested_time = db["ingested_time"]
                embed.add_field(
                    name=db_name,
                    value=f"{ingested_url}\n**DB ID:** `{db_id}`\n**Time Ingested:** `{ingested_time}`",
                    inline=False
                )
        except Exception as e:
            embed = discord.Embed(title="Error", color=embed_color_failure, description="No DB Found", inline=True)
            log_error(self.bot, e)
        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command()
    async def listalldb(self, ctx: commands.Context):
        """
        Lists all documents for all users.
        Args:
          ctx (commands.Context): The context of the command.
        Returns:
          None
        Side Effects:
          Sends an embed with the list of documents.
        Notes:
          The command must be used in the chatbot category.
        Examples:
          >>> listalldb
          Sends an embed with the list of documents.
        """
        channel = ctx.channel
        if channel.category.id != self.bot.chatbot_category_id:
            await ctx.send(embed=discord.Embed(title="Error", color=embed_color_failure, description="Please use this command in the 'AI' text-chat category."), ephemeral=True)
            return
        await ctx.defer(ephemeral=True)
        db_list = handler.list_all_db()
        if not db_list:
            await ctx.send(embed=discord.Embed(title="Error", color=embed_color_failure, description="No databases found."), ephemeral=True)
            return
        try:
            log_debug(self.bot, f"Listing all DBs.")
            embed = discord.Embed(title="All DBs", color=embed_color)
            for db in db_list:
                db_name = db["db_name"]
                db_id = db["db_id"]
                ingested_url = db["ingested_url"]
                ingested_time = db["ingested_time"]
                user_id = db["user_id"]
                embed.add_field(
                    name=f"**Name:** {db_name}",
                    value=f"**User ID:** `{user_id}`\n{ingested_url}\n**DB ID:** `{db_id}`\n**Ingested at:** `{ingested_time}`",
                    inline=False
                )
        except Exception as e:
            embed = discord.Embed(title="Error", color=embed_color_failure, description="No DB Found", inline=True)
            log_error(self.bot, e)
        await ctx.send(embed=embed, ephemeral=True)


async def setup(bot: "Bot") -> None:
    """Loads the cog."""
    try:
        await bot.add_cog(ListDBCog(bot))
        log_debug(bot, "ListDBCog loaded.")
    except Exception as e:
        log_error(bot, f"Error loading ListDBCog: {e}")
