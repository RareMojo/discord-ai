@echo off

REM Check if .env file exists, if not, create a default .env file
if not exist .env (
  (
  echo OPENAI_API_KEY=your_openai_key
  echo SERPAPI_API_KEY=your_serapi_key
  echo DISCORD_TOKEN=your_discord_bot_key
  echo DISCORD_GUILD_ID=your_discord_guild_id
  echo CHATBOT_CATEGORY_ID=your_chat_category_id
  echo CHATBOT_THREADS_ID=your_chat_threads_id
  echo OPENAI_MODEL="gpt-3.5-turbo-16k"
  ) > .env
)

REM Create a virtual environment
python -m venv venv

REM Activate the virtual environment
call venv\Scripts\activate

REM Update pip
python -m pip install --upgrade pip

REM Install requirements
pip install -r requirements.txt

REM Launch src/main.py
python src\main.py

REM Deactivate the virtual environment
call venv\Scripts\deactivate.bat