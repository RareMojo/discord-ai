<br/>
<p align="center">

  <img align="center" width="150" height="150" src="https://cdn.discordapp.com/icons/1119885301872070706/cfc3f8e3fc867c9a174ab9a7a11397e9.webp?size%253D100">

  <h3 align="center">GPT Engineer Discord Bot</h3>

  <p align="center">
    Our communities personal assistant!
    <br/>
    <br/>
    <a href="https://github.com/AntonOsika/gpt-engineer"><strong>Check out GPT-Engineer! »</strong></a>
    <br/>
  </p>
</p>
 
<br>

## Prerequisites

Before you begin, ensure you have met the following requirements:

- [Python 3.9+](https://www.python.org/downloads/)
- [Windows/Linux/MacOS](https://lmgtfy.app/?q=what+operating+system+do+i+have)
- [Discord App](https://discordpy.readthedocs.io/en/stable/discord.html)

### OpenAI API Key

1. **Sign up at OpenAI**: Visit the [OpenAI website](https://www.openai.com/) and sign up for an account.
2. **Go to API keys**: Click your profile icon and select "View API keys" from the dropdown menu.
3. **Create an API key**: Click the "Create new secret key" button to generate a new key.

### Pinecone DB

1. **Sign up for Pinecone**: Visit the [Pinecone website](https://www.pinecone.io/) and sign up for an account.
2. **Get your Pinecone API key**: After signing up, navigate to your dashboard and obtain your Pinecone API key.
[Video Tutorial](https://youtu.be/dnEfQhjZgw0?t=328)

### MongoDB

1. **Sign up for Railway**: Visit the [Railway.app website](https://railway.app/) and sign up for an account.
2. **Create a new project**: Follow the [official Railway documentation](https://docs.railway.app/getting-started#create-a-project) to create a new project.
3. **Add MongoDB plugin**: In your Railway project, add the MongoDB plugin by following the [official Railway documentation](https://docs.railway.app/getting-started).
[Video Tutorial](https://www.youtube.com/watch?v=tp0bQNDtLPc&t=88s)

<br>

## Installation

To install the GPT Engineer Discord Bot, follow these steps:

<br>

1. Clone the repository:

```bash
git clone https://github.com/RareMojo/gpt-engineer-discordbot.git
```

<br>

2. Navigate to the project directory:

```bash
cd gpt-engineer-discordbot
```

<br>

3. Run the start script:

<br>

For Windows:

```bash
start.bat
```

For Linux/Mac:

```bash
sh start.sh
```

<br>

## Configuration

Open `example_.env` file in the root directory of the project, and add your keys:

```env
OPENAI_API_KEY=your-key-here
DISCORD_TOKEN=your-token-here
DISCORD_GUILD_ID=your-server-id-here
CHATBOT_CATEGORY_ID=your-aichat-category-id-here
CHATBOT_THREADS_ID=your-aichat-threads-id-here
OPENAI_MODEL=gpt-3.5-turbo-16k
MONGO_URI=your-mongo-uri-here
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_INDEX=your-pinecone-index-here
PINECONE_ENV=your-pinecone-env-here
```

Rename the file to `.env` and save it.

<br>

## Usage

After installation and configuration, the bot will run automatically. It uses the GPT model to interact with users in the specified Discord channel.

<br>

## Contributing to GPT Engineer Discord Bot

To contribute to GPT Engineer Discord Bot, follow these steps:

1. Fork this repository.
2. Create a branch: \`git checkout -b <branch_name>\`.
3. Make your changes and commit them: \`git commit -m '<commit_message>'\`
4. Push to the original branch: \`git push origin <project_name>/<location>\`
5. Create the pull request.

Alternatively, see the GitHub documentation on [creating a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

<br>

## Credits & Thanks

I'm grateful to the creators of these open source projects:
- [Langchain-Chatbot](https://github.com/Haste171/langchain-chatbot) by Haste171
- [Write-the](https://github.com/Wytamma/write-the) by Wytamma

<br>

Their contributions have enhanced and reduced workload for our chat bot's functionality and streamlined documentation. <br>
Thank you, Haste171 and Wytamma, for inspiring developers and allowing others to incorporate and use your work.

<br>

## Contact

If you want to contact me, you can reach me on Discord `@RareMojo`.