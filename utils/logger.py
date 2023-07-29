import asyncio
import logging
import os
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING

from utils.terminal import TerminalCommands

if TYPE_CHECKING:
    from discord_bot.bot import Bot


class Logger(logging.Logger):
    """
    Sets up the Logger class.
    Args:
      name (str): The name of the logger.
      log_file (Path): The path to the log file.
      level (str): The logging level.
      maxBytes (int): The maximum size of the log file.
      backupCount (int): The number of log files to keep.
    Returns:
      None
    Examples:
      >>> logger = Logger('my_logger', log_file='/path/to/log.log', level='INFO', maxBytes=1000000, backupCount=1)
    """

    def __init__(
        self,
        name: str,
        log_file: Path,
        level="INFO",
        maxBytes: int = 1000000,
        backupCount: int = 1,
    ):
        """
        Initializes the Logger class.
        Args:
          name (str): The name of the logger.
          log_file (Path): The path to the log file.
          level (str): The logging level.
          maxBytes (int): The maximum size of the log file.
          backupCount (int): The number of log files to keep.
        Returns:
          None
        Examples:
          >>> logger = Logger('my_logger', log_file='/path/to/log.log', level='INFO', maxBytes=1000000, backupCount=1)
        """
        super().__init__(name, level)
        """Sets up the Logger class"""
        self.log_file = log_file
        self.name = name
        self.level = level  # type: ignore
        self.maxBytes = maxBytes
        self.backupCount = backupCount
        self.setup_logger()

    def setup_logger(self):
        """
        Sets up the logger.
        Args:
          None
        Returns:
          None
        Examples:
          >>> logger.setup_logger()
        """
        file_handler = LoggerRotator(
            log_file=self.log_file, maxBytes=self.maxBytes, backupCount=self.backupCount
        )

        file_handler.setFormatter(LoggerFormat())
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(LoggerFormat())

        self.setLevel(self.level)
        file_handler.setLevel(self.level)
        console_handler.setLevel(self.level)

        self.addHandler(file_handler)
        self.addHandler(console_handler)


