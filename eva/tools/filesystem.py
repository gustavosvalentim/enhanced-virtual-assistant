import logging
import os

from langchain.tools import tool


logger = logging.getLogger(__file__)


@tool
def write_file(filepath: str, content: str) -> str:
    """Writes the content to a file. 
    
    Parameters:
        filepath (str): Path to the file
        content (str): Content to be written
    """

    logger.debug(f'Writing to file {filepath}')

    with open(filepath, 'a+') as buf:
        buf.write(content)

    return f'File {filepath} was written successfully'


@tool
def read_file(filepath: str) -> str:
    """Reads a file from filesystem.
    
    Parameters:
        filepath (str): Path of the file
    """

    logger.debug(f'Reading from file {filepath}')

    if not os.path.exists(filepath):
        return f'File {filepath} does not exist'

    with open(filepath, 'r') as buf:
        return buf.read()
