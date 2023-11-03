from utility import RebuildOutline
from pypdf import PdfReader, Transformation
from pypdf.generic import RectangleObject
from datetime import datetime
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
    
    @staticmethod
    def get_page_dimensions(reader_object, replace_cover=False):
        '''Get first page height x width attributes'''
        if replace_cover:
            box = reader_object.pages[1].mediabox
        else:
            box = reader_object.pages[0].mediabox
        return box

    @staticmethod
    def resize_page(page, reference):
        '''Resize the page mediabox to reference page'''
        page.mediabox = RectangleObject(
            (reference[0], reference[1], reference[2], reference[3]))

    def transform_page_cover(self, page):
        '''Scales cover page dimensions to original document'''
        box = self.get_page_dimensions(page)
        ref_box = self.get_page_dimensions(self.reader, 
            replace_cover=self.replace)
        
        height, width = ref_box.height, ref_box.width
        height_scale = height / box.height
        width_scale = width / box.width

        scale = Transformation().scale(sx=width_scale, sy=height_scale)
        print(f'Vertical Scale: {height_scale}, Horizontal Scale: {width_scale}')
        page.pages[0].add_transformation(scale)

        self.resize_page(page.pages[0], ref_box)

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
            self.transform_page_cover(creader)
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