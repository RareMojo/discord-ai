
from typing import TYPE_CHECKING

from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts.chat import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    MessagesPlaceholder,
                                    SystemMessagePromptTemplate)


if TYPE_CHECKING:
    from discord_bot.bot import Bot


class SearchAgent:
    def __init__(self, bot: 'Bot'):
        self.bot = bot
        client = bot.openai_api_key
        model = bot.openai_model

        self.chat = ChatOpenAI(client=client, model=str(model), temperature=0)
        self.llm = OpenAI(client=client, model=str(model), temperature=0)
        self.tools = load_tools(["serpapi", "llm-math"], llm=self.llm)
        self.agent = initialize_agent(self.tools, self.chat, agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

    def predict(self, prompt):
        return self.agent.run(prompt)
    

class ChatAgent:
    def __init__(self, bot: 'Bot', channel_id, temperature=0, return_messages=True):
        self.bot = bot
        client = self.bot.openai_api_key
        model = self.bot.openai_model
        self.channel_id = channel_id
        
        with open(bot.dbs.configs.path / "preprompt", "r") as f:
            preprompt = f.read()
        
        preprompt = preprompt.replace("{persona}", bot.config.get("persona"))

        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(f"{preprompt}"),
            MessagesPlaceholder(variable_name=channel_id),
            HumanMessagePromptTemplate.from_template("{input}")
        ])

        self.llm = ChatOpenAI(client=client, model=str(model), temperature=temperature)
        memory = ConversationBufferWindowMemory(k=3, memory_key=channel_id, return_messages=return_messages)
        self.conversation = ConversationChain(memory=memory, prompt=self.prompt, llm=self.llm, verbose=True)

    def predict(self, prompt):
        response = self.conversation.predict(input=prompt)
        return response
    