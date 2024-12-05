from pypdf import PdfReader, PdfWriter
from typing import Any, List, Union
import re


class RebuildOutline:
    '''Utility class the fixes encoding issues in PDF outlines'''
    def __init__(self, reader: PdfReader, writer: PdfWriter):

        self.reader = reader
        self.writer = writer

    @staticmethod
    def extract_text(text: List[str]) -> str:
        '''Basic text extraction and cleaning utility'''
        assert isinstance(text, str), 'Error - text is not a string'
        text = text.replace('\\x00', '')
        matches = re.search(r'b[\'"](.*)[\'"]', text)
        return matches.group(1) if matches else text

    def recursive_outline_call(self,outlines: List[Union[List, str]], parent: Union[None, Any]) -> None:
        '''Recursive function for nested outlines in rebuild_outline'''
        for item in outlines:

            if not isinstance(item, list):
                title = self.extract_text(item['/Title'])
                page_number = self.reader.get_destination_page_number(item)
                self.writer.add_outline_item(title, page_number, parent)

            else:
                self.recursive_outline_call(item, parent)

    def rebuild_outline(self, outlines: List[Union[List, str]]) -> None:
        '''Rebuilds PDF outline after cleaning up any string-encoding issues'''
        assert isinstance(outlines, list), 'Error - outlines must be list'
        print('Rebuilding outline...')

        for item in outlines:

            if not isinstance(item, list):
                page_number = self.reader.get_destination_page_number(item)
                parent = self.writer.add_outline_item(item['/Title'], page_number)

            else:
                self.recursive_outline_call(item, parent)
