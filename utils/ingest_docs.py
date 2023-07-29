import asyncio
import os
import tempfile
from typing import TYPE_CHECKING
from urllib.parse import urljoin

import aiohttp
import pinecone
from bs4 import BeautifulSoup
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone

from utils.logger import log_debug, log_error, log_info

if TYPE_CHECKING:
    from discord_bot.bot import Bot


async def download_file(bot: "Bot", session, url, output_directory):
    """
    Downloads a file from a given URL.
    Args:
      bot (Bot): The bot instance.
      session (aiohttp.ClientSession): The aiohttp session.
      url (str): The URL of the file to download.
      output_directory (str): The directory to save the file to.
    Side Effects:
      Writes the file to the output directory.
    Examples:
      >>> download_file(bot, session, 'https://example.com/file.txt', '/tmp/')
    """
    async with session.get(url) as response:
        if response.status == 200:
            file_name = os.path.join(output_directory, os.path.basename(url))
            file_content = await response.read()
            with open(file_name, "wb") as file:
                file.write(file_content)
            log_debug(bot, f"Downloaded: {url}")
        else:
            log_error(bot, f"Failed to download: {url}")


async def ingest_docs(bot: "Bot", url, namespace):
    """
    Ingests documents from a given URL into Pinecone.
    Args:
      bot (Bot): The bot instance.
      url (str): The URL of the documents to ingest.
      namespace (str): The namespace to ingest the documents into.
    Side Effects:
      Ingests documents into Pinecone.
    Examples:
      >>> ingest_docs(bot, 'https://example.com/docs', 'my_namespace')
    """
    base_url = url

    with tempfile.TemporaryDirectory() as temp_dir:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as response:
                if response.status == 200:
                    soup = BeautifulSoup(await response.text(), "html.parser")
                    tasks = []

                    for link in soup.find_all("a", {"class": "reference internal"}):
                        file_url = urljoin(base_url, link["href"])
                        if file_url.endswith(".html"):
                            tasks.append(
                                download_file(bot, session, file_url, temp_dir)
                            )

                    await asyncio.gather(*tasks)
                else:
                    log_error(bot, f"Failed to download: {base_url}")

        from langchain.document_loaders.readthedocs import ReadTheDocsLoader

        class MyReadTheDocsLoader(ReadTheDocsLoader):
            """My custom ReadTheDocsLoader."""

            def _clean_data(self, data: str) -> str:
                """
                Cleans the data from a given HTML string.
                Args:
                  data (str): The HTML string to clean.
                Returns:
                  str: The cleaned string.
                Examples:
                  >>> MyReadTheDocsLoader._clean_data('<html><body>Hello World!</body></html>')
                  'Hello World!'
                """
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(data, **self.bs_kwargs)

                html_tags = [
                    ("div", {"role": "main"}),
                    ("main", {"id": "main-content"}),
                    ("body", {}),
                ]

                text = None

                for tag, attrs in html_tags[::-1]:
                    text = soup.find(tag, attrs)
                    if text is not None:
                        break

                if text is not None:
                    text = text.get_text()
                else:
                    text = ""

                return "\n".join([t for t in text.split("\n") if t])

        loader = MyReadTheDocsLoader(temp_dir, features="html.parser", encoding="utf-8")
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000, chunk_overlap=100
        )
        texts = text_splitter.split_documents(docs)

        pinecone.init(api_key=bot.pinecone_api_key, environment=bot.pinecone_env)
        embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002", openai_api_key=bot.openai_api_key
        )
        Pinecone.from_documents(
            texts, embeddings, index_name=bot.pinecone_index, namespace=namespace
        )
        log_debug(
            bot,
            f"Successfully ingested {len(texts)} documents into Pinecone index {bot.pinecone_index} in namespace {namespace}.",
        )
