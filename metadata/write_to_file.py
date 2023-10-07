from utility import RebuildOutline
from datetime import datetime
from pypdf import PdfReader
from os import remove

class Write:
    '''Writes metadata to PDF'''
    def __init__(self, author, title, reader, writer, _input, replace=False):
        
        self.reader = reader
        self.writer = writer
        self.input = _input
        self.author = author
        self.title = title
        self.replace = replace

    def add_my_metadata(self, author, title):
        '''Adds metadata to file'''
        time = datetime.now().strftime(f"D\072%Y%m%d%H%M%S'-5\'00'")
        self.writer.add_metadata({'/Author': author, '/Title': title, '/ModDate': time})
    
    def call_rb(self, append=False):
        '''Calls utility.RebuildOutline on reader/writer object'''
        if append: 
            self.writer.append(self.input, import_outline=False)
        else: 
            try: self.writer.add_metadata(self.reader)
            except: print('Error: File is missing data.')
        rb = RebuildOutline(self.reader, self.writer)
        rb.rebuild_outline(outlines=self.reader.outline)
    
    def insert_new_cover(self, replace_cover=False):
        '''Adds a new book cover to PDF'''
        if replace_cover: 
            self.call_rb()
            for page in self.reader.pages[1:]:
                self.writer.add_page(page)
        else:
            self.writer.clone_reader_document_root(self.reader)
            self.writer.add_metadata(self.reader.metadata)
        with open('cover_page.pdf', 'rb') as f:
            creader = PdfReader(f)
            self.writer.insert_page(creader.pages[0], index=0)
        
        remove('cover_page.pdf')

    def write_to_file(self, output=None, insert_cover=False, rebuild_outline_flag=False):
        '''Writes new metadata to file'''
        if rebuild_outline_flag: self.call_rb(append=True)
        elif insert_cover: self.insert_new_cover(replace_cover=self.replace)
        else:
            self.writer.clone_reader_document_root(self.reader)
            self.writer.add_metadata(self.reader.metadata)

        print(f'Writing metadata to file...')
        self.add_my_metadata(self.author, self.title)

        if output is None: output = self.input

        with open(output, 'wb') as file:
            self.writer.write(file)
        print('PDF metadata successfully updated.')