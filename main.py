import asyncio
from pathlib import Path

from discord_bot.build import BuildBot
from utils.tools import make_filepaths

#   __                                             __                               
#  /\ \     __                                    /\ \                        __    
#  \_\ \   /\_\     ____    ___     ___    _ __   \_\ \               __     /\_\   
#  /'_` \  \/\ \   /',__\  /'___\  / __`\ /\`'__\ /'_` \   _______  /'__`\   \/\ \  
# /\ \L\ \  \ \ \ /\__, `\/\ \__/ /\ \L\ \\ \ \/ /\ \L\ \ /\______\/\ \L\.\_  \ \ \ 
# \ \___,_\  \ \_\\/\____/\ \____\\ \____/ \ \_\ \ \___,_\\/______/\ \__/.\_\  \ \_\
#  \/__,_ /   \/_/ \/___/  \/____/ \/___/   \/_/  \/__,_ /          \/__/\/_/   \/_/
#                                                                                                                                                                                                                                                                                                                                
#
# discord-ai: A Discord bot written in Python with LangChain and ChatGPT integration.
# This bot's primary objective in life is to assist in fulfilling gpt-engineering's mission.
# Thanks and have fun yall! -RareMojo


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
