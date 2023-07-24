from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Optional

import discord
from discord.ext import commands

from discord_bot.ai import ChatAgent, SearchAgent
from utils.logger import log_debug, welcome_to_bot
from utils.parser import split_chat
from utils.tools import update_with_discord

if TYPE_CHECKING:
    from discord_bot.bot import Bot

class CoreCog(commands.Cog, name='Bot Core', description='Core Discord event functionality + ChatGPT integration.'):
    """
    Be sure to set above to your .env file. Don't share these keys.
    You can edit agents and personas or manage memories in the 'data/ai' directory.

    The bot will have individual memory with each users conversation.
    All memories are cleared after token limit is reached, or after 3 minutes of inactivity.

    Simply type in the apropriate channel to talk to the bot.
    There is a built in rate limiter.

    WARNING: BEWARE OF ANY POSSIBLE OUTPUTS, AND MONITOR API USAGE. WE ARE NOT RESPONSIBLE FOR YOUR ACTIONS. BE SAFE.
    """
    def __init__(self, bot: 'Bot'):
        self.bot = bot

        self.guild_id = self.bot.guild_id
        self.chatbot_threads_id = bot.chatbot_threads_id
        self.category_id = bot.chatbot_category_id
        self.chat_agents = {}
        self._cd = commands.CooldownMapping.from_cooldown(
            1, 3.0, commands.BucketType.member)


    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        """Called when a thread is created."""
        time.sleep(0.25)
        persona = self.bot.config.get("persona")
        if thread.parent.name == "ai-chatbot":  # type: ignore
            reply = (
                f"Hello {thread.owner.mention}, please stay in this thread. " # type: ignore
                f"\nDo not ping people in {thread.name} and do not make duplicates. "
                f"\nIf {persona} does not respond to your thread within 1 minute or has an error, try again. "
                f"\nPlease **do not spam** the bot. If it still does not work ping an `Admin`. "
                f"\n\n**{persona} Start of Conversation:**"
            )
            await thread.send(reply)


    @commands.Cog.listener()
    async def on_message(self, ctx: discord.Message):
        """Called when a message is received."""
        chatbot = self.bot.user
        prompt = str(ctx.content)
        user = str(ctx.author.display_name)

        channel = ctx.channel
        self.channel_id = channel.id
        mentioned = False

        if prompt.startswith(self.bot.config.get("prefix")):
            return

        if ctx.guild != self.guild_id:
            ratelimit = self.get_ratelimit(ctx)
            supported_channel = self.category_id
            self.channel_id = ctx.channel.category_id if isinstance(
                ctx.channel, discord.Thread) else ctx.channel.id

            if chatbot in ctx.mentions:
                mentioned = True

            if self.channel_id != supported_channel or mentioned:
                return
            
            if not (ctx.author.bot):
                waiting = True

                if ratelimit is None or ratelimit < 0:
                    log_debug(self.bot, "Sending message to Chat-GPT...")

                    async with channel.typing():
                        while waiting:

                            if self.channel_id not in self.chat_agents:
                                self.chat_agents[self.channel_id] = ChatAgent(self.bot, self.channel_id)

                            chat_agent = self.chat_agents[self.channel_id]
                            messages = chat_agent.predict(prompt)
                            
                            if not messages:
                                raise ValueError("No response received from the agent.")

                            log_debug(self.bot, "Received response from OpenAI.")
                            
                            response = messages
                            response_chunks = split_chat(response)
                            
                            if response_chunks is None:
                                waiting = False
                                log_debug(self.bot, "No response from Chat-GPT API.")
                                return

                            for chunk in response_chunks:
                                if channel is not None:
                                    await channel.send(chunk)
                                    await asyncio.sleep(0.33)
                            else:
                                waiting = False
                else:
                    rate_response = f"You are talking too fast, {user}"
                    waiting = False
                    log_debug(
                        self.bot, f"User {user} is talking too fast. Rate limit: {ratelimit}")
                    await channel.send(rate_response)
                    return


    @commands.hybrid_command()
    async def search(self, ctx: commands.Context, *, prompt: str):
        """Runs the chatbot with internet tooling."""
        waiting = True
        channel = ctx.channel
        self.channel_id = channel.id
        async with channel.typing():
            while waiting:

                if self.channel_id not in self.chat_agents:
                    self.chat_agents[self.channel_id] = SearchAgent(self.bot)

                chat_agent = self.chat_agents[self.channel_id]
                messages = chat_agent.predict(prompt)

                if not messages:
                    raise ValueError("No response received from the agent.")

                log_debug(self.bot, "Received response from OpenAI.")

                response = messages
                response_chunks = split_chat(response)

                if response_chunks is None:
                    waiting = False
                    log_debug(self.bot, "No response from Chat-GPT API.")
                    return

                for chunk in response_chunks:
                    if channel is not None:
                        await channel.send(chunk)
                        await asyncio.sleep(0.33)
                else:
                    waiting = False
        
    
    @commands.Cog.listener()
    async def on_connect(self):
        """Called when bot connects to Discord."""
        try:
            # Update Bot's status and activity, if applicable.
            await update_with_discord(self.bot)
            self.bot.log.debug('Bot connected to Discord.')
        except Exception as e:
            self.bot.log.error(f'Error updating Bot: {e}')


    @commands.Cog.listener()
    async def on_ready(self):
        """Called when Bot is ready and connected to Discord."""
        try:
            await welcome_to_bot(self.bot)
            self.bot.log.debug('Bot is ready and connected to Discord.')
        except Exception as e:
            self.bot.log.error(f'Error welcoming Bot: {e}')
            
            
    @commands.Cog.listener()
    async def block_dms(self, ctx: commands.Context) -> bool:
        return ctx.guild is not None
    

    def get_ratelimit(self, message: discord.Message) -> Optional[float]:
        """Returns the ratelimit left."""
        bucket = self._cd.get_bucket(message)
        if bucket is None:
            return
        return bucket.update_rate_limit()


async def setup(bot: 'Bot') -> None:
    """Loads the cog."""
    try:
        await bot.add_cog(CoreCog(bot))
        bot.log.debug('CoreCog loaded.')
    except Exception as e:
        bot.log.error(f'Error loading CoreCog: {e}')
