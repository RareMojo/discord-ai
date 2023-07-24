import asyncio
from pathlib import Path

from discord_bot.build import BuildBot
from utils.db import DB, DBs

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
# gpt-engineer-discord-bot: A basic Discord bot written in Python.
# This bot is to serve all users and developers at the gpt-engineer project discord.
# Thanks and have fun yall!


def launch_bot():
    """
    Ensures that the bot's files are set up, then builds and starts the bot.

    Launch this file to start the bot. Run: `python main.py` in the command line.
    """
    root_dir = Path(__file__).parent.parent.absolute()
    configs_dir = Path(root_dir / "configs")
    src_dir = Path(__file__).parent.absolute()
    data_dir = Path(src_dir / "data")
    assets = Path(root_dir / "assets")
    bot_dir = Path(src_dir / "discord_bot")
    logs_dir = Path(data_dir / "logs")
    cogs_dir = Path(src_dir / "cogs")

    dbs = DBs(
        bot=DB(bot_dir),
        logs=DB(logs_dir),
        configs=DB(configs_dir),
        assets=DB(assets),
        cogs=DB(cogs_dir),
        data=DB(data_dir),
    )

    builder = BuildBot(dbs)
    bot = builder.build_bot()

    if bot:
        asyncio.run(bot.start_bot())
    else:
        print("Bot failed to build or start.")
        input("Press ENTER to EXIT.")


if __name__ == "__main__":
    launch_bot()
