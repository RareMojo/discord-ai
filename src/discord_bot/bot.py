import asyncio
import json
import os
from typing import TYPE_CHECKING

from discord.ext import commands
from dotenv import load_dotenv

from utils.db import DBs
from utils.logger import terminal_command_loop

load_dotenv()

CHATBOT_CATEGORY_ID = int(os.getenv("CHATBOT_CATEGORY_ID", 0))
CHATBOT_THREADS_ID = int(os.getenv("CHATBOT_THREADS_ID", 0))
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

if TYPE_CHECKING:
    from discord import Intents

    from utils.logger import Logger


class Bot(commands.Bot):
    """Main Bot class that handles the bot's initialization and startup.

    Attributes:
        intents (discord.Intents): The bot's intents.
        dbs (DBs): The bot's databases.
        logger (Logger): The bot's logger.
    """
    def __init__(self, intents: 'Intents', dbs: DBs, logger: 'Logger'):
        self.log = logger
        self.log.debug("Bot built.")
        self.dbs = dbs
        self.config_file = dbs.configs.path / "config.json"
        self.avatar_file = dbs.assets.path / "images" / "avatar.png"
        self.cogs_dir = dbs.cogs.path
        self.guild_id = int(GUILD_ID) if GUILD_ID else None
        self.owner_id = int(OWNER_ID) if OWNER_ID else None
        self.chatbot_category_id = CHATBOT_CATEGORY_ID
        self.chatbot_threads_id = CHATBOT_THREADS_ID
        self.discord_token = str(DISCORD_TOKEN)
        self.openai_api_key = str(OPENAI_API_KEY)
        self.openai_model = str(OPENAI_MODEL)
        

        with open(self.config_file, "r") as f:
            self.config = json.load(f)

        self.display_name = self.config.get("bot_name")

        super().__init__(command_prefix=self.config.get("prefix"), intents=intents)
        self.log.debug("Bot initialized.")
        self.running = True

    async def start_bot(self):
        """Starts bot."""
        self.log.info("Bot starting...")
        await self.load_cogs()

        bot_task = asyncio.create_task(
            self.start(self.discord_token), name="bot")
        command_task = asyncio.create_task(
            terminal_command_loop(self), name="terminal")

        try:
            while self.running:
                await asyncio.sleep(0)

        except Exception as e:
            self.log.error(f"Bot encountered an error: {e}")

        finally:
            bot_task.cancel()
            command_task.cancel()

    def stop_bot(self):
        """Stops bot."""
        self.log.info("Bot stopping...")
        self.running = False

    async def load_cogs(self):
        """Loads all cogs in the cogs directory."""
        self.log.debug("Loading cogs...")
        loaded_extensions = 0
        cog_name = None
        try:
            for filename in os.listdir(self.cogs_dir):
                if filename.endswith("cog.py"):
                    cog_name = f"cogs.{filename[:-3]}"
                    if cog_name in self.extensions:
                        self.log.debug(
                            f"Skipping - [ {filename[:-3]} ] (already loaded)")
                        continue
                    await self.load_extension(cog_name)
                    self.log.debug(f"Loaded - [ {filename[:-3]} ]")
                    loaded_extensions += 1
        except Exception as e:
            raise e
        self.log.debug(f"Loaded {loaded_extensions} cogs.")
