from typing import Any, List, Union
from pathlib import Path
import json
import re

class RebuildOutline:
    '''Utility class the fixes encoding issues in PDF outlines'''
    def __init__(self, reader: bytes, writer: bytes):

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

    def check_if_json_exists(self, input: str) -> bool:
        '''Checks if given JSON exists'''
        return Path(input).exists()

    def check_urls(self, _json: Path, url: str) -> bool:
        '''Checks if api_call URL matches record'''
        if not self.check_if_json_exists(_json):
            return False

        with open(_json, 'r') as f:
            data = json.load(f)

        return data['key'] == url

    @staticmethod
    def add_url_to_json(url: str, _json: str) -> None:
        '''Append search URL to given JSON'''
        data = {'key': url}
        with open(_json, 'w') as f:
            json.dump(data, f)
