import json
import logging
import os
import traceback
from typing import TYPE_CHECKING

import discord

from utils.tools import get_boolean_input, update_config

if TYPE_CHECKING:
    from discord_bot.bot import Bot


# Terminal Commands Functions


def add_blacklist(bot: "Bot") -> None:
    """
    Adds a cog to the blacklist.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Side Effects:
      Updates the config file.
    Examples:
      >>> add_blacklist(bot)
    """
    config_file = bot.config_file
    with open(config_file, "r") as f:
        config = json.load(f)

    try:
        edit_confirm = get_boolean_input(
            bot, "Are you sure you want to add to the blacklist? (y/n) "
        )
        if not edit_confirm:
            return
        else:
            cogs = list_cogs(bot)
            bot.log.info("Choose the cog to add to the blacklist:")

            cog_index = int(
                input("Enter the number of the cog you want to blacklist: ")
            )
            cog_name = cogs[cog_index - 1]
            blacklist = config.get("blacklist")

            if cog_name in blacklist:
                bot.log.warning(f"{cog_name} is already in the cog removal blacklist.")
                return

            blacklist.append(cog_name)

            try:
                new_data = {"blacklist": blacklist}
                update_config(config_file, new_data)

            except Exception as e:
                bot.log.debug(f"Failed to update the configuration file: {e}")
                return bot.log.warning("Failed to add to the cog removal blacklist.")

            bot.log.info(f"{cog_name} has been added to the cog removal blacklist.")

    except Exception as e:
        bot.log.debug(f"Failed to add to the cog removal blacklist: {e}")
        bot.log.warning("Failed to add to the cog removal blacklist.")


def remove_blacklist(bot: "Bot") -> None:
    """
    Removes a cog from the blacklist.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Side Effects:
      Updates the config file.
    Examples:
      >>> remove_blacklist(bot)
    """
    config_file = bot.config_file

    with open(config_file, "r") as f:
        config = json.load(f)

    try:
        edit_confirm = get_boolean_input(
            bot, "Are you sure you want to remove from the blacklist? (y/n) "
        )

        if not edit_confirm:
            return
        else:
            blacklist = config.get("blacklist")

            if not blacklist:
                bot.log.warning("The cog removal blacklist is empty.")
                return

            bot.log.info("Choose the cog to remove from the blacklist:")

            for i, cog_name in enumerate(blacklist):
                bot.log.info(f"{i+1}. {cog_name}")

            cog_index = int(input("Enter the number of the cog you want to remove: "))
            cog_name = blacklist[cog_index - 1]

            if cog_name not in blacklist:
                bot.log.warning(f"{cog_name} is not in the cog removal blacklist.")
                return

            blacklist.remove(cog_name)

            try:
                new_data = {"blacklist": blacklist}
                update_config(config_file, new_data)

            except Exception as e:
                bot.log.debug(f"Failed to update the configuration file: {e}")
                return bot.log.warning(
                    "Failed to remove the cog from the cog removal blacklist."
                )

            bot.log.info(f"{cog_name} has been removed from the cog removal blacklist.")

    except Exception as e:
        bot.log.debug(f"Failed to remove from the cog removal blacklist: {e}")
        bot.log.warning("Failed to remove from the cog removal blacklist.")


def toggle_debug_mode(bot: "Bot") -> None:
    """
    Toggles debug mode.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Side Effects:
      Updates the config file.
    Examples:
      >>> toggle_debug_mode(bot)
    """
    config_file = bot.config_file

    with open(config_file, "r") as f:
        config = json.load(f)

    try:
        if config.get("log_level") == "DEBUG":
            bot.log.info("Disabling debug mode...")

            try:
                new_data = {"log_level": "INFO"}
                update_config(config_file, new_data)

            except Exception as e:
                bot.log.debug(f"Failed to update the configuration file: {e}")
                return bot.log.warning("Failed to disable debug mode.")

            bot.log.info("Restarting to apply changes...")

        else:
            bot.log.info("Enabling debug mode...")

            try:
                new_data = {"log_level": "DEBUG"}
                update_config(config_file, new_data)

            except Exception as e:
                bot.log.debug(f"Failed to update the configuration file: {e}")
                return bot.log.warning("Failed to enable debug mode.")

            bot.log.setLevel(logging.DEBUG)
            bot.log.info("Restarting to apply changes...")

        input("Press ENTER to EXIT.")
        bot.stop_bot()

    except FileNotFoundError:
        bot.log.warning(f"Config file {bot.config} not found.")
    except KeyError:
        bot.log.warning(f"Key not found in config file {bot.config}.")
    except Exception as e:
        bot.log.warning(f"An error occurred while toggling debug mode: {e}")
    else:
        bot.log.debug("Debug mode toggled successfully.")


