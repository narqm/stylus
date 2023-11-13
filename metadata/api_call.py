from pathlib import Path
from requests_html import HTMLSession
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
            self.url += f'+inauthor:{author}'
        if isbn: self.url += f'+isbn:{isbn}'

        return self.url

class GenericAPICalls:
    '''Generic API calls for hi-resolution bookcovers'''

    def __init__(self, isbn, thumbnail):

        self.google_thumbnail = thumbnail
        
        self.url_apple = f'https://itunes.apple.com/lookup?isbn={isbn}'
        self.url_google = f'https://books.google.com/books?vid=ISBN{isbn}' \
                                '&printsec=frontcover'

    def call_google_preview(self):
        '''Sends a GET request to Google Books static link preview'''
        session = HTMLSession()
        print(f'Sending requests to {self.url_google}...')
        r = session.get(self.url_google)
        r.html.render(sleep=1)
        
        xpath = '//*[@id="viewport"]/div[1]/div/div/div[1]/div[2]/div/div[3]/img'
        cover_page = r.html.xpath(xpath, first=True)
        return cover_page.attrs['src']
    
    def call_google_api(self):
        '''Sends a GET request for Google Books static link thumbnail url'''
        assert self.google_thumbnail is not None, 'Missing thumbnail link!'
        url = self.google_thumbnail.split('&', 1)[0] + '&printsec=frontcover&' \
            'img=0&zoom=0&edge=curl&source=gbs_api'
        return url
    
    def call_itunes_api(self):
        '''Sends a GET request to iTunes Search API'''
        print(f'Sending requests to {self.url_apple}...')
        r = requests.get(self.url_apple)
        s = r.json()

        list_s = s['results'][0]['artworkUrl100'].split('/')
        high_res = '/100000x100000bb.jpg'
        return '/'.join(list_s[:-1]) + high_res
    
    @staticmethod
    def download_image(url):
        '''Download image from source'''
        print(f'Getting book cover from: {url}')
        r = requests.get(url)
        with open('cover_page.jpg', 'wb') as file:
            file.write(r.content)
