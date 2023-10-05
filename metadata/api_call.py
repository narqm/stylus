from pathlib import Path
import requests

class GoogleBooksAPICall:
    '''Builds a Dynamic Link and sends it to Google Books'''
    __slots__ = 'file', 'name', 'author', 'isbn', 'url', 'output'

    def __init__(self, file):
        self.file = Path(file)
        assert Path.is_file(self.file), 'File path must be valid'
        assert Path(self.file).suffix == '.pdf', 'Error - Invalid file type'

    @staticmethod
    def call_api(url, output):
        '''Sends a GET request to the API'''
        print(f'Sending request to {url}...')

        r = requests.get(url)
        assert r.status_code == 200, f'Error - Status Code {r.status_code}'

        s = r.json()

        with open(output, 'wb') as handler:
            for chunk in r.iter_content(chunk_size=128):
                handler.write(chunk)

    def build_api_request(self, author='', isbn=''):
        '''Builds a Google Books API call'''
        assert isinstance(isbn, str), f'Error - isbn is a {isbn.__class__.__name__}'
        name = Path(self.file).stem.lower().replace(' ', '+')
        if ',' in name: name = name.split(',')[0]
    
        self.url = 'https://www.googleapis.com/' \
                        f'books/v1/volumes?q={name}'
        
        if author: 
            author = author.replace(' ', '+').lower()
            self.url =+ f'+inauthor:{author}'
        if isbn: self.url += f'+isbn:{isbn}'

        return self.url