def remove_cogs(bot: "Bot") -> None:
    """
    Removes cogs from the cogs directory.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Side Effects:
      Removes cogs from the cogs directory.
    Examples:
      >>> remove_cogs(bot)
    """
    cogs_dir = bot.cogs_dir
    config_file = bot.config_file

    with open(config_file, "r") as f:
        config = json.load(f)

    bot.log.debug(f"Ignored cogs: {bot.config.get('blacklist')}")

    try:
        remove_cogs = get_boolean_input(bot, "Do you want to uninstall cogs? (y/n) ")
        successful = False

        if remove_cogs == True:
            remove_all = get_boolean_input(
                bot, "Do you want to uninstall all cogs at once? (y/n) "
            )

            if remove_all == True:
                confirm_remove_all = get_boolean_input(
                    bot, "Are you sure you want to uninstall all cogs? (y/n) "
                )

                if confirm_remove_all == True:
                    bot.log.info("Uninstalling all cogs...")

                    for file in os.listdir(cogs_dir):
                        if file.endswith("cog.py") and file not in config.get(
                            "blacklist"
                        ):
                            try:
                                os.remove(f"{cogs_dir}/{file}")
                                bot.log.debug(f"Removed {file} from {cogs_dir}")

                            except Exception as e:
                                bot.log.error(
                                    f"Error occurred while removing {file}: {e}"
                                )
                else:
                    bot.log.info("Cogs not uninstalled.")
            else:
                bot.log.info("Fetching the list of cogs from the cogs directory...")
                files = [
                    file
                    for file in os.listdir(cogs_dir)
                    if file.endswith("cog.py") and file not in config.get("blacklist")
                ]
                bot.log.debug(f"List of installed cogs: {files}")

                for i, file in enumerate(files, start=1):
                    bot.log.info(f"{i}. {file}")

                selected_cogs = input(
                    "Enter the numbers of the cogs you want to uninstall (separated by commas): "
                )
                selected_cogs = [int(num.strip()) for num in selected_cogs.split(",")]
                confirm_removal = get_boolean_input(
                    bot, "Are you sure you want to uninstall the selected cogs? (y/n) "
                )

                if confirm_removal == True:
                    successful = True
                    bot.log.info("Uninstalling selected cogs...")

                    for cog_index in selected_cogs:
                        cog_name = files[cog_index - 1]
                        try:
                            os.remove(f"{cogs_dir}/{cog_name}")
                            bot.log.debug(f"Removed {cog_name} from {cogs_dir}")
                            bot.log.info(f"{cog_name} uninstalled.")
                        except Exception as e:
                            bot.log.error(
                                f"Error occurred while removing {cog_name}: {e}"
                            )

                    if successful == True:
                        bot.log.info("Cogs uninstalled.")

                    list_cogs(bot)
                else:
                    bot.log.info("Cogs not uninstalled.")

    except FileNotFoundError:
        bot.log.warning(f"Config file {bot.config} not found.")
    except json.decoder.JSONDecodeError as e:
        bot.log.warning(f"Error loading config file {bot.config}: {e}")
    except Exception as e:
        bot.log.error(f"Error occurred while uninstalling cogs: {e}")


