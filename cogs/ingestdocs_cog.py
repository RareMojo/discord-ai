import sys
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from utils.ingest_docs import ingest_docs
from utils.mongo_db import MongoDBHandler
from utils.logger import log_debug, log_error, log_info

if TYPE_CHECKING:
    from discord_bot.bot import Bot

embed_color = 0xFD7C42
sys.path.append("../")
handler = MongoDBHandler("database")


class IngestDocsCog(commands.Cog):
    """
    Cog for ingesting documentation URLs.
    """

    def __init__(self, bot: "Bot"):
        """
        Initializes the IngestDocsCog class.
        Args:
          bot (Bot): The Bot instance.
        """
        self.bot = bot

    @commands.hybrid_command()
    async def ingestdocs(self, ctx: commands.Context, url: str, docs_name: str):
        """
        Ingests a documentation URL.
        Args:
          ctx (commands.Context): The context of the command.
          url (str): The URL of the documentation to ingest.
          docs_name (str): The name of the documentation.
        Returns:
          discord.Embed: An embed containing the result of the ingestion.
        Examples:
          >>> await ctx.send(embed=await ingestdocs(ctx, 'https://example.com', 'Example Docs'))
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
                    title="Ingesting Documentation URL",
                    type="rich",
                    description=f"\n *This might take a while*",
                    color=embed_color,
                )
                await ctx.send(embed=embed)
                log_debug(
                    self.bot, f"Ingesting {url} as {docs_name} for {ctx.author.name}"
                )
                await ingest_docs(self.bot, url=url, namespace=random_uuid)
                current_time = datetime.now()
                handler.handle_data(
                    user_id=str(ctx.author.id),
                    user_name=str(ctx.author.name),
                    docs_name=docs_name,
                    docs_id=random_uuid,
                    ingest_url=url,
                    ingested_time=current_time,
                )
                embed = discord.Embed(
                    title="Success",
                    description=f"{url}\n**Docs Name:** `{docs_name}`\n**Docs ID:** `{random_uuid}`",
                    timestamp=current_time,
                    color=embed_color,
                )
                await ctx.send(embed=embed)
            except Exception as e:
                log_error(
                    self.bot,
                    f"Error ingesting {url} as {docs_name} for {ctx.author.name}: {e}",
                )
                embed = discord.Embed(
                    title="Error", description=f"Error: {e}", color=embed_color
                )
            else:
                pass
        except Exception as e:
            log_error(
                self.bot,
                f"Error ingesting {url} as {docs_name} for {ctx.author.name}: {e}",
            )
            embed = discord.Embed(
                title="Error", description=f"Error: {e}", color=embed_color
            )
            await ctx.send(embed=embed)


async def setup(bot: "Bot") -> None:
    """Loads the cog."""
    try:
        await bot.add_cog(IngestDocsCog(bot))
        log_debug(bot, "IngestDocsCog loaded.")
    except Exception as e:
        log_error(bot, f"Error loading IngestDocsCog: {e}")
