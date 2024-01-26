from pathlib import Path
from typing import List
import requests
import re

class GoogleBooksAPICall:
    '''Builds a Dynamic Link and sends it to Google Books'''
    __slots__ = 'file', 'name', 'author', 'isbn', 'url', 'output', 'accepted_file_types'

    def __init__(self, file: str):
        self.file: Path = Path(file)
        accepted_file_types: List[str] = ['.pdf', '.epub']
        assert Path.is_file(self.file), 'File path must be valid'
        assert Path(self.file).suffix in accepted_file_types, 'Error - Invalid file type'

    @staticmethod
    def call_api(url: str, output: str) -> None:
        '''Sends a GET request to the API'''
        print(f'Sending request to {url}...')

        r = requests.get(url)
        assert r.status_code == 200, f'Error - Status Code {r.status_code}'

        s = r.json()

        with open(output, 'wb') as handler:
            for chunk in r.iter_content(chunk_size=128):
                handler.write(chunk)

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
        name = self.format_title(self.file)
        name = self.parse_file_name(name).replace(' ', '+')
        if ',' in name: name = name.split(',')[0]

        self.url = 'https://www.googleapis.com/' \
                        f'books/v1/volumes?q={name}'

        if author:
            author = author.replace(' ', '+').lower()
            self.url += f'+inauthor:{author}'
        if isbn: self.url += f'+isbn:{isbn}'

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

    def call_itunes_api(self) -> str:
        '''Sends a GET request to iTunes Search API'''
        r = requests.get(self.url_apple)
        print(f'Sending requests to {self.url_apple}...')
        s = r.json()

        try:
            list_s: List[str] = s['results'][0]['artworkUrl100'].split('/')
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
