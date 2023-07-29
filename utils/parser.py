import ast
import os
import re

import astor

from discord_bot.bot import Bot
from utils.logger import log_debug, log_error


def clean_response(bot: Bot, user: str, response: str):
    """
    Removes labels from a response string.
    Args:
      bot (Bot): The Bot instance.
      user (str): The user's name.
      response (str): The response string.
    Returns:
      str: The response string with labels removed.
    Examples:
      >>> clean_response(bot, "User", "User: Hello")
      "Hello"
    """
    labels = [
        "System: ",
        "User: ",
        "Assistant: ",
        "[System]: ",
        "[User]: ",
        "[Assistant]: ",
        f"{bot.config.get('persona')}: ",
        f"[{bot.config.get('actor')}]: ",
        f"{user}: ",
        f"[{user}]: ",
    ]

    for label in labels:
        response = response.replace(label, "")

    return response


def split_chat(chat, max_chars=2000):
    """
    Splits a chat into chunks of a maximum length.
    Args:
      chat (str): The chat string.
      max_chars (int, optional): The maximum length of each chunk. Defaults to 2000.
    Returns:
      list: A list of chunks.
    Examples:
      >>> split_chat("Hello world!", 5)
      ["Hello", " worl", "d!"]
    """
    lines = chat.split("\n")
    chunks = []
    chunk = ""
    inside_code_block = False
    language = ""

    code_block_start_pattern = re.compile(r"^```[\s]*\w*")
    code_block_end_pattern = re.compile(r"^```$")

    def add_chunk(chunk):
        """
        Adds a chunk to a list of chunks.
        Args:
          chunk (str): The chunk to add.
          chunks (list): The list of chunks.
        Returns:
          None
        Side Effects:
          Adds the chunk to the list of chunks.
        Examples:
          >>> chunks = []
          >>> add_chunk("Hello", chunks)
          >>> chunks
          ["Hello"]
        """
        if chunk:
            chunks.append(chunk)

    for line in lines:
        if code_block_start_pattern.match(line):
            if not inside_code_block and chunk:
                add_chunk(chunk)
                chunk = ""
            inside_code_block = True
            language = line.strip("`").strip()

            if len(chunk) + len(line) + 1 > max_chars:
                add_chunk(chunk)
                chunk = ""
            chunk += line + "\n"
            continue

        elif code_block_end_pattern.match(line):
            inside_code_block = False

            if len(chunk) + len(line) + 1 > max_chars:
                add_chunk(chunk)
                chunk = ""
            chunk += line + "\n"
            add_chunk(chunk)
            chunk = ""
            continue

        if inside_code_block:
            if len(chunk) + len(line) + 1 > max_chars:
                # Add the end delimiter for the current code block
                chunk += "```\n"
                add_chunk(chunk)
                chunk = ""

                # Start a new chunk with the correct language identifier
                chunk += f"```{language}\n"
            chunk += line + "\n"
        else:
            if len(chunk) + len(line) + 1 > max_chars:
                add_chunk(chunk)
                chunk = ""
            chunk += line + "\n"

    add_chunk(chunk)

    return chunks


def parse_python_files(directory):
    """
    Parses all Python files in a directory.
    Args:
      directory (str): The directory to parse.
    Returns:
      dict: A dictionary of file names and contents.
    Examples:
      >>> parse_python_files("/path/to/directory")
      {
        "file1.py": {
          "classes": {...},
          "functions": {...},
          "variables": {...},
          "imports": {...},
        },
        "file2.py": {
          "classes": {...},
          "functions": {...},
          "variables": {...},
          "imports": {...},
        },
        ...
      }
    """
    file_contents = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                name, content = parse_python_file(file_path)
                file_contents[name] = content

    return file_contents


def parse_python_file(file_path):
    """
    Parses a Python file.
    Args:
      file_path (str): The path to the file.
    Returns:
      tuple: A tuple of the file name and a dictionary of its contents.
    Examples:
      >>> parse_python_file("/path/to/file.py")
      ("file.py", {
        "classes": {...},
        "functions": {...},
        "variables": {...},
        "imports": {...},
      })
    """
    with open(file_path, "r") as file:
        name = os.path.basename(file_path)
        content = file.read()
        tree = ast.parse(content)
        classes = find_classes(tree)
        functions = find_functions(tree)
        variables = find_variables(tree)
        imports = find_imports(tree)
        return name, {
            "classes": classes,
            "functions": functions,
            "variables": variables,
            "imports": imports,
        }


def find_classes(tree):
    """
    Finds all classes in a Python AST.
    Args:
      tree (ast.AST): The Python AST.
    Returns:
      dict: A dictionary of class names and source code.
    Examples:
      >>> tree = ast.parse("class MyClass: pass")
      >>> find_classes(tree)
      {"MyClass": "class MyClass: pass"}
    """
    classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes[node.name] = astor.to_source(node)

    return classes


def find_functions(tree):
    """
    Finds all functions in a Python AST.
    Args:
      tree (ast.AST): The Python AST.
    Returns:
      dict: A dictionary of function names and source code.
    Examples:
      >>> tree = ast.parse("def my_func(): pass")
      >>> find_functions(tree)
      {"my_func": "def my_func(): pass"}
    """
    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions[node.name] = astor.to_source(node)

    return functions


def find_variables(tree):
    """
    Finds all variables in a Python AST.
    Args:
      tree (ast.AST): The Python AST.
    Returns:
      dict: A dictionary of variable names and source code.
    Examples:
      >>> tree = ast.parse("my_var = 1")
      >>> find_variables(tree)
      {"my_var": "my_var = 1"}
    """
    variables = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variables[target.id] = astor.to_source(node)

    return variables


def find_imports(tree):
    """
    Finds all imports in a Python AST.
    Args:
      tree (ast.AST): The Python AST.
    Returns:
      dict: A dictionary of import names and source code.
    Examples:
      >>> tree = ast.parse("import my_module")
      >>> find_imports(tree)
      {"my_module": "import my_module"}
    """
    imports = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports[alias.name] = astor.to_source(node)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports[alias.name] = astor.to_source(node)

    return imports
