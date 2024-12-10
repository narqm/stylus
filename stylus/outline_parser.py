from pypdf import PdfReader, PdfWriter
from typing import Any, Union
from itertools import chain
import re


class RebuildOutline:
    '''Utility class; fixes encoding issues in PDF utlines caused by pypdf.'''

    def __init__(self, reader: PdfReader, writer: PdfWriter):

        self.reader = reader
        self.writer = writer

    @staticmethod
    def extract_text(text: list[str]) -> str:
        '''Basic text extraction and cleaning utility.'''
        assert isinstance(text, str), 'Error - text is not a string'
        text = text.replace('\\x00', '')
        matches = re.search(r'b[\'"](.*)[\'"]', text)
        return matches.group(1) if matches else text

    def create_parent(self, item: dict[str],
                      page_num: int,
                      _parent=None) -> dict[str]:
        '''Returns parent object for nested assignment.'''
        return self.writer.add_outline_item(item,
                                            page_num,
                                            parent=_parent)

    def get_page_number(self, item: dict[str]) -> int:
        '''Method grabs outline page number from reader object.'''
        return self.reader.get_destination_page_number(item)

    def recursive_outline_call(self, outlines: list[Union[list, str]],
                               parent: Union[None, Any]):
        '''Recursive function for nested outlines in rebuild_outline.'''
        for item in outlines:

            if not isinstance(item, list):
                title: str = self.extract_text(item['/Title'])
                _parent = self.create_parent(title, self.get_page_number(item),
                                             parent)

            else:
                self.recursive_outline_call(item, _parent)

    def rebuild_outline(self, outlines: list[Union[list, str]]):
        '''Rebuilds PDF outline after cleaning up any string-encoding issues.'''
        # this is horribly slow!
        assert isinstance(outlines, list), 'Error - outlines must be list'
        print('Rebuilding outline...')

        for item in outlines:

            if not isinstance(item, list):
                parent = self.create_parent(item['/Title'],  # extract_text()?
                                            self.get_page_number(item))

            else:
                self.recursive_outline_call(item, parent)
