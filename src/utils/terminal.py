
from typing import TYPE_CHECKING

from utils.commands import (add_blacklist, exit_bot_terminal, list_cogs, ping,
                            remove_blacklist, remove_cogs, set_bot_avatar,
                            set_bot_name, set_bot_presence, set_owner,
                            show_aliases, show_help, sync_commands,
                            toggle_debug_mode, wipe_config)
from utils.tools import download_cogs

if TYPE_CHECKING:
    from discord_bot.bot import Bot


class TerminalCommands():
    """
    This class handles Logger terminal commands.
    These commands are meant to be uni-directional. 

    Args:
        bot (Bot): The Bot instance.
        terminal_command (str): The terminal command.
    """
    def __init__(self, bot: 'Bot', terminal_command: str):
        self.bot = bot
        self.repo = self.bot.config.get("cog_repo")
        self.repo_owner, self.repo_name, self.repo_info = self.repo.get(
            "repo_owner"), self.repo.get("repo_name"), self.repo.get("repo_info")
        self.terminal_command = terminal_command


    async def handle_terminal_command(self):
        """        
        Handles the terminal command.

        Do not call these from outside sources.

        Terminal -> External Application == GOOD!

        External Application -> Terminal == BAD!
        """
        user_command = self.terminal_command.lower()
        self.bot.log.info("Received command: {}".format(user_command))


        if user_command in ["exit", "quit", "shutdown"]:
            self.bot.log.debug("Exiting bot terminal...")
            exit_bot_terminal(self.bot)


        elif user_command in ["help", "h", "?"]:
            self.bot.log.debug("Showing help...")
            show_help(self.bot)


        elif user_command in ["ping", "p"]:
            self.bot.log.debug("Pinging...")
            ping(self.bot)


        elif user_command in ["setbotname", "setbot", "sbn"]:
            self.bot.log.debug("Setting bot name...")
            await set_bot_name(self.bot)


        elif user_command in ["setpresence", "setpres", "sp"]:
            self.bot.log.debug("Setting bot presence...")
            await set_bot_presence(self.bot)


        elif user_command in ["setavatar", "setava", "sa"]:
            self.bot.log.debug("Setting bot avatar...")
            await set_bot_avatar(self.bot)


        elif user_command in ["setowner", "setown"]:
            self.bot.log.debug("Setting owner...")
            await set_owner(self.bot)


        elif user_command in ["reload", "sync", "r"]:
            self.bot.log.debug("Syncing commands...")
            await sync_commands(self.bot)


        elif user_command in ["wipebot", "wipeconfig", "wipe", "wb"]:
            self.bot.log.debug("Wiping bot config...")
            wipe_config(self.bot)


        elif user_command in ["getcog", "getcogs", "gc"]:
            self.bot.log.debug("Downloading cogs...")
            download_cogs(self.bot, self.repo_owner,
                          self.repo_name, self.repo_info)
            await self.bot.load_cogs()
            self.bot.log.info("Reloaded all cogs.")
            self.bot.log.info(
                "You may need to resync with Discord to apply new commands.")
            await sync_commands(self.bot)


        elif user_command in ["removecog", "removecogs", "rc"]:
            self.bot.log.debug("Removing cogs...")
            remove_cogs(self.bot)


        elif user_command in ["listcogs", "list", "lc"]:
            self.bot.log.debug("Listing cogs...")
            list_cogs(self.bot)


        elif user_command in ["alias", "aliases", "a"]:
            self.bot.log.debug("Showing aliases...")
            show_aliases(self.bot)


        elif user_command in ["debug", "d"]:
            self.bot.log.debug("Toggling debug mode...")
            toggle_debug_mode(self.bot)


        elif user_command in ["addblacklist", "addbl", "abl"]:
            self.bot.log.debug("Adding to blacklist...")
            add_blacklist(self.bot)


        elif user_command in ["removeblacklist", "rmblist", "rmbl"]:
            self.bot.log.debug("Removing from blacklist...")
            remove_blacklist(self.bot)


        else:
            self.bot.log.info(
                f"{user_command} is not a recognized command.")
