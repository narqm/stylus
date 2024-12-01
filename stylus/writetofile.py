from outlineparser import RebuildOutline
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject
from os import remove, listdir, path, getcwd
from datetime import datetime
from typing import Any
from statistics import mode
from random import sample


class Write:
    '''Writes metadata to PDF'''
    def __init__(self, author: str, title: str, reader: PdfReader,
                 writer: PdfWriter, _input: str, replace: bool = False):
        assert not reader.is_encrypted, 'Failed to edit - document is encrypted.'

        self.reader = reader
        self.writer = writer
        self.input = _input
        self.author = author
        self.title = title
        self.replace = replace

    def add_my_metadata(self, author: str, title: str) -> None:
        '''Adds metadata to file'''
        time = datetime.now().strftime(f"D\072%Y%m%d%H%M%S'-5\'00'")
        self.writer.add_metadata({'/Author': author, '/Title': title, '/ModDate': time})

    def call_rb(self, append: bool = False) -> None:
        '''Calls utility.RebuildOutline on reader/writer object'''
        if append:
            self.writer.append(self.input, import_outline=False)
        rb = RebuildOutline(self.reader, self.writer)
        rb.rebuild_outline(outlines=self.reader.outline)

    @staticmethod
    def build_page_dim_sample(_input: PdfReader, _k: int) -> RectangleObject:
        '''Function builds page.width random sample off k items.'''
        index: list[int] = sample(range(len(_input.pages)), _k)
        _widths: list[float] = []
        rect_obj_collection: list[RectangleObject] = []
        # needs refactor
        for i in index:
            _widths.append(_input.pages[i].mediabox.width)
            rect_obj_collection.append(_input.pages[i].mediabox)
        _mode_width: int = mode(_widths)
        return next(rect for rect in rect_obj_collection if int(rect.width) == _mode_width)

    @staticmethod
    def calc_sample_size(_reader_object: PdfReader) -> int:
        '''Function calculates sample size from PdfReader object.'''
        num_of_pages: int = len(_reader_object.pages)
        return int(num_of_pages * .1)

    def get_page_dimensions(self, reader_object: PdfReader, replace_cover: bool = False) -> RectangleObject:
        '''Get first page height x width attributes'''
        # use len(PdfReader().pages) to get page length
        # if replace_cover:  # should rndm sample 10-20% and use mode dim
        #     box = reader_object.pages[1].mediabox
        # else:
        #     box = reader_object.pages[0].mediabox
        # return box
        sample_size: int = self.calc_sample_size(reader_object)
        if replace_cover:
            return self.build_page_dim_sample(reader_object, sample_size)
        return reader_object.pages[0].mediabox

    @staticmethod
    def resize_page(page: Any, reference: tuple[float]) -> None:
        '''Resize the page mediabox to reference page'''
        page.mediabox = RectangleObject(reference)

    def _check_new_cover(self, base: tuple[float], ref: tuple[float]) -> bool:
        '''Check new cover page dimensions against ebook'''
        if base.width <= ref.width:
            return False
        return True

    def transform_page_cover(self, page: Any) -> None:
        '''Scales cover page dimensions to original document'''
        box: RectangleObject = self.get_page_dimensions(page)
        ref_box: RectangleObject = self.get_page_dimensions(self.reader, self.replace)

        if not self._check_new_cover(box, ref_box):
            return

        height, width = ref_box.height, ref_box.width
        height_scale = min((height / box.height), 1)
        width_scale = min((width / box.width), 1)

        scale = Transformation().scale(sx=width_scale, sy=height_scale)
        print(f'Vertical Scale: {height_scale}, Horizontal Scale: {width_scale}')
        page.pages[0].add_transformation(scale)

        self.resize_page(page.pages[0], ref_box)

    def insert_new_cover(self, replace_cover: bool = False) -> None:
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

    def write_to_file(self, output: bool = None, insert_cover: bool = False,
                      rebuild_outline_flag: bool = False) -> None:
        '''Writes new metadata to file'''
        if rebuild_outline_flag: self.call_rb(append=True)
        elif insert_cover: self.insert_new_cover(replace_cover=self.replace)
        else:
            self.writer.clone_reader_document_root(self.reader)
            self.writer.add_metadata(self.reader.metadata)

        print('Writing metadata to file...')
        self.add_my_metadata(self.author, self.title)

        if output is None: output = self.input

        with open(output, 'wb') as file:
            self.writer.write(file)

        self.clean_up()

        print('PDF metadata successfully updated.')

    def clean_up(self):
        '''Clean up JSON search files'''
        origin = getcwd()

        content = listdir(origin)
        if 'key.json' in content:
            key = path.join(origin, 'key.json')
            remove(key)

        if 'results.json' in content:
            results = path.join(origin, 'results.json')
            remove(results)
