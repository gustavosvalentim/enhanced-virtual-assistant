import logging
from langchain_core.tools import tool
from wikipediaapi import Wikipedia


logger = logging.getLogger(__name__)
wiki = Wikipedia(user_agent='Jarvis Agent', language='en')


@tool
def find_wikipedia_pages_by_subject(subject: str):
    """Searches pages in Wikipedia by subject. """

    logger.debug('Find pages for subject: %s', subject)

    pages = wiki.page(subject).links.values()
    pages_num = len(pages)
    output = []
    max_links = min(pages_num, 10)
    for page in list(pages)[:max_links]:
        logger.debug('Found page %s for subject %s', page.title, subject)
        output.append(f'Title: {page.title}\r\n'
                      f'Summary: {page.summary}\r\n'
                      '---\r\n')

    logger.debug('Found %d pages for subject: %s', len(pages), subject)

    return '\r\n'.join(output)


@tool
def get_wikipedia_page_by_title(page_title: str) -> str:
    """Get the content from a wikipedia page. """

    logger.debug('Getting page content for page title: %s', page_title)

    page = wiki.page(page_title)

    if not page.exists():
        logger.debug('Page with title %s does not exist', page_title)
        return 'Page does not exist'
    
    logger.debug('Found page with title %s', page_title)

    return (f'Page title: {page.title}'
            f'URL: {page.fullurl}'
            f'Text: {page.text}')


if __name__ == '__main__':
    pages = find_wikipedia_pages_by_subject.invoke('python')
    content = get_wikipedia_page_by_title.invoke('Python (Programming language)')

    # print(pages)
    # print(content)
