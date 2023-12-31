from typing import Dict, List, Union, Tuple
from pathlib import Path
import json
import sys

class FormatMetadata:
    '''Formats metadata for grammatical consistancy'''
    functors = ['a', 'an', 'the', 'in', 'on', 'at', 'by', 'and', 
                'but', 'or', 'you', 'your', 'my', 'his', 'her', 
                'their', 'this', 'that', 'these', 'those', 'what', 
                'which', 'who', 'there', 'can', 'will', 'should', 
                'would', 'must', 'may', 'might', 'could', 'not', 
                'no', 'to', 'of']

    edition = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 
               'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth', 'thirteenth', 
               'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth', 'eighteenth', 
               'nineteenth', 'twentieth', 'edition']

    def __init__(self):
        assert Path('results.json').is_file(), 'Missing results.json'
        with open('results.json', 'rb') as f:
            self.data = json.load(f)

        self.author, self.title = '', ''

        self.isbn_10, self.isbn_13 = '', ''

        self.thumbnail = ''

        self.volume_info: iter = (values['volumeInfo'] for values in self.data['items'])

    def std_title(self, title: str) -> str:
        '''Modifies variable str to check grammatical functors'''
        format_title = [title.split(' ')[0].capitalize()]
        for word in title.split(' ')[1:]:
            if word.lower() in self.functors:
                format_title.append(word.lower())
            elif word.lower() in self.edition:
                format_title.append(word.capitalize())
            elif title.isupper():
                format_title.append(word.capitalize())
            else: format_title.append(word)

        return ' '.join(format_title)

    def format_metadata(self) -> None:
        '''Formats desired metadata from JSON'''
        current = next(self.volume_info)

        title = self.std_title(current['title'])
        if current.get('subtitle'): 
            subtitle = self.std_title(current['subtitle'])
            title += ': {value}'.format(value=subtitle)

        if current.get('authors'):
            if len(current['authors']) == 3:
                author = ', '.join(current['authors'][:-1]) + ', and ' + current['authors'][-1]
            elif len(current['authors']) == 1: 
                author = current['authors'][0]
            elif len(current['authors']) >= 4: 
                author = current['authors'][0] + ' and Others'
            else: author = current['authors'][0] + ' and ' + current['authors'][-1]
        else:
            print('No author data on file...')
            author, title = DirectInput.user_metadata_prompt()

        try:
            self.get_thumbnail(current)
        except KeyError as ke:
            print(f'{ke} - preview link is missing')

        self.get_isbn(current)

        self.confirm_metadata(author, title)

    def get_isbn(self, current: Union[Dict, List]) -> None:
        '''Obtains the ISBN-13 value from JSON'''
        self.isbn_13 = current['industryIdentifiers'][0]['identifier']

    def get_thumbnail(self, current: Union[Dict, List]) -> None:
        '''Grabs current selection thumbnail image link from JSON'''
        if current['imageLinks'].get('thumbnail'):
            self.thumbnail = current['imageLinks']['thumbnail']
        else: self.thumbnail = None

    def confirm_metadata(self, author: str, title: str) -> None:
        '''Confirm if given metadata is correct'''
        accepted_resp = ['yes', 'y']
        print('Found \"{title}\" by {author}'.format(title=title, author=author))
        confirm = input('Is this ok? (y/n) ').lower()

        if confirm not in accepted_resp:
            try: self.format_metadata()
            except StopIteration:
                sys.exit('Out of results')
        else: self.author, self.title = author, title

    def metadata(self) -> Tuple[str]:
        '''Returns accepted metadata in a tuple'''
        return self.author, self.title, self.isbn_13, self.thumbnail

class DirectInput:
    '''Allows users to directly enter metadata'''

    @staticmethod
    def user_metadata_prompt() -> Tuple[str]:
        '''Prompts user input for PDF author and title'''
        print('Add the PDF author and title as comma separated values.')
        metadata = input('author, title: ').split(',', maxsplit=1)
        return tuple(m.strip() for m in metadata)
