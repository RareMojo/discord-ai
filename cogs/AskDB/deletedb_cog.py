import sys
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from utils.mongo_db import MongoDBHandler
from discord_bot.logger import log_debug, log_error, log_info

if TYPE_CHECKING:
    from discord_bot.bot import Bot


embed_color_pending = 0xFD7C42
embed_color_success = discord.Color.brand_green()
embed_color_failure = discord.Color.brand_red()

sys.path.append("../")
handler = MongoDBHandler("askdb")



class DeleteDBCog(commands.Cog):
    """
    Cog for deleting DBs.
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
        Deletes a DB with the given ID.
        Args:
        ctx (commands.Context): The context of the command.
        db_id (str): The ID of the DB to delete.
        Returns:
        None
        Examples:
        >>> deletedb("12345")
        Successfully deleted!
        db name: <db_name>
        db ID: 12345
        """
        channel = ctx.channel
        allowed_roles = ["Contributor", "Moderator", "Administrator", "Developer", "Head Developer", "Super Admin", "BOT"]
        author_roles = [role.name for role in ctx.author.roles]
        
        if not any(role in allowed_roles for role in author_roles):
            await ctx.send(embed=discord.Embed(title="Error", color=embed_color_failure, description="You do not have permission to use this command."), ephemeral=True)
            return
        
        if channel.category.id != self.bot.chatbot_category_id:
            await ctx.send(embed=discord.Embed(title="Error", color=embed_color_failure, description="Please use this command in the 'AI' text-chat category."), ephemeral=True)
            return

        if not handler.check_exists(db_id=db_id):
            await ctx.send(embed=discord.Embed(title="Error", color=embed_color_failure, description="The DB ID you provided does not exist."), ephemeral=True)
            return
        await ctx.defer(ephemeral=True)
        user_id = str(ctx.author.id)
        r = handler.delete_db(user_id=user_id, db_id=db_id)
        if r:
            db_name = handler.get_db_name(user_id=user_id, db_id=db_id)
            log_debug(self.bot, f"Successfully deleted DB with ID: {db_id}")
            embed = discord.Embed(title="Status", color=embed_color_success)
            embed.add_field(
                name="Status",
                value=f"Successfully deleted!\n**DB name:** `{db_name}`\n**DB ID:** `{db_id}`",
                inline=True,
            )
        else:
            log_debug(self.bot, f"DB with ID {db_id} not found.")
            embed = discord.Embed(title="Error", color=embed_color_failure)
            embed.add_field(
                name="Error",
                value=f"DB with ID {db_id} not found. No action was taken.",
                inline=True,
            )
        await ctx.send(embed=embed)


async def setup(bot: "Bot") -> None:
    """Loads the cog."""
    try:
        await bot.add_cog(DeleteDBCog(bot))
        log_debug(bot, "DeleteDBCog loaded.")
    except Exception as e:
        log_error(bot, f"Error loading DeleteDBCog: {e}")
