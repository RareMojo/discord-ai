import asyncio
from typing import TYPE_CHECKING

from utils.commands import (
    add_blacklist,
    exit_bot_terminal,
    list_cogs,
    ping,
    remove_blacklist,
    remove_cogs,
    set_bot_avatar,
    set_bot_name,
    set_bot_presence,
    set_owner,
    show_aliases,
    show_help,
    sync_commands,
    toggle_debug_mode,
    wipe_config,
)
from utils.tools import download_cogs

if TYPE_CHECKING:
    from discord_bot.bot import Bot


async def terminal_command_loop(bot: "Bot"):
    """
    Runs a loop to handle terminal commands.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> await terminal_command_loop(bot)
    """
    owner_name = bot.config.get("owner_name")
    bot_name = bot.config.get("bot_name")
    loop = asyncio.get_event_loop()
    delay = 0.25
    launch_delay = 3.5
    black = "\x1b[30m"
    red = "\x1b[31m"
    purple = "\x1b[35m"
    cyan = "\x1b[36m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    gray = "\x1b[38m"
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    if bot.running:
        await asyncio.sleep(launch_delay)

    while bot.running:
        await asyncio.sleep(delay)
        terminal_format = f"{bold}{green}{owner_name}{reset}{bold}{black}@{reset}{bold}{purple}{bot_name}{reset}"
        terminal_prompt = f"{terminal_format}{black}{bold}: > {reset}"

        terminal_command = loop.run_in_executor(None, input, terminal_prompt)

        command_handler = TerminalCommands(bot, await terminal_command)
        await command_handler.handle_terminal_command()

class TerminalCommands:
    """
    Initializes the TerminalCommands class.
    Args:
      bot (Bot): The bot instance.
      terminal_command (str): The terminal command to handle.
    """

    def __init__(self, bot: "Bot", terminal_command: str):
        """
        Initializes the TerminalCommands class.
        Args:
          bot (Bot): The bot instance.
          terminal_command (str): The terminal command to handle.
        """
        self.bot = bot
        self.repo = self.bot.config.get("cog_repo")
        self.repo_owner, self.repo_name, self.repo_info = (
            self.repo.get("repo_owner"),
            self.repo.get("repo_name"),
            self.repo.get("repo_info"),
        )
        self.terminal_command = terminal_command

    async def handle_terminal_command(self):
        """
        Handles the terminal command.
        Returns:
          None
        Side Effects:
          Executes the command specified by the terminal command.
        Examples:
          >>> handle_terminal_command("ping")
          Pinging...
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
            download_cogs(self.bot, self.repo_owner, self.repo_name, self.repo_info)
            await self.bot.load_cogs()
            self.bot.log.info("Reloaded all cogs.")
            self.bot.log.info(
                "You may need to resync with Discord to apply new commands."
            )
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
            self.bot.log.info(f"{user_command} is not a recognized command.")
