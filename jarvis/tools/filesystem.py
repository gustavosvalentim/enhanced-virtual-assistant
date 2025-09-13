import os

from pathlib import Path
from langchain.tools import tool


BASE_DIR = Path(os.getcwd())


@tool
def write_file(filepath: str, content: str) -> str:
    """Writes the content to a file. 
    
    Parameters:
        filepath (str): Path to the file
        content (str): Content to be written
    """

    with open(BASE_DIR / filepath, 'a+') as buf:
        buf.write(content)
    return f'Wrote to file at {BASE_DIR / filepath}'


@tool
def read_file(filepath: str) -> str:
    """Reads a file from filesystem.
    
    Parameters:
        filepath (str): Path of the file
    """

    with open(BASE_DIR / filepath, 'r') as buf:
        return buf.read()