def list_cogs(bot: "Bot") -> list:
    """
    Lists the installed cogs.
    Args:
      bot (Bot): The bot instance.
    Returns:
      list: A list of installed cogs.
    Examples:
      >>> list_cogs(bot)
      ['cog1.py', 'cog2.py', 'cog3.py']
    """
    cogs_dir = bot.cogs_dir

    try:
        bot.log.debug(f"Fetching list of installed cogs from directory {cogs_dir}...")
        files = [file for file in os.listdir(cogs_dir) if file.endswith("cog.py")]

        if not files:
            bot.log.info("No cogs installed.")
            return []
        else:
            bot.log.info("List of installed cogs:")

            for i, file in enumerate(files, start=1):
                bot.log.info(f"{i}. {file}")

            bot.log.debug(
                f"List of installed cogs fetched successfully from directory {cogs_dir}."
            )
            return files

    except FileNotFoundError:
        bot.log.error(f"The directory {cogs_dir} does not exist.")
        return []
    except Exception as e:
        bot.log.error(
            f"An error occurred while fetching the list of installed cogs: {e}"
        )
        return []


def wipe_config(bot: "Bot") -> None:
    """
    Wipes the config file and shuts down the bot.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Side Effects:
      Wipes the config file and shuts down the bot.
    Examples:
      >>> wipe_config(bot)
    """
    try:
        bot.log.warning("This will wipe the config file and shut down Bot.")
        wipe = get_boolean_input(bot, "Do you want to wipe the config file? (y/n) ")

        if wipe == True:
            wipe_confirm = get_boolean_input(
                bot, "Are you sure you want to wipe config and restart? (y/n) "
            )

            if wipe_confirm == True:
                with open(bot.config_file, "w") as f:
                    f.write("")

                bot.log.info("Config file wiped.")
                bot.log.warning("Bot will now shut down.")
                exit_bot_terminal(bot)

            else:
                bot.log.info("Config file not wiped.")

        else:
            bot.log.info("Config file not wiped.")

    except FileNotFoundError as e:
        bot.log.debug(f"Config file not found: {e}")
    except Exception as e:
        bot.log.error(f"An error occurred while wiping the config file: {e}")


def exit_bot_terminal(bot: "Bot") -> None:
    """
    Shuts down the bot.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> exit_bot_terminal(bot)
    """
    try:
        bot.log.debug("Shutting down Bot...")
        bot.stop_bot()
    except Exception as e:
        bot.log.error(f"Error shutting down Bot: {e}")


async def set_bot_name(bot: "Bot") -> None:
    """
    Sets the bot name.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> await set_bot_name(bot)
    """
    config_file = bot.config_file

    with open(config_file, "r") as f:
        config = json.load(f)

    try:
        bot.log.debug("Setting bot name...")
        bot.log.info(f"Current name: {config.get('bot_name')}")
        change_bot_name = get_boolean_input(
            bot, "Do you want to change the bot name? (y/n) "
        )

        if change_bot_name == True:
            new_name = input("Enter new bot name: ")

            try:
                await bot.user.edit(username=new_name)  # type: ignore
                bot.log.info(
                    "Config change, bot_name: {} -> {}".format(
                        config.get("bot_name"), new_name
                    )
                )

                with open(bot.config_file, "w") as f:
                    config.set("bot_name", new_name)
                    config.write(f)

            except Exception as e:
                bot.log.error("Error: {}".format(e))
                bot.log.warning("Bot name not changed on Discord servers.")
        else:
            bot.log.info("Name not changed.")

    except Exception as e:
        bot.log.error("Error: {}".format(e))
        traceback.print_exc()


async def set_bot_avatar(bot: "Bot") -> None:
    """
    Sets the bot avatar.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> await set_bot_avatar(bot)
    """
    try:
        config_file = bot.config_file
        bot.log.debug("Setting bot avatar...")
        bot.log.info(
            "This sets the avatar to the image at ../resources/images/avatar.png"
        )
        change_avatar = get_boolean_input(
            bot, "Do you want to change the avatar? (y/n) "
        )
        successful = True

        with open(bot.avatar_file, "rb") as f:
            new_avatar = f.read()

        if change_avatar == True:
            try:
                await bot.user.edit(avatar=new_avatar)  # type: ignore
            except Exception as e:
                bot.log.error("Error: {}".format(e))
                bot.log.warning("Avatar not changed on Discord servers.")
                bot.log.warning("It will automatically be changed on the next startup.")
                successful = False

            if successful == True:
                try:
                    new_data = {"update_bot": True}
                    update_config(config_file, new_data)
                except Exception as e:
                    bot.log.debug(f"Failed to update the configuration file: {e}")
                    return bot.log.warning("Failed to set update flag.")

            if successful == True:
                bot.log.info("Avatar changed.")
        else:
            bot.log.info("Avatar not changed.")

    except Exception as e:
        bot.log.error("Error: {}".format(e))


