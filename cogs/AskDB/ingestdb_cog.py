import sys
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from utils.ingest import ingest
from utils.mongo_db import MongoDBHandler
from discord_bot.logger import log_debug, log_error, log_info

if TYPE_CHECKING:
    from discord_bot.bot import Bot

embed_color = 0xFD7C42
sys.path.append("../")
handler = MongoDBHandler("database")


class IngestDBCog(commands.Cog):
    """
    Cog for ingesting URLs.
    """

    def __init__(self, bot: "Bot"):
        """
        Initializes the IngestDBCog class.
        Args:
          bot (Bot): The Bot instance.
        """
        self.bot = bot

    @commands.hybrid_command()
    async def ingestdb(self, ctx: commands.Context, url: str, db_name: str):
        """
        Ingests a URL.
        Args:
          ctx (commands.Context): The context of the command.
          url (str): The URL to ingest.
          db_name (str): The name of the db.
        Returns:
          discord.Embed: An embed containing the result of the ingestion.
        Examples:
          >>> await ctx.send(embed=await ingestdb(ctx, 'https://example.com', 'Example db'))
          Embed containing the result of the ingestion.
        """
        channel = ctx.channel
        if channel.category.id != self.bot.chatbot_category_id:
            await ctx.send(
                "Please use this command in the chatbot category.", ephemeral=True
            )
            return
        await ctx.defer()
        try:
            try:
                random_uuid = str(uuid.uuid4())
                embed = discord.Embed(
                    title="Ingesting URL",
                    type="rich",
                    description=f"\n *This might take a while*",
                    color=embed_color,
                )
                await ctx.send(embed=embed, ephemeral=True)
                log_debug(
                    self.bot, f"Ingesting {url} as {db_name} for {ctx.author.name}"
                )
                await ingest(self.bot, url=url, namespace=random_uuid)
                current_time = datetime.now()
                handler.handle_data(
                    user_id=str(ctx.author.id),
                    user_name=str(ctx.author.name),
                    db_name=db_name,
                    db_id=random_uuid,
                    ingest_url=url,
                    ingested_time=current_time,
                )
                embed = discord.Embed(
                    title="Success",
                    description=f"{url}\n**DB Name:** `{db_name}`\n**DB ID:** `{random_uuid}`",
                    timestamp=current_time,
                    color=embed_color,
                )
                await ctx.send(embed=embed, ephemeral=True)
            except Exception as e:
                log_error(
                    self.bot,
                    f"Error ingesting {url} as {db_name} for {ctx.author.name}: {e}",
                )
                embed = discord.Embed(
                    title="Error", description=f"Error: {e}", color=embed_color
                )
            else:
                pass
        except Exception as e:
            log_error(
                self.bot,
                f"Error ingesting {url} as {db_name} for {ctx.author.name}: {e}",
            )
            embed = discord.Embed(
                title="Error", description=f"Error: {e}", color=embed_color
            )
            await ctx.send(embed=embed, ephemeral=True)


async def setup(bot: "Bot") -> None:
    """Loads the cog."""
    try:
        await bot.add_cog(IngestDBCog(bot))
        log_debug(bot, "IngestDBCog loaded.")
    except Exception as e:
        log_error(bot, f"Error loading IngestDBCog: {e}")
