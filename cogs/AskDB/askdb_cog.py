import os
import sys
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from utils.ai import ChatQuery
from utils.mongo_db import MongoDBHandler
from discord_bot.logger import log_debug, log_error, log_info

if TYPE_CHECKING:
    from discord_bot.bot import Bot

sys.path.append("../")
handler = MongoDBHandler("database")
embed_color = discord.Color.blurple()


class AskDB(commands.Cog):
    """
    Cog for querying documents.
    """

    def __init__(self, bot: "Bot"):
        """
        Initializes the AskDB.
        Args:
          bot (Bot): The bot instance.
        """
        self.bot = bot

    @commands.hybrid_command()
    async def askdb(
        self,
        ctx: commands.Context,
        query: str,
        db_id: str = "2349f359-9c6e-4436-b707-af6492ddd2d7", # default to the db_id of gpt-engineer
        source: bool = False,
    ):  
        """
        Queries documents for a given query.
        Args:
          ctx (commands.Context): The context of the command.
          query (str): The query to search for.
          db_id (str): The ID of the documents to search.
        Returns:
          discord.Embed: An embed containing the query results.
        Examples:
          >>> await ctx.send(embed=askdb("What is GPT-Engineer?", "2349f359-9c6e-4436-b707-af6492ddd2d7"))
          Embed containing query results.
        """
        channel = ctx.channel
        if channel.category.id != self.bot.chatbot_category_id:
            await ctx.send(
                "Please use this command in the chatbot category.", ephemeral=True
            )
            return
        await ctx.defer(ephemeral=False)
        chat_history = []
        log_debug(self.bot, f"Query: {query}")
        try:
            chat_query = ChatQuery(self.bot, namespace=db_id)
            q = chat_query.query()
            result = q({"question": query, "chat_history": chat_history})
            source_documents = result["source_documents"]
            parsed_documents = []
            for doc in source_documents:
                parsed_doc = {
                    "page_content": doc.page_content,
                    "metadata": {
                        "author": doc.metadata.get("author", ""),
                        "creationDate": doc.metadata.get("creationDate", ""),
                        "creator": doc.metadata.get("creator", ""),
                        "file_path": doc.metadata.get("file_path", ""),
                        "format": doc.metadata.get("format", ""),
                        "keywords": doc.metadata.get("keywords", ""),
                        "modDate": doc.metadata.get("modDate", ""),
                        "page_number": doc.metadata.get("page_number", 0),
                        "producer": doc.metadata.get("producer", ""),
                        "source": doc.metadata.get("source", ""),
                        "subject": doc.metadata.get("subject", ""),
                        "title": doc.metadata.get("title", ""),
                        "total_pages": doc.metadata.get("total_pages", 0),
                        "trapped": doc.metadata.get("trapped", ""),
                    },
                }
                parsed_documents.append(parsed_doc)
            embed = discord.Embed(
                title="Query Results:",
                description=f'{result["answer"]}\n\n',
                color=embed_color,
            )

            if source == True:
                for i, doc in enumerate(parsed_documents, start=1):
                    source = doc['metadata']['source']
                    source_name = os.path.basename(source)
                    embed.add_field(
                        name=f"Source {i}", value=f'{source_name}', inline=True)

                source_count = len(parsed_documents)
                embed.set_footer(text=f"Total Sources: {source_count}")
            else:
                embed.add_field(name="Query:", value=f"**{query}**", inline=False)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error: {e}", ephemeral=False)
            log_error(self.bot, f"Error: {e}")


async def setup(bot: "Bot") -> None:
    """Loads the cog."""
    try:
        await bot.add_cog(AskDB(bot))
        log_debug(bot, "AskDB loaded.")
    except Exception as e:
        log_error(bot, f"Error loading AskDB: {e}")