async def set_bot_presence(bot: "Bot") -> None:
    """
    Sets the bot presence.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> await set_bot_presence(bot)
    """
    try:
        config_file = bot.config_file
        with open(config_file, "r") as f:
            config = json.load(f)

        bot.log.info("Current presence: {}".format(config.get("presence")))
        update_presence = get_boolean_input(
            bot, "Do you want to change the presence? (y/n) "
        )

        if update_presence == True:
            new_presence = input("Enter new presence: ")

            try:
                new_data = {"update_bot": True, "presence": new_presence}
                update_config(config_file, new_data)

            except Exception as e:
                bot.log.debug(f"Failed to update the configuration file: {e}")
                return bot.log.warning("Failed to set update flag.")

            try:
                # Try to change the presence on Discord servers.
                await bot.change_presence(activity=discord.Game(name=new_presence))
                bot.log.info(
                    "Config change, presence: {} -> {}".format(
                        config.get("presence"), new_presence
                    )
                )

            except Exception as e:
                bot.log.error("Error: {}".format(e))
                bot.log.warning("Presence not changed.")
        else:
            bot.log.info("Presence not changed.")

    except Exception as e:
        bot.log.debug(f"Error in set_bot_presence: {traceback.format_exc()}")
        bot.log.error(f"Error in set_bot_presence: {e}")


async def sync_commands(bot: "Bot") -> None:
    """
    Synchronizes commands with Discord.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> await sync_commands(bot)
    """
    bot.log.debug("Synchronizing commands...")

    try:
        config = bot.config
        bot.log.debug("Synchronizing commands...")
        synchronize = get_boolean_input(
            bot, "Do you want to synchronize commands? (y/n) "
        )

        if synchronize == True:
            # Try to update commands on Discord servers.
            bot.log.debug("Updating commands on Discord servers...")
            sync_list = await bot.tree.sync()
            bot.log.info(f"{len(sync_list)} commands synchronized.")
            config["update_bot"] = True
        else:
            bot.log.info("Commands not synchronized.")

    except Exception as e:
        bot.log.debug(f"Error in sync_commands: {traceback.format_exc()}")
        bot.log.error(f"Error in sync_commands: {e}")
        bot.log.error("Commands not synchronized.")


async def set_owner(bot: "Bot") -> None:
    """
    Sets the owner of the bot.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> await set_owner(bot)
    """
    try:
        config_file = bot.config_file

        with open(config_file, "r") as f:
            config = json.load(f)

        bot.log.info(
            f"Current owner: {config.get('owner_name')} - {config.get('owner_id')}"
        )
        change_owner_name = get_boolean_input(
            bot, "Do you want to change bot owner? (y/n) "
        )

        if change_owner_name == True:
            new_owner_name = input("Enter new owner name: ")
            new_owner_id = input("Enter new owner id: ")

            try:
                new_data = {
                    "update_bot": True,
                    "owner_name": new_owner_name,
                    "owner_id": new_owner_id,
                }
                update_config(config_file, new_data)

            except Exception as e:
                bot.log.debug(f"Failed to update the configuration file: {e}")
                return bot.log.warning("Failed to set update flag.")

            bot.log.info(
                "Config change, owner_name: {} -> {}".format(
                    config.get("owner_name"), new_owner_name
                )
            )
            bot.log.info(
                "Config change, owner_id: {} -> {}".format(
                    config.get("owner_id"), new_owner_id
                )
            )
        else:
            bot.log.info("Owner not changed.")

    except Exception as e:
        bot.log.debug(f"Error in set_owner function: {e}")
        bot.log.error(f"Error in set_owner function: {e}")


