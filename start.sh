#!/bin/bash

# Check if .env file exists, if not, create a default .env file
if [ ! -f .env ]; then
  cat > .env << EOL
OPENAI_API_KEY=your_openai_key
SERPAPI_API_KEY=your_serapi_key
DISCORD_TOKEN=your_discord_bot_key
DISCORD_GUILD_ID=your_discord_guild_id
CHATBOT_CATEGORY_ID=your_chat_category_id
CHATBOT_THREADS_ID=your_chat_threads_id
OPENAI_MODEL="gpt-3.5-turbo-16k"
EOL
fi

# Create a virtual environment
python3 -m venv venv

# Install requirements
venv/bin/pip install -r requirements.txt

# Launch src/main.py
venv/bin/python main.py