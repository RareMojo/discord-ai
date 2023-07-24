import ast
import os
import re

import astor

from discord_bot.bot import Bot
from utils.logger import log_debug, log_error


def clean_response(bot: Bot, user: str, response: str):
    """Cleans a response from the OpenAI API."""
    labels = ["System: ", "User: ", "Assistant: ",
              "[System]: ", "[User]: ", "[Assistant]: ",
              f"{bot.config.get('persona')}: ", f"[{bot.config.get('actor')}]: ",
              f"{user}: ", f"[{user}]: "]
    
    for label in labels:
        response = response.replace(label, "")

    return response

def split_chat(chat, max_chars=2000):
    """Splits a given chat into chunks of a specified maximum character length."""
    lines = chat.split('\n')
    chunks = []
    chunk = ""
    inside_code_block = False
    language = ""

    code_block_start_pattern = re.compile(r'^```[\s]*\w*')
    code_block_end_pattern = re.compile(r'^```$')

    def add_chunk(chunk):
        if chunk:
            chunks.append(chunk)

    for line in lines:
        if code_block_start_pattern.match(line):
            if not inside_code_block and chunk:
                add_chunk(chunk)
                chunk = ""
            inside_code_block = True
            language = line.strip('`').strip()

            if len(chunk) + len(line) + 1 > max_chars:
                add_chunk(chunk)
                chunk = ""
            chunk += line + '\n'
            continue
        
        elif code_block_end_pattern.match(line):
            inside_code_block = False

            if len(chunk) + len(line) + 1 > max_chars:
                add_chunk(chunk)
                chunk = ""
            chunk += line + '\n'
            add_chunk(chunk)
            chunk = ""
            continue

        if inside_code_block:
            if len(chunk) + len(line) + 1 > max_chars:
                # Add the end delimiter for the current code block
                chunk += '```\n'
                add_chunk(chunk)
                chunk = ""

                # Start a new chunk with the correct language identifier
                chunk += f'```{language}\n'
            chunk += line + '\n'
        else:
            if len(chunk) + len(line) + 1 > max_chars:
                add_chunk(chunk)
                chunk = ""
            chunk += line + '\n'

    add_chunk(chunk)
    
    return chunks


def parse_python_files(directory):
    """Parses all Python files in a given directory and its subdirectories."""
    file_contents = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                name, content = parse_python_file(file_path)
                file_contents[name] = content
                
    return file_contents


def parse_python_file(file_path):
    """Parses a Python file and extracts its classes, functions, variables, and imports."""
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
            "imports": imports
        }


def find_classes(tree):
    """Parses all classes in a Python file and returns a dictionary."""
    classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes[node.name] = astor.to_source(node)
            
    return classes


def find_functions(tree):
    """Parses all functions in a Python file and returns a dictionary."""
    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions[node.name] = astor.to_source(node)
            
    return functions


def find_variables(tree):
    """Parses all variables in a Python file and returns a dictionary."""
    variables = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variables[target.id] = astor.to_source(node)
                    
    return variables


def find_imports(tree):
    """Parses all imports in a Python file and returns a dictionary."""
    imports = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports[alias.name] = astor.to_source(node)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports[alias.name] = astor.to_source(node)
                
    return imports
