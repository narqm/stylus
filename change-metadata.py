import re
from datetime import datetime
from pypdf import PdfReader
from pypdf import PdfWriter
import requests
from pathlib import Path
import argparse
import sys

class Metadata():
    '''Performs a search of GoogleBooks for the metadata
    of a given file and returns search results.Then appends 
    metadata to a new file and overwrites erroneous fields.'''

    def __init__(self, file):
        '''Initializes the class and sets file path and result key.'''
        self.file = file
        self.key = 0
    
    def validate_file_path(self):
        '''Checks if file path is valid and is a PDF.'''
        test_file = Path(self.file)
        if not Path.is_file(test_file):
            print('This file doesn\'t exist. Please try again.')
            sys.exit()
        
        if test_file.suffix != '.pdf':
            print('Invalid file type. Only PDfs are accepted')
            sys.exit()

    def build_api_request(self, author=''):
        '''Builds the GoogleBooks API call.'''
        file_name = Path(self.file).stem.lower()
        if ',' in file_name:
            file_name = file_name.split(',')[0]
        
        self.name = file_name.replace(' ', '+')

        self.url = 'https://www.googleapis.com/' \
                        f'books/v1/volumes?q={self.name}'

        if author is not None:
            author = author.replace(' ', '+').lower()
            self.url = f'{self.url}+inauthor:{author}'

    def call_api(self):
        '''Sends a GET request to the API and returns results.'''
        print(f'Sending request to {self.url}.')

        r = requests.get(self.url)
        s = r.json()

        self.results = []

        for num, _ in enumerate(s):
            api_info = s['items'][num]['volumeInfo']
            self.results.append(api_info)
    
    def format_info(self):
        '''Saves metadata to PDF.'''
        query = self.results[self.key]
        api_authors = query['authors']
        self.title = query['title']
        self.author = ''

        if len(api_authors) > 1:
            if len(api_authors) >= 3:
                for element in api_authors[:-1]:
                    self.author += f'{element}, '
                self.author += f'and {api_authors[-1]}'      
            else:
                self.author = ' and '.join(api_authors)
        else:
            self.author = api_authors[0]

        check_author_names = []
        for part in self.author.split(' '):
            if len(part) <= 1:
                part += '.'
            check_author_names.append(part)
        self.author = ' '.join(check_author_names)

    def confirm_info(self):
        '''Confirm if the metadata is correct.'''
        print(f'Found {self.title} by {self.author}.')
        print('Is this information correct? Y[es]\\N[o].')
        
        accepted_responses = ['yes', 'y']
        user_response = input('> ')

        if user_response.lower() not in accepted_responses:
            self.key += 1
            try:
                Metadata.format_info(self)
            except IndexError:
                print('Out of results.')
                sys.exit()
            Metadata.confirm_info(self)
    
    def extract_text(s):
        '''Basic text extraction and cleaning.'''
        pattern = r'b[\'"](.*)[\'"]'
        matches = re.search(pattern, s.replace('\\x00', ''))
        if matches:
            return matches.group(1)
        return s.replace('\\x00', '')

    def _lists(self, outline_list, parent):
        '''Recursively searches through outline lists 
        and prints the title and page number.'''
        for sub_sect in outline_list:
            if isinstance(sub_sect, list):
                Metadata._lists(self, sub_sect, child_parent)
            else:
                new_title = Metadata.extract_text(sub_sect['/Title'])
                page_number = self.reader.get_destination_page_number(sub_sect)
                child_parent = self.writer.add_outline_item(
                    new_title, page_number, parent)

    def outline_rebuilder(self):
        '''Rebuilds the PDF's outline after cleaning up 
            any possible string-encoding issues.'''   
        for outline in self.outlines:
            if isinstance(outline, list):
                Metadata._lists(self, outline, main_parent)
            else:
                page_number = self.reader.get_destination_page_number(outline)
                main_parent = self.writer.add_outline_item(
                    outline['/Title'], page_number)
    
    def write_to_file(self, output='', outline_flag=False):
        '''Appends the metadata to a new file
            and overwrites erroneous fields.'''
        self.reader = PdfReader(self.file)
        self.writer = PdfWriter()
        self.output = output

        if outline_flag is True:
            self.writer.append(self.file, import_outline=False)
            self.outlines = self.reader.outline
            Metadata.outline_rebuilder(self)
        
        else:
            self.writer.append(self.file)

        old_metadata = self.reader.metadata

        if old_metadata is not None:
            self.writer.add_metadata(old_metadata)

        utc_time = '-5\'00'
        time = datetime.now().strftime(
            f"D\072%Y%m%d%H%M%S{utc_time}"
        )

        self.writer.add_metadata(
            {
                '/Author': self.author,
                '/Title': self.title,
                '/ModDate': time
            }
        )

        if self.output is None:
            self.output = self.file
        
        with open(self.output, 'wb') as file:
            self.writer.write(file)

if __name__ == '__main__':

    accepted_files = ['.pdf']

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=str, action='store', 
        help='The path of your PDF file')
    parser.add_argument('-o', '--output', type=str, required=False,
        help='Ouput path for your file')
    parser.add_argument('-a', '--author', type=str, required=False,
        help='Add author name to search term')
    parser.add_argument('-b', '--debug_bookmark', 
        required=False, action='store_true')
    
    args = parser.parse_args()

    pdf_file = Path(args.path)
    pdf_author = args.author
    file_output = args.output
    b_flag = args.debug_bookmark

    if pdf_file.suffix not in accepted_files:
        raise ValueError(f'{pdf_file.stem} is not a valid file type.')

    try:
        metadata = Metadata(file=pdf_file)
        metadata.validate_file_path()
        metadata.build_api_request(author=pdf_author)
        metadata.call_api()
        metadata.format_info()
        metadata.confirm_info()
        print("Writing metadata to file...")
        metadata.write_to_file(output=file_output, outline_flag=b_flag)
        print('PDF metadata successfully updated.')
    except EOFError as e:
        print('Program aborted.')
        sys.exit()