def show_help(bot: "Bot") -> None:
    """
    Displays a list of available commands.
    Args:
      bot (Bot): The bot instance.
    Returns:
      None
    Examples:
      >>> show_help(bot)
    """
    black = "\u001b[30m"
    cyan = "\u001b[36m"
    green = "\u001b[32m"
    purple = "\u001b[35m"
    bold = "\u001b[1m"
    reset = "\u001b[0m"
    commands = {
        "exit": "Shuts Bot and the script down.",
        "help": "Displays this message.",
        "ping": "Pongs.",
        "setbotname": "Changes the current Bot name.",
        "setpresence": "Changes the current Bot presence.",
        "setavatar": "Changes the current Bot avatar.",
        "setowner": "Sets the owner of the bot.",
        "reload": "Synchronizes commands with Discord.",
        "wipebot": 'Wipes the bot"s configuration files.',
        "getcogs": "Downloads and loads cogs.",
        "removecog": "Removes cogs from the bot.",
        "listcogs": "Lists all cogs currently loaded.",
        "aliases": "Lists all command aliases.",
        "debug": "Toggles debug mode.",
        "addblacklist": "Adds a cog to the blacklist.",
        "removeblacklist": "Removes a cog from the blacklist.",
    }

    try:
        bot.log.debug("Starting show_help function...")
        bot.log.info(
            f"{black}{'-' * 24}[ {purple}{bold}Available commands{reset}{black} ]{'-' * 24}{reset}"
        )
        bot.log.info("")
        bot.log.info(
            f"{cyan}Simply type the command you want to execute and press enter.{reset}"
        )
        bot.log.info(
            f"{cyan}A brief description of the command will be displayed below.{reset}"
        )
        bot.log.info("")

        for command, description in commands.items():
            bot.log.info(
                f"{green}{command}{' ' * (30 - len(command))}{black}- {description}{' ' * (45 - len(description))}{reset}"
            )
        bot.log.info("")
        bot.log.info(
            f"{black}{'-' * 22}[ {purple}{bold}End available commands{reset}{black} ]{'-' * 22}{reset}"
        )
        bot.log.debug("Exiting show_help function...")

    except Exception as e:
        bot.log.error(f"Error in show_help function: {e}")
        traceback.print_exc()


def show_aliases(bot: "Bot") -> None:
    """
    Prints a list of command aliases.
    Args:
      bot (Bot): The bot instance.
    Side Effects:
      Prints a list of command aliases to the console.
    Examples:
      >>> show_aliases(bot)
    """
    black = "\u001b[30m"
    purple = "\u001b[35m"
    green = "\u001b[32m"
    bold = "\u001b[1m"
    reset = "\u001b[0m"
    aliases = {
        "exit": ["quit", "shutdown"],
        "help": ["h", "?"],
        "ping": ["p"],
        "setbotname": ["setbot", "sbn"],
        "setpresence": ["setbotpres", "sbp"],
        "setavatar": ["setava", "sba"],
        "setowner": ["setown"],
        "reload": ["sync", "r"],
        "wipebot": ["wipeconfig", "wipe", "wb"],
        "getcogs": ["getcogs", "gc"],
        "removecog": ["removecogs", "rc"],
        "listcogs": ["list", "lc"],
        "alias": ["aliases", "a"],
        "debug": ["d"],
        "addblacklist": ["addbl", "abl"],
        "removeblacklist": ["rmblist", "rmbl"],
    }

    try:
        bot.log.debug("Starting show_aliases function...")
        bot.log.info(
            f"{black}{'-' * 24}[ {purple}{bold}Command Aliases{reset}{black} ]{'-' * 24}{reset}"
        )
        bot.log.info("")

        for command, alias_list in aliases.items():
            aliases_str = ", ".join(alias_list)
            bot.log.info(
                f"{green}{command}{' ' * (30 - len(command))}{black}- {aliases_str}{' ' * (45 - len(aliases_str))}{reset}"
            )
        bot.log.info("")
        bot.log.info(
            f"{black}{'-' * 22}[ {purple}{bold}End command aliases{reset}{black} ]{'-' * 22}{reset}"
        )
        bot.log.debug("Exiting show_aliases function...")

    except Exception as e:
        bot.log.error(f"Error in show_aliases function: {e}")
        traceback.print_exc()


def ping(bot: "Bot") -> None:
    """
    Prints 'Pong!' to the console.
    Args:
      bot (Bot): The bot instance.
    Side Effects:
      Prints 'Pong!' to the console.
    Examples:
      >>> ping(bot)
      Pong!
    """
    try:
        bot.log.info("Pong!")
    except Exception as e:
        bot.log.error(f"Error in ping function: {e}")