class LoggerFormat(logging.Formatter):
    """
    Formats the log messages.
    Args:
      record (logging.LogRecord): The log record to format.
    Returns:
      str: The formatted log message.
    Examples:
      >>> formatter = LoggerFormat()
      >>> formatter.format(logging.LogRecord('my_logger', logging.INFO, 'my_message'))
      '(black)2020-09-09 12:00:00(reset) (levelcolor)INFO     (black)[(reset)(purple)GPT-Engineer-Bot(black)] >(reset) my_message'
    """

    black = "\x1b[30m"
    red = "\x1b[31m"
    purple = "\x1b[35m"
    cyan = "\x1b[36m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    gray = "\x1b[38m"
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: cyan + bold,
        logging.INFO: green + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red + bold,
        logging.CRITICAL: red + bold,
    }

    def format(self, record: logging.LogRecord):
        """
        Formats the log messages.
        Args:
          record (logging.LogRecord): The log record to format.
        Returns:
          str: The formatted log message.
        Examples:
          >>> formatter = LoggerFormat()
          >>> formatter.format(logging.LogRecord('my_logger', logging.INFO, 'my_message'))
          '(black)2020-09-09 12:00:00(reset) (levelcolor)INFO     (black)[(reset)(purple)GPT-Engineer-Bot(black)] >(reset) my_message'
        """
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname: <8}(black)[(reset)(purple)GPT-Engineer-Bot(black)] >(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(gray)", self.gray + self.bold)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(purple)", self.purple + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


class LoggerRotator(RotatingFileHandler):
    """
    Rotates the log files.
    Args:
      log_file (Path): The path to the log file.
      mode (str): The mode to open the log file in.
      maxBytes (int): The maximum size of the log file.
      backupCount (int): The number of log files to keep.
      encoding (str): The encoding of the log file.
    Returns:
      None
    Examples:
      >>> logger_rotator = LoggerRotator(log_file='/path/to/log.log', mode='a', maxBytes=0, backupCount=0, encoding=None)
    """

    def __init__(
        self, log_file: Path, mode="a", maxBytes=0, backupCount=0, encoding=None
    ):
        """
        Initializes the LoggerRotator class.
        Args:
          log_file (Path): The path to the log file.
          mode (str): The mode to open the log file in.
          maxBytes (int): The maximum size of the log file.
          backupCount (int): The number of log files to keep.
          encoding (str): The encoding of the log file.
        Returns:
          None
        Examples:
          >>> logger_rotator = LoggerRotator(log_file='/path/to/log.log', mode='a', maxBytes=0, backupCount=0, encoding=None)
        """
        self.log_file = log_file

        if os.path.isfile(self.log_file):
            if os.path.isfile(os.path.join(os.path.dirname(self.log_file), "old.log")):
                os.remove(os.path.join(os.path.dirname(self.log_file), "old.log"))

            os.rename(
                self.log_file, os.path.join(os.path.dirname(self.log_file), "old.log")
            )

        super().__init__(log_file, mode, maxBytes, backupCount, encoding)
        self.mode = mode
        self.backupCount = backupCount
        self.encoding = encoding

    def emit(self, record: logging.LogRecord):
        """
        Writes the log message to the log file.
        Args:
          record (logging.LogRecord): The log record to write.
        Returns:
          None
        Examples:
          >>> logger_rotator.emit(logging.LogRecord('my_logger', logging.INFO, 'my_message'))
        """
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

        try:
            msg = self.format(record)
            msg = ansi_escape.sub("", msg)
            with open(self.baseFilename, "a", encoding="utf-8") as f:
                f.write(msg + self.terminator)

        except Exception:
            self.handleError(record)


# Extra logging functions


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
    green = LoggerFormat.green
    black = LoggerFormat.black
    purple = LoggerFormat.purple
    bold = LoggerFormat.bold
    reset = LoggerFormat.reset

    if bot.running:
        await asyncio.sleep(launch_delay)

    while bot.running:
        await asyncio.sleep(delay)
        terminal_format = f"{bold}{green}{owner_name}{reset}{bold}{black}@{reset}{bold}{purple}{bot_name}{reset}"
        terminal_prompt = f"{terminal_format}{black}{bold}: > {reset}"

        terminal_command = loop.run_in_executor(None, input, terminal_prompt)

        command_handler = TerminalCommands(bot, await terminal_command)
        await command_handler.handle_terminal_command()


async def welcome_to_bot(bot: "Bot") -> None:
    """
    Prints bot instance details and a welcome message.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> welcome_to_bot(bot)
      Bot Instance Details:
      Display name: BotName
      Presence: Playing a game
      Linked with Guild | ID: 123456789
      Bot is online and ready.
      Welcome to BotName!
      Be sure to check out the documentation at the GitHub repository.
      Type 'help' for a list of terminal commands.
    """
    bot_name = bot.config.get("bot_name")
    presence = bot.config.get("presence")
    owner_name = bot.config.get("owner_name")

    try:
        bot.log.debug("Starting welcome_to_bot function...")
        bot.log.info("Bot Instance Details:")
        bot.log.info(f"Display name: {bot_name}")
        bot.log.info(f"Presence: {presence}")

        for guild in bot.guilds:
            bot.log.info(f"Linked with {guild} | ID: {guild.id}")

        bot.log.info("Bot is online and ready.")

        if bot.config.get("update_bot") == False:
            bot.log.info(f"Welcome back to {bot_name}, {owner_name}!")
            bot.log.info("Type 'help' for a list of terminal commands.")
        else:
            bot.log.info(f"Welcome to {bot_name}!")
            bot.log.info(
                "Be sure to check out the documentation at the GitHub repository."
            )
            bot.log.info("Type 'help' for a list of terminal commands.")

    except Exception as e:
        bot.log.error(f"Error in welcome_to_bot function: {e}")


def log_debug(bot: "Bot", message: str) -> None:
    """
    Logs a debug message.
    Args:
      bot (Bot): The bot instance.
      message (str): The message to log.
    Returns:
      None
    Examples:
      >>> log_debug(bot, "Debug message")
      DEBUG: Debug message
    """
    bot.log.debug(message)


def log_error(bot: "Bot", message: str) -> None:
    """
    Logs an error message.
    Args:
      bot (Bot): The bot instance.
      message (str): The message to log.
    Returns:
      None
    Examples:
      >>> log_error(bot, "Error message")
      ERROR: Error message
    """
    bot.log.error(message)


def log_warning(bot: "Bot", message: str) -> None:
    """
    Logs a warning message.
    Args:
      bot (Bot): The bot instance.
      message (str): The message to log.
    Returns:
      None
    Examples:
      >>> log_warning(bot, "Warning message")
      WARNING: Warning message
    """
    bot.log.warning(message)


def log_info(bot: "Bot", message: str) -> None:
    """
    Logs an info message.
    Args:
      bot (Bot): The bot instance.
      message (str): The message to log.
    Returns:
      None
    Examples:
      >>> log_info(bot, "Info message")
      INFO: Info message
    """
    bot.log.info(message)
