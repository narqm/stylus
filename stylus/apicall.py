from pathlib import Path
from typing import Union
import requests
import re


class FileNameParser:
    '''Parse eBook file name for API call builder'''

    def __init__(self, file: Path):
        assert Path.is_file(file), 'File path must be valid'
        self.file: str = file.stem.lower()

    def parse_file_name(self, name: str) -> None:
        '''Regular expression file name parser'''
        pattern = re.compile(r'^(.*?)\s(by|-|_)\s(.*?)$')
        self.file = pattern.search(name).group(1)

    def check_name_break(self, name: str) -> bool:
        '''Check file name for common delimiters'''
        name_break = ['by', '-']
        values = re.split(r'\s|_', name)
        for value in values:
            return value in name_break

    def return_query_body(self) -> str:
        '''Return the file name for API consumption'''
        if self.check_name_break(self.file):
            self.parse_file_name(self.file)
        return self.file


class GoogleBooksAPICall:
    '''Builds a Dynamic Link and sends it to Google Books'''
    __slots__ = 'file', 'name', 'author', 'isbn', 'url', 'output', 'accepted_file_types'

    def __init__(self, file: str):
        self.file: Path = Path(file)
        accepted_file_types: list[str] = ['.pdf', '.epub']
        assert Path.is_file(self.file), 'File path must be valid'
        assert Path(self.file).suffix in accepted_file_types, 'Error - Invalid file type'
        self.url = ''

    @staticmethod
    def dwnld_json(_r: dict, _output: str):
        '''Download JSON to local file.'''
        with open(_output, 'wb') as handler:
            for chunk in _r.iter_content(chunk_size=128):
                handler.write(chunk)

    @staticmethod
    def call_api(url: str, output: str = 'results.json'):
        '''Sends a GET request to the API.'''
        print(f'Sending request to {url}...')

        r: str = requests.get(url)
        assert r.status_code == 200, f'Error - Status Code {r.status_code}'

        # GoogleBooksAPICall.dwnld_json(r, output)

        return r.json()

    @staticmethod
    def parse_file_name(name: str) -> str:
        '''Regular expression file name parser'''
        pattern = re.compile(r'^(.*?)\s(by|-|_)\s(.*?)$')
        return pattern.search(name).group(1)

    @staticmethod
    def format_title(title: str) -> str:
        '''Format book title for API call'''
        return Path(title).stem.lower()

    def build_api_request(self, author: str = '', isbn: str = '') -> str:
        '''Builds a Google Books API call'''
        assert isinstance(isbn, str), f'Error - isbn is a {isbn.__class__.__name__}'
        filenameparser = FileNameParser(self.file)
        name = filenameparser.return_query_body().replace(' ', '+')
        name = name.split(',')[0] if ',' in name else name
        self.url = 'https://www.googleapis.com/' \
                   f'books/v1/volumes?q={name}'

        if author:
            author = author.replace(' ', '+').lower()
            self.url += f'+inauthor:{author}'
        self.url += f'+isbn:{isbn}' if isbn else ''
        return self.url


class GenericAPICalls:
    '''Generic API calls for hi-resolution bookcovers'''

    def __init__(self, isbn: str, thumbnail: str):

        self.google_thumbnail = thumbnail

        self.url_apple = f'https://itunes.apple.com/lookup?isbn={isbn}'
        self.url_google = f'https://books.google.com/books?vid=ISBN{isbn}&printsec=frontcover'

    def call_google_api(self) -> str:
        '''Sends a GET request for Google Books static link thumbnail url'''
        assert self.google_thumbnail is not None, 'Missing thumbnail link!'
        url = self.google_thumbnail.split('&', 1)[0] + '&printsec=frontcover&' \
            'img=0&zoom=0&edge=curl&source=gbs_api'
        return url

    def call_itunes_api(self) -> Union[str, None]:
        '''Sends a GET request to iTunes Search API'''
        r = requests.get(self.url_apple)
        print(f'Sending requests to {self.url_apple}...')
        s = r.json()

        try:
            list_s: list[str] = s['results'][0]['artworkUrl100'].split('/')
        except IndexError as ie:
            print(f'{ie} - index out of range.')
            return
        high_res: str = '/100000x100000bb.jpg'
        return '/'.join(list_s[:-1]) + high_res

    @staticmethod
    def download_image(url: str, name: str):
        '''Download image from source'''
        print(f'Getting book cover from: {url}')
        r = requests.get(url)
        with open(name, 'wb') as file:
            file.write(r.content)
