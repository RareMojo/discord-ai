import json
import re
import traceback
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from discord_bot.bot import Bot


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


def get_new_config():
    """
    Generates a new configuration dictionary.
    Args:
      None
    Returns:
      dict: A new configuration dictionary.
    Examples:
      >>> get_new_config()
      {
          "owner_name": "",
          "prefix": "",
          "bot_name": "",
          "presence": "",
          "persona": "Engi",
          "log_level": "INFO",
          "update_bot": True,
      }
    """
    return {
        "owner_name": input("Owner Name: "),
        "prefix": input("Command Prefix: "),
        "bot_name": input("Bot Name: "),
        "presence": input("Presence: "),
        "persona": input("Persona: "),
        "log_level": "INFO",
        "update_bot": True,
    }


def update_config(config_file, new_data):
    """
    Updates a configuration file with new data.
    Args:
      config_file (str): The path to the configuration file.
      new_data (dict): The new data to add to the configuration file.
    Returns:
      None
    Side Effects:
      Updates the configuration file with the new data.
    Examples:
      >>> update_config('config.json', {'update_bot': False})
    """
    with open(config_file, "r") as file:
        config_data = json.load(file)

    config_data.update(new_data)

    with open(config_file, "w") as file:
        updated_config = {**config_data, **new_data}
        json.dump(updated_config, file, indent=4)


async def update_with_discord(bot: "Bot") -> None:
    """
    Updates the bot's settings with Discord.
    Args:
      bot (Bot): The bot object.
    Returns:
      None
    Side Effects:
      Updates the bot's settings with Discord.
    Examples:
      >>> update_with_discord(bot)
    """
    successful = True
    bot.log.debug("Starting update_with_discord function...")
    bot.log.debug("Checking for updates to bot settings...")
    update = bot.config.get("update_bot")
    bot_name = bot.config.get("bot_name")
    presence = bot.config.get("presence")

    if update == True:
        bot.log.info("First run or changes detected!")
        bot.log.info("Setting name, presence, and avatar to config values.")
        bot.log.warning(
            "This action is rate limited, so to change it later, edit the config file."
        )
        bot.log.warning("You may also manually set these attributes with the terminal.")

        try:
            with open(bot.avatar_file, "rb") as f:
                new_avatar = f.read()
                await bot.user.edit(avatar=new_avatar)
            await bot.user.edit(username=bot_name)
            await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=presence))

        except Exception as e:
            bot.log.error("Error: {}".format(e))
            bot.log.error("Failed to synchronize bot settings with Discord.")
            bot.log.warning(
                "Bot name, avatar, or presence not changed on Discord servers."
            )
            bot.log.warning("This will be run again on next startup.")
            successful = False

        if successful == True:
            update = False
            bot.log.debug("Successfully synchronized bot settings with Discord.")
            bot.config["update_bot"] = update

            with open(bot.config_file, "w") as f:
                json.dump(bot.config, f, indent=4)
    else:
        bot.log.info("Bot settings are up to date.")
        bot.log.info("Connected to Discord.")
    bot.log.debug("Exiting update_bot function...")


def get_boolean_input(bot: "Bot", prompt: str) -> bool:
    """
    Gets a boolean input from the user.
    Args:
      bot (Bot): The bot object.
      prompt (str): The prompt to display to the user.
    Returns:
      bool: The boolean input from the user.
    Examples:
      >>> get_boolean_input(bot, 'Would you like to download extra extensions? (y/n) ')
      True
    """
    while True:
        try:
            user_input = input(prompt)

            if user_input.lower() in ["true", "t", "yes", "y"]:
                return True

            elif user_input.lower() in ["false", "f", "no", "n"]:
                return False

            else:
                bot.log.warning("Invalid input. Try again.")

        except Exception as e:
            bot.log.error(f"Error occurred while getting boolean input: {e}")
            bot.log.debug(f"Error details: {traceback.format_exc()}")
            bot.log.warning("Invalid input. Try again.")


def make_filepaths(paths: dict):
    """
    Creates file paths from a dictionary.
    Args:
      paths (dict): A dictionary of file paths.
    Returns:
      None
    Side Effects:
      Creates the file paths in the dictionary.
    Examples:
      >>> make_filepaths({'config': Path('config.json'), 'cogs': Path('cogs')})
    """
    for path in paths.values():
        if path.suffix:
            path.parent.mkdir(parents=True, exist_ok=True)
        else:
            path.mkdir(parents=True, exist_ok=True)
            

def clean_response(bot: 'Bot', user: str, response: str):
    """
    Removes labels from a response string.
    Args:
      bot (Bot): The Bot instance.
      user (str): The user's name.
      response (str): The response string.
    Returns:
      str: The response string with labels removed.
    Examples:
      >>> clean_response(bot, "User", "User: Hello")
      "Hello"
    """
    labels = [
        "System: ",
        "User: ",
        "Assistant: ",
        "[System]: ",
        "[User]: ",
        "[Assistant]: ",
        f"{bot.config.get('persona')}: ",
        f"[{bot.config.get('actor')}]: ",
        f"{user}: ",
        f"[{user}]: ",
    ]

    for label in labels:
        response = response.replace(label, "")

    return response


def split_chat(chat, max_chars=2000):
    """
    Splits a chat into chunks of a maximum length.
    Args:
      chat (str): The chat string.
      max_chars (int, optional): The maximum length of each chunk. Defaults to 2000.
    Returns:
      list: A list of chunks.
    Examples:
      >>> split_chat("Hello world!", 5)
      ["Hello", " worl", "d!"]
    """
    lines = chat.split("\n")
    chunks = []
    chunk = ""
    inside_code_block = False
    language = ""

    code_block_start_pattern = re.compile(r"^```[\s]*\w*")
    code_block_end_pattern = re.compile(r"^```$")

    def add_chunk(chunk):
        """
        Adds a chunk to a list of chunks.
        Args:
          chunk (str): The chunk to add.
          chunks (list): The list of chunks.
        Returns:
          None
        Side Effects:
          Adds the chunk to the list of chunks.
        Examples:
          >>> chunks = []
          >>> add_chunk("Hello", chunks)
          >>> chunks
          ["Hello"]
        """
        if chunk:
            chunks.append(chunk)

    for line in lines:
        if code_block_start_pattern.match(line):
            if not inside_code_block and chunk:
                add_chunk(chunk)
                chunk = ""
            inside_code_block = True
            language = line.strip("`").strip()

            if len(chunk) + len(line) + 1 > max_chars:
                add_chunk(chunk)
                chunk = ""
            chunk += line + "\n"
            continue

        elif code_block_end_pattern.match(line):
            inside_code_block = False

            if len(chunk) + len(line) + 1 > max_chars:
                add_chunk(chunk)
                chunk = ""
            chunk += line + "\n"
            add_chunk(chunk)
            chunk = ""
            continue

        if inside_code_block:
            if len(chunk) + len(line) + 1 > max_chars:
                chunk += "```\n"
                add_chunk(chunk)
                chunk = ""

                chunk += f"```{language}\n"
            chunk += line + "\n"
        else:
            if len(chunk) + len(line) + 1 > max_chars:
                add_chunk(chunk)
                chunk = ""
            chunk += line + "\n"

    add_chunk(chunk)

    return chunks