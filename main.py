import asyncio
from pathlib import Path

from discord_bot.build import BuildBot
from utils.tools import make_filepaths

#              __
#             /\ \__                                 __
#   __   _____\ \ ,_\             __    ___      __ /\_\    ___      __     __   _ __
# /'_ `\/\ '__`\ \ \/  _______  /'__`\/' _ `\  /'_ `\/\ \ /' _ `\  /'__`\ /'__`\/\`'__\
# /\ \L\ \ \ \L\ \ \ \_/\______\/\  __//\ \/\ \/\ \L\ \ \ \/\ \/\ \/\  __//\  __/\ \ \/
# \ \____ \ \ ,__/\ \__\/______/\ \____\ \_\ \_\ \____ \ \_\ \_\ \_\ \____\ \____\\ \_\
# \/___L\ \ \ \/  \/__/         \/____/\/_/\/_/\/___L\ \/_/\/_/\/_/\/____/\/____/ \/_/
#   /\____/\ \_\                                 /\____/
#   \_/__/  \/_/                                 \_/__/
#
#
#
# gpt-engineer-discordbot: A basic Discord bot written in Python with LangChain and ChatGPT integration.
# This bot is to serve all users and developers at the gpt-engineer project discord.
# Thanks and have fun yall!


def launch_bot():
    """
    Ensures that the bot's files are set up, then builds and starts the bot.

    Launch this file to start the bot. Run: `python main.py` in the command line.
    """
    src_dir = Path(__file__).parent.absolute()
    configs_dir = Path(src_dir / "configs")
    data_dir = Path(src_dir / "data")
    assets = Path(src_dir / "assets")
    bot_dir = Path(src_dir / "discord_bot")
    logs_dir = Path(data_dir / "logs")
    cogs_dir = Path(src_dir / "cogs")

    paths = {
        "root": src_dir,
        "configs": configs_dir,
        "src": src_dir,
        "data": data_dir,
        "assets": assets,
        "bot": bot_dir,
        "logs": logs_dir,
        "cogs": cogs_dir,
    }

    make_filepaths(paths)

    builder = BuildBot(paths)
    bot = builder.build_bot()

    if bot:
        asyncio.run(bot.start_bot())
    else:
        print("Bot failed to build or start.")
        input("Press ENTER to EXIT.")


if __name__ == "__main__":
    launch_bot()
