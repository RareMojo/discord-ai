import sys
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from utils.mongo_db import MongoDBHandler
from utils.logger import log_debug, log_error

if TYPE_CHECKING:
    from discord_bot.bot import Bot

sys.path.append("../")
handler = MongoDBHandler("database")
embed_color = 0xFD7C42


class DeleteDocsCog(commands.Cog):
    """
    Cog for deleting docs.
    """

    def __init__(self, bot: "Bot"):
        """
        Initializes the DeleteDocsCog class.
        Args:
          bot (Bot): The bot instance.
        """
        self.bot = bot

    @commands.hybrid_command()
    async def deletedocs(self, ctx: commands.Context, docs_id: str):
        """
        Deletes a docs with the given ID.
        Args:
          ctx (commands.Context): The context of the command.
          docs_id (str): The ID of the docs to delete.
        Returns:
          None
        Examples:
          >>> deletedocs("12345")
          Successfully deleted!
          Docs name: <docs_name>
          Docs ID: 12345
        """
        channel = ctx.channel
        if channel.category.id != self.bot.chatbot_category_id:
            await ctx.send(
                "Please use this command in the chatbot category.", ephemeral=True
            )
            return
        await ctx.defer()
        embed = discord.Embed(title="Delete Docs", color=embed_color)
        try:
            log_debug(self.bot, f"Deleting docs with ID: {docs_id}")
            user_id = str(ctx.author.id)
            docs_name = handler.get_docs_name(user_id=user_id, docs_id=docs_id)
            r = handler.delete_docs(user_id=user_id, docs_id=docs_id)
            embed.add_field(
                name="Status",
                value=f"Successfully deleted!\n**Docs name:** `{docs_name}`\n**Docs ID:** `{docs_id}`",
                inline=True,
            )
        except ValueError as e:
            embed.add_field(name="Error", value=str(e), inline=True)
            log_error(self.bot, e)
        await ctx.send(embed=[embed])


async def setup(bot: "Bot") -> None:
    """Loads the cog."""
    try:
        await bot.add_cog(DeleteDocsCog(bot))
        log_debug(bot, "DeleteDocsCog loaded.")
    except Exception as e:
        log_error(bot, f"Error loading DeleteDocsCog: {e}")
