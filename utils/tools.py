import csv
import json
import os
import re
import shutil
import subprocess
import tempfile
import traceback
from pathlib import Path
from typing import TYPE_CHECKING
import discord
import requests

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
          "blacklist": ["core_cog.py, commands_cog.py, chatgpt_cog.py"],
          "cog_repo": {
              "repo_owner": "RareMojo",
              "repo_name": "YoBot-Discord-Cogs",
              "repo_info": "cogdescriptions.csv",
          },
          "update_bot": True,
      }
    """
    repo_owner = "RareMojo"
    repo_name = "YoBot-Discord-Cogs"
    repo_info = "cogdescriptions.csv"

    return {
        "owner_name": input("Owner Name: "),
        "prefix": input("Command Prefix: "),
        "bot_name": input("Bot Name: "),
        "presence": input("Presence: "),
        "persona": "Engi",
        "log_level": "INFO",
        "blacklist": ["core_cog.py, commands_cog.py, chatgpt_cog.py"],
        "cog_repo": {
            "repo_owner": repo_owner,
            "repo_name": repo_name,
            "repo_info": repo_info,
        },
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
                await bot.user.edit(avatar=new_avatar)  # type: ignore
            activity = discord.Activity(
                type=discord.ActivityType.watching, name=presence
            )
            await bot.user.edit(username=bot_name)  # type: ignore
            await bot.change_presence(status=discord.Status.online, activity=activity)

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


def download_cogs(bot: "Bot", owner: str, repo: str, file_name: str):
    """
    Downloads extra extensions from a repository.
    Args:
      bot (Bot): The bot object.
      owner (str): The repository owner.
      repo (str): The repository name.
      file_name (str): The name of the file containing the extension information.
    Returns:
      list: A list of rows from the file.
    Examples:
      >>> download_cogs(bot, 'RareMojo', 'YoBot-Discord-Cogs', 'cogdescriptions.csv')
      [['core_cog', 'Core cog for YoBot', 'RareMojo', 'https://github.com/RareMojo/YoBot-Discord-Cogs/tree/master/core_cog'], ['commands_cog', 'Commands cog for YoBot', 'RareMojo', 'https://github.com/RareMojo/YoBot-Discord-Cogs/tree/master/commands_cog'], ['chatgpt_cog', 'ChatGPT cog for YoBot', 'RareMojo', 'https://github.com/RareMojo/YoBot-Discord-Cogs/tree/master/chatgpt_cog']]
    """
    get_cogs = get_boolean_input(
        bot, "Would you like to download extra extensions? (y/n) "
    )

    if get_cogs == True:
        try:
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/{file_name}"
            response = requests.get(url)

            if response.status_code == 200:
                bot.log.debug(f"{file_name} fetched.")
                csv_contents = response.text.splitlines()
                csv_reader = csv.reader(csv_contents)
                headers = next(csv_reader)
                rows = list(csv_reader)
                bot.log.debug(f"Loaded file {file_name}:")
                bot.log.info(f"{headers[0]} | {headers[1]} | {headers[2]}")

                for i, row in enumerate(rows):
                    bot.log.info(f"{i+1}: {row[0]}, {row[1]} Author: {row[2]}")
                row_num = input("Enter the row number of the extension to install: ")

                try:
                    row_num = int(row_num)
                    if row_num < 1 or row_num > len(rows):
                        raise ValueError
                except ValueError:
                    bot.log.error("Invalid row number.")
                    return []

                link = rows[row_num - 1][headers.index("Repo")]
                extension_name = link.split("/")[-1]

                try:
                    bot.log.info(f"Downloading {extension_name}...")
                    github_clone_repo(bot, link, bot.cogs_dir)

                except Exception as e:
                    bot.log.error(f"Error downloading {extension_name}: {e}")
                    return []

                bot.log.info(f"{extension_name} download successful.")
                return rows
            else:
                bot.log.error(
                    f"Error fetching {file_name}. Status code: {response.status_code}"
                )
                return []

        except Exception as e:
            bot.log.error(f"Error fetching {file_name}: {e}")
            bot.log.debug(f"Error details: {traceback.format_exc()}")
            return []
    else:
        bot.log.info("Skipping extra extensions.")
        bot.log.info(
            "If you would like to install extra extensions, run the command 'getcogs'."
        )


def github_clone_repo(bot: "Bot", repo: str, target_dir: Path):
    """
    Clones a repository from GitHub.
    Args:
      bot (Bot): The bot object.
      repo (str): The repository URL.
      target_dir (Path): The target directory to clone the repository to.
    Returns:
      None
    Side Effects:
      Clones the repository to the target directory.
    Examples:
      >>> github_clone_repo(bot, 'https://github.com/RareMojo/YoBot-Discord-Cogs', Path('cogs'))
    """
    try:
        bot.log.debug(f"Cloning {repo} to {target_dir}...")

        with tempfile.TemporaryDirectory() as temp_dir:
            command = ["git", "clone", repo, temp_dir]
            subprocess.check_call(command)

            for filename in os.listdir(temp_dir):
                if filename == ".git":
                    continue

                src_file = os.path.join(temp_dir, filename)
                dst_file = target_dir / filename

                if dst_file.exists():
                    if dst_file.is_file() or dst_file.is_symlink():
                        dst_file.unlink()
                    else:
                        shutil.rmtree(str(dst_file))

                shutil.move(src_file, str(target_dir))

    except Exception as e:
        bot.log.error(f"Error cloning {repo}: {e}")
        bot.log.debug(f"Error details: {traceback.format_exc()}")
    else:
        bot.log.debug(f"Cloned {repo} to {target_dir}.")


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
                # Add the end delimiter for the current code block
                chunk += "```\n"
                add_chunk(chunk)
                chunk = ""

                # Start a new chunk with the correct language identifier
                chunk += f"```{language}\n"
            chunk += line + "\n"
        else:
            if len(chunk) + len(line) + 1 > max_chars:
                add_chunk(chunk)
                chunk = ""
            chunk += line + "\n"

    add_chunk(chunk)

    return chunks