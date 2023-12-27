from typing import List, Union, Any
from pathlib import Path
import re

class RebuildOutline:
    '''Utility class the fixes encoding issues in PDF outlines'''
    def __init__(self, reader: bytes, writer: bytes):

        self.reader = reader
        self.writer = writer

    @staticmethod
    def extract_text(text: List[str]) -> str:
        '''Basic text extraction and cleaning utility'''
        pattern = r'b[\'"](.*)[\'"]'
        matches = re.search(pattern, text.replace('\\x00', ''))
        if matches: return matches.group(1)
        return text.replace('\\x00', '')

    def search_lists(self, outline: List[Union[List, str]], parent: List[str]) -> None:
        '''Recursively searches nested outline objects'''
        for sub_section in outline:
            if isinstance(sub_section, list):
                child_object = None
                self.search_lists(sub_section, child_object)
            else:
                title = self.extract_text(sub_section['/Title'])
                page_number = self.reader.get_destination_page_number(sub_section)
                child_object = self.writer.add_outline_item(
                    title, page_number, parent)

    def rebuild_outline(self, outlines: List[Union[List, str]]) -> None:
        '''Rebuilds PDF outline after cleaning up any string-encoding issues'''
        assert isinstance(outlines, list), 'Error - outlines is not a list'
        print('Rebuilding outline...')
        for outline in outlines:
            if isinstance(outline, list):
                parent = None
                self.search_lists(outline, parent)
            else:
                page_number = self.reader.get_destination_page_number(outline)
                parent = self.writer.add_outline_item(
                    outline['/Title'], page_number)

class Utilities:
    '''General utility class for path unpacking'''
    def __init__(self):
        ...

    @staticmethod
    def unpack_text_file(file: Path) -> List[Path]:
        '''Unpack text file lines to list'''
        assert Path(file).suffix == '.txt', 'Error - can only unpack .txt files'
        with open(file, 'r') as file:
            files = file.readlines()

        files = [file.replace('\"', '').replace('\n', '') for file in files]

        return files
