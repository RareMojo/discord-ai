<p align="center">
  <a href="https://discord.gg/8tcDQ89Ej2">
    <img src="https://dcbadge.vercel.app/api/server/8tcDQ89Ej2?style=flat" alt="Discord Follow">
  </a>

  <a href="https://github.com/RareMojo/discord-ai">
    <img src="https://img.shields.io/github/stars/RareMojo/discord-ai?style=social" alt="GitHub Repo stars">
  </a>

  <a href="https://www.oracle.com/chatbots/what-is-a-chatbot/">
    <img src="https://img.shields.io/badge/Discord-Chatbot-5865F2" alt="Discord Chatbot">
  </a>

  <a href="https://github.com/langchain-ai">
    <img src="https://img.shields.io/badge/LangChain-Integrated-37ff77" alt="LangChain Integration">
  </a>

  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow" alt="LICENSE">
  </a>
</p>

<br/>
<p align="center">
  <h2 align="center">discord-ai</h2><br>

  <p align="center">
    <img align="center" width="275" height="275" src="https://i.imgur.com/7VclQXi.png">
    <br/>
    <br/>
    Your communities personal assistant.<br><br>
    <a href="https://github.com/AntonOsika/gpt-engineer"><strong>Check out GPT-Engineer! »</strong></a>
    <br/>
  </p>
</p>

<br>

## About discord-ai

discord-ai is a super smart and versatile AI assistant for Discord communities!

Its primary objective is to serve the specific needs of the discord-ai Discord community. This version you see here is the open-source adaptation, allowing anyone to benefit from its awesome features!

Whether you need information, want to chat, interact with documents, code, explore websites, or enjoy some cool Discord-only features, discord-ai has got your back. It's designed to be user-friendly, customizable, and open source – just the way you like it!

We're all about community here! Join us in making discord-ai even better. Your ideas and contributions are always welcome.

Let's level up your Discord experience with discord-ai, the friendly AI chatbot for everyone! 🤖💬

<br>

## Prerequisites

Before you begin, ensure you have met the following requirements:

