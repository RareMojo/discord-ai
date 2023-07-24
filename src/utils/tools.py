import csv
import json
import os
import shutil
import subprocess
import tempfile
import traceback
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import discord
import requests

if TYPE_CHECKING:
    from discord_bot.bot import Bot


def get_new_config():
    """Collects inputs for a new config"""
    repo_owner = "RareMojo"
    repo_name = "YoBot-Discord-Cogs"
    repo_info = "cogdescriptions.csv"

    return {
        "owner_name": input('Owner Name: '),
        "prefix": input('Command Prefix: '),
        "bot_name": input('Bot Name: '),
        "presence": input('Presence: '),
        "persona": "Engi",
        "log_level": 'INFO',
        "blacklist": ["core_cog.py, commands_cog.py, chatgpt_cog.py"],
        "cog_repo": {
            "repo_owner": repo_owner,
            "repo_name": repo_name,
            "repo_info": repo_info,
        },
        "update_bot": True
    }


def update_config(config_file, new_data):
    """Updates the config file with new data."""
    with open(config_file, 'r') as file:
        config_data = json.load(file)

    config_data.update(new_data)

    with open(config_file, 'w') as file:
        updated_config = {**config_data, **new_data}
        json.dump(updated_config, file, indent=4)


async def update_with_discord(bot: 'Bot') -> None:
    """Updates bot's name, presence, and avatar to config values on Discord servers."""
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
            "This action is rate limited, so to change it later, edit the config file.")
        bot.log.warning(
            "You may also manually set these attributes with the terminal.")

        try:
            with open(bot.avatar_file, "rb") as f:
                new_avatar = f.read()
                await bot.user.edit(avatar=new_avatar)  # type: ignore
            activity = discord.Activity(type=discord.ActivityType.watching, name=presence)
            await bot.user.edit(username=bot_name)  # type: ignore
            await bot.change_presence(status=discord.Status.online, activity=activity)

        except Exception as e:
            bot.log.error("Error: {}".format(e))
            bot.log.error("Failed to synchronize bot settings with Discord.")
            bot.log.warning(
                "Bot name, avatar, or presence not changed on Discord servers.")
            bot.log.warning("This will be run again on next startup.")
            successful = False

        if successful == True:
            update = False
            bot.log.debug(
                "Successfully synchronized bot settings with Discord.")
            bot.config["update_bot"] = update

            with open(bot.config_file, "w") as f:
                json.dump(bot.config, f, indent=4)
    else:
        bot.log.info("Bot settings are up to date.")
        bot.log.info("Connected to Discord.")
    bot.log.debug("Exiting update_bot function...")


def get_boolean_input(bot: 'Bot', prompt: str) -> bool:
    """
    Returns a boolean input.

    Args:
        bot (bot): The bot instance.
        prompt (str): The prompt to display.
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


def download_cogs(bot: 'Bot', owner: str, repo: str, file_name: str):
    """
    Fetches a CSV file from a GitHub repository.

    Args:
        bot (bot): The bot instance.
        owner (str): The owner of the repo.
        repo (str): The name of the repo.
        file_name (str): The name of the file to fetch.

    Returns:
        list: The contents of the CSV file.
    """
    get_cogs = get_boolean_input(
        bot, "Would you like to download extra extensions? (y/n) ")

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
                row_num = input(
                    "Enter the row number of the extension to install: ")

                try:
                    row_num = int(row_num)
                    if row_num < 1 or row_num > len(rows):
                        raise ValueError
                except ValueError:
                    bot.log.error("Invalid row number.")
                    return []

                link = rows[row_num-1][headers.index("Repo")]
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
                    f"Error fetching {file_name}. Status code: {response.status_code}")
                return []

        except Exception as e:
            bot.log.error(f"Error fetching {file_name}: {e}")
            bot.log.debug(f"Error details: {traceback.format_exc()}")
            return []
    else:
        bot.log.info("Skipping extra extensions.")
        bot.log.info(
            "If you would like to install extra extensions, run the command 'getcogs'.")


def github_clone_repo(bot: 'Bot', repo: str, target_dir: Path):
    """
    Clones a GitHub repository.

    Args:
        bot (bot): The bot instance.
        repo (str): The GitHub repository to clone.
        target_dir (Path): The directory to clone the repository to.
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


