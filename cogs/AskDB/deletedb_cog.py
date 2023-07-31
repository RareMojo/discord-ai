import sys
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from utils.mongo_db import MongoDBHandler
from discord_bot.logger import log_debug, log_error, log_info

if TYPE_CHECKING:
    from discord_bot.bot import Bot

sys.path.append("../")
handler = MongoDBHandler("database")
embed_color = 0xFD7C42


class DeleteDBCog(commands.Cog):
    """
    Cog for deleting dbs.
    """

    def __init__(self, bot: "Bot"):
        """
        Initializes the DeleteDBCog class.
        Args:
          bot (Bot): The bot instance.
        """
        self.bot = bot

    @commands.hybrid_command()
    async def deletedb(self, ctx: commands.Context, db_id: str):
        """
        Deletes a db with the given ID.
        Args:
          ctx (commands.Context): The context of the command.
          db_id (str): The ID of the db to delete.
        Returns:
          None
        Examples:
          >>> deletedb("12345")
          Successfully deleted!
          db name: <db_name>
          db ID: 12345
        """
        channel = ctx.channel
        if channel.category.id != self.bot.chatbot_category_id:
            await ctx.send(
                "Please use this command in the chatbot category.", ephemeral=True
            )
            return
        await ctx.defer()
        embed = discord.Embed(title="Delete DB", color=embed_color)
        try:
            log_debug(self.bot, f"Deleting DB with ID: {db_id}")
            user_id = str(ctx.author.id)
            db_name = handler.get_db_name(user_id=user_id, db_id=db_id)
            r = handler.delete_db(user_id=user_id, db_id=db_id)
            embed.add_field(
                name="Status",
                value=f"Successfully deleted!\n**DB name:** `{db_name}`\n**DB ID:** `{db_id}`",
                inline=True,
            )
        except ValueError as e:
            embed.add_field(name="Error", value=str(e), inline=True)
            log_error(self.bot, e)
        await ctx.send(embed=[embed])


async def setup(bot: "Bot") -> None:
    """Loads the cog."""
    try:
        await bot.add_cog(DeleteDBCog(bot))
        log_debug(bot, "DeleteDBCog loaded.")
    except Exception as e:
        log_error(bot, f"Error loading DeleteDBCog: {e}")
