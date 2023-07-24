import json
import os
from pathlib import Path

from discord import Intents

from discord_bot.bot import Bot
from utils.db import DBs
from utils.logger import Logger
from utils.tools import download_cogs, get_new_config


class BuildBot(Bot):
    """
    The Builder class is used to build a new instance of the bot class.

    Attributes:
        dbs (DBs): The bot's databases.
    """
    def __init__(self, dbs: DBs):
        self.dbs = dbs
        self.log_file = self.dbs.logs.path / "latest.log"
        self.cogs_dir = self.dbs.cogs.path


    def __setup_logger__(self, config: dict):
        """Sets up the logger."""

        text_logo_file = self.dbs.assets.path / "texts" / "logo.txt"
        if config.get("log_level") is None:
            self.level = "INFO"

        else:
            self.level = config.get("log_level") or "INFO"

        try:
            if not os.path.isfile(self.log_file):
                with open(self.log_file, "w") as f:
                    f.write("")

            self.log = Logger(name="bot", log_file=self.log_file,
                              level=self.level, maxBytes=1000000, backupCount=1)

        except OSError as e:
            raise e

        try:
            with open(text_logo_file, "r") as logo:
                text_logo = logo.read()

        except OSError as e:
            raise e

        green = "\033[92m"
        reset = "\033[0m"
        self.log.info("\n" + green + text_logo + reset + "\n")


    def __setup_cogs__(self, config: dict, cogs_dir: Path):
        """Downloads the selected cogs from the bot repository if the option is selected."""
        self.log.info("Setting up cogs...")

        try:
            self.log.debug("Checking for cogs directory...")

            if not os.path.isdir(cogs_dir):
                self.log.debug(
                    "Cogs directory not found. Creating cogs directory...")
                os.mkdir(cogs_dir)
            else:
                self.log.debug("Cogs directory found.")

                update = config.get("update_bot", False)

                if update:
                    self.log.debug("Updating cogs...")
                    download_cogs(self, config['cog_repo']['repo_owner'],
                                  config['cog_repo']['repo_name'], config['cog_repo']['repo_info'])
                    self.log.info("Cogs updated.")

        except FileNotFoundError as e:
            self.log.error("Cogs directory not found.", e)
        except Exception as e:
            self.log.error("Error setting up cogs.", e)


    def __make_config__(self, config_path: Path):
        """Creates a new config file if one is not found."""
        new_config = None

        if not os.path.isfile(config_path):
            print("Config file not found. Creating config file...")
            new_config = get_new_config()
        else:
            print("Config file found. Checking for missing config values...")

            with open(config_path, 'r') as f:
                config = json.load(f)

            new_config = config

        with open(config_path, 'w') as f:
            json.dump(new_config, f, indent=4)

        print("Config file updated.")


    def build_bot(self):
        """
        The build method builds a new instance of the bot class.

        Returns:
            bot: A newly prepared instance of the bot class.
        """
        config = self.dbs.configs.path / "config.json"
        self.__make_config__(config)

        with open(self.dbs.configs.path / "config.json", 'r') as f:
            self.config = json.load(f)
        self.__setup_logger__(self.config)
        self.__setup_cogs__(self.config, self.cogs_dir)

        self.log.info("Building bot...")
        intents = Intents.default()
        intents.message_content = True
        intents.members = True
        return Bot(
            intents=intents,
            dbs=self.dbs,
            logger=self.log
        )
