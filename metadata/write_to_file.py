from datetime import datetime
from utility import RebuildOutline

class Write:
    '''Writes metadata to PDF'''
    def __init__(self, author, title, reader, writer, _input):
        
        self.reader = reader
        self.writer = writer
        self.input = _input
        self.author = author
        self.title = title

    def add_my_metadata(self, author, title):
        '''Adds metadata to file'''
        time = datetime.now().strftime(f"D\072%Y%m%d%H%M%S'-5\'00'")
        self.writer.add_metadata({'/Author': author, '/Title': title, '/ModDate': time})

    def write_to_file(self, output=None, rebuild_outline_flag=False):
        '''Writes new metadata to file'''
        if rebuild_outline_flag:
            self.writer.append(self.input, import_outline=False)
            rb = RebuildOutline(self.reader, self.writer)
            rb.rebuild_outline(outlines=self.reader.outline)
        else:
            self.writer.clone_reader_document_root(self.reader)
            self.writer.add_metadata(self.reader.metadata)
        
        print(f'Writing metadata to file...')
        self.add_my_metadata(self.author, self.title)

        if output is None: output = self.input

        with open(output, 'wb') as file:
            self.writer.write(file)
        print('PDF metadata successfully updated.')