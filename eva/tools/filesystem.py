import logging
import os

from langchain.tools import tool


logger = logging.getLogger(__file__)


@tool
def write_file(filepath: str, content: str) -> str:
    """Write a file.

    Parameters:
        filepath (str): Path to the file
        content (str): Content to be written
    """

    logger.debug(f'Writing to file {filepath}')

    try:
        with open(filepath, 'a+', encoding='utf-8') as buf:
            buf.write(content)
    except Exception as e:
        logger.error('Could not write file at %s', filepath, e, exc_info=True)
        return f'Could not write file at {filepath}'

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

    try:
        with open(filepath, 'r') as buf:
            return buf.read()
    except Exception as e:
        logger.error('There was an error reading the file %s', filepath, e, exc_info=True)
        return 'There was an problem reading the file'