- [Python 3.10+](https://www.python.org/downloads/)
- **Windows/Linux/MacOS**
- [Discord App](https://discordpy.readthedocs.io/en/stable/discord.html)

<br>

### OpenAI API Key

1. **Sign up at OpenAI**: Visit the [OpenAI website](https://www.openai.com/) and sign up for an account.
2. **Obtain your API key**: Click your profile icon and select "**View API keys**" from the dropdown menu. Then, click the "**Create new secret key**" button to generate a new API key.

<br>

### Pinecone DB

1. **Sign up for Pinecone**: Visit the [Pinecone website](https://www.pinecone.io/) and sign up for an account.
2. **Get your Pinecone API key**: After signing up, navigate to your dashboard and obtain your **Pinecone API key, index, and environment**. Watch this [Video Tutorial](https://youtu.be/dnEfQhjZgw0?t=328) for assistance.

<br>

### MongoDB

1. **Sign up for Railway**: Visit the [Railway.app website](https://railway.app/) and sign up for an account.
2. **Create a new project**: Follow the [official Railway documentation](https://docs.railway.app/getting-started#create-a-project) to create a new project.
3. **Add MongoDB plugin**: In your Railway project, add the MongoDB plugin by following the [official Railway documentation](https://docs.railway.app/getting-started).
4. **Get your MongoDB URI**: After adding the MongoDB plugin, navigate to the plugin settings and obtain your **MongoDB URI**. Watch this [Video Tutorial](https://www.youtube.com/watch?v=tp0bQNDtLPc&t=88s) for assistance.

<br>

## Installation

To install discord-ai, follow these steps:

<br>

1. Clone the repository:

    `git clone https://github.com/RareMojo/discord-ai.git`

<br>

2. Navigate to the project directory:

    `cd discord-ai`

<br>

3. Run the start script:

    - For Windows:<br>
    `start.bat`

    - For Linux/Mac:<br>
    `sh start.sh`

<br>

## Configuration

1. `example_.env` | `.env`:

   - You will need to provide Discord Token and API keys for the bot to function properly.
   - You also need to provide the Discord server ID, category ID, and threads ID.
   - The category ID is the ID of the chat category all of your AI chat channels will be in.
   - The threads ID is the ID of the threads channel that will be used for generic agent interaction.

    <br>

      Open `example_.env` file in the root directory of the project, and add your keys:

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


      
      Rename the file to `.env` if you haven't already and save it.

<br>

2. `configs\config.json`:

- You will be prompted to fill out the required parts of this during setup automatically.
- You may directly edit this file to change anything as well.
- If you change something that should be updated with the Discord servers, change `update_bot` to true.
- You can also edit most of the config values via the bot terminal.

<br>

3. `configs\preprompts`:

<br>

- This is a small preprompt that is injected before chat interactions.
- It maintains small details such as the bot's name and personality.
- You may directly edit this to fit your needs.

<br>

4. `TMUX (Optional)`:

- This is used to run the bot like a service in a separate terminal.
- You can install it by running `sudo apt install tmux` on Linux.
- Feel free to use other methods of running the bot in the background.
- [TMUX Tutorial](https://www.hamvocke.com/blog/a-quick-and-easy-guide-to-tmux/)

<br>

## Usage

After installation and configuration, the bot will run automatically.
It uses the GPT model to interact with users in the specified Discord channel.
Currently, it can ingest ReadTheDocs URLs and provide help using it as context.

<br>

Here is a step-by-step guide on how to use the bot:

<br>

1. **Channel Setup**:
- The bot can be set up in any channel of your Discord server. This is an example of a proper setup. Copy the category ID and paste it in the `.env` file.
- You do not need to have the same names or exact setup. This is just recommended. Just make certain you use the correct channel IDs.

    ![Channel Setup](https://i.imgur.com/ex0aM7t.png)

<br>

2. **Thread Listing**:
- This is an example of the thread listing within the threads section that is to be used for generic agent interaction.
- Copy the thread channel ID and paste it in the `.env` file.

    ![Thread Listing](https://i.imgur.com/iImvMSV.png)

<br>

3. **Help DB**:
- The bot can provide help related to database commands.
- Use the `/helpdb` command to get a list of all database related commands.

    ![Help DB](https://i.imgur.com/zlTwiwT.png)

<br>

4. **Ingest DB**:
- The bot can ingest data into the database.
- Currently, the only supported data type is ReadTheDocs URLs.
- Example: https://gpt-engineer.readthedocs.io/en/latest/
- Use the `/ingestdb` command followed by the data you want to ingest and a name for the data.

    ![Ingest DB](https://i.imgur.com/UbnrjV4.png)

<br>

5. **List DB**:
- The bot can list all the data in the database.
- Use the `/listdb` command to get a list of all the data in the database.

    ![List DB](https://i.imgur.com/fgbQvrn.png)

<br>

6. **AI Chat**:
- The bot can interact with users in the specified Discord channel.
- Make a thread in the designated ai-chat thread, and the chatbot will automatically start interacting with you.

    ![AI Chat](https://i.imgur.com/tVVMnYP.png)

<br>

7. **Ask DB**:
- The bot can fetch information from the database.
- Use the `/askdb` command followed by your query and the db ID to get the required information.
- The ID is set to the `gpt-engineer-docs` database by default.

    ![Ask DB](https://i.imgur.com/Y1enGPn.png)

<br>

Remember to replace the command prefix `/` with the prefix you have set for your bot. Enjoy interacting with your GPT Engineer Discord Bot!

<br>

## Contributing to discord-ai

To contribute to discord-ai, follow these steps:

<br>

1. Fork this repository.
2. Create a branch: `git checkout -b <branch_name>`
3. Make your changes and commit them: `git commit -m <commit_message>`
4. Push to the original branch: `git push origin <project_name>/<location>`
5. Create the pull request.

Alternatively, see the GitHub documentation on [creating a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

<br>

## Credits & Thanks

I'm grateful to the creators of these open source projects:
- [Langchain-Chatbot](https://github.com/Haste171/langchain-chatbot) by Haste171

<br>

Their contributions have enhanced and reduced workload for our chat bot's functionality and streamlined documentation. <br>
Thank you, Haste171, for inspiring developers and allowing others to incorporate and use your work.

<br>

## License
`discord-ai` is completely open source, licensed under the [MIT](https://opensource.org/licenses/MIT) license.
See [LICENSE.md](https://github.com/RareMojo/discord-ai/blob/main/LICENSE.md) for more information.

Logo was made with the amazing and fun to use [Stable Diffusion](https://huggingface.co/stabilityai)