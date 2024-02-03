from typing import List
from pathlib import Path
import json


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
