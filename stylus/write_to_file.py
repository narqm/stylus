from outline_parser import RebuildOutline
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject
from os import remove, listdir, path, getcwd
from datetime import datetime
from typing import Any
from statistics import mode
from random import sample
from PIL import Image
from io import BytesIO
import img2pdf
import uuid


class Converter:
    '''Streams and resizes JPEG to img2pdf converter,
       writes img2pdf file to Random UUID.'''

    def __init__(self, _path: str, height: int, width: int):
        self._path: str = _path
        self.height: int = height
        self.width: int = width
        self.pdf_cover_path: str = f'{uuid.uuid4()}.pdf'

    def scalar(self, img_height: float, img_width: float) -> float:
        '''Calculates image transform scalar from self.height, self.width.'''
        # use a scale factor !w
        height_scale = min(self.height / img_height, 1)
        width_scale = min(self.width / img_width, 1)
        return height_scale, width_scale

    def resize_image(self) -> bytes:
        '''Function loads and resizes JPEG to given dimension.'''
        with Image.open(self._path) as im:
            resized: Image = im  # .resize((self.height, self.width))
            with BytesIO() as image_stream:
                resized.save(image_stream, format='JPEG')
                jpg_bytes: bytes = image_stream.getvalue()
        return jpg_bytes

    def convert_to_pdf(self):
        '''Passes PIL image to img2pdf convert function.'''
        resized_image: bytes = self.resize_image()
        with open(self.pdf_cover_path, 'wb') as f:
            f.write(img2pdf.convert(resized_image))


class Write:
    '''Writes metadata to PDF'''

    def __init__(self, author: str, title: str, reader: PdfReader,
                 writer: PdfWriter, _input: str, replace: bool = False,
                 image_path: str = ''):

        assert not reader.is_encrypted, 'Failed to edit - document is encrypted.'

        self.reader = reader  # metadat present
        self.writer = writer  # no metadata
        self.input = _input
        self.author = author
        self.title = title
        self.replace = replace
        self.image_path = image_path

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
        sample_size: int = self.calc_sample_size(reader_object)
        if replace_cover:
            return self.build_page_dim_sample(reader_object, sample_size)
        return reader_object.pages[0].mediabox

    @staticmethod
    def resize_page(page: Any, reference: tuple[float]) -> None:
        '''Resize the page mediabox to reference page'''
        # problem with ineffective cover_image scalar,
        # may need to scale page images too? ;_;
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

        # apply the following to Converter
        height, width = ref_box.height, ref_box.width
        height_scale = min((height / box.height), 1)
        width_scale = min((width / box.width), 1)

        scale = Transformation().scale(sx=width_scale, sy=height_scale)
        print(f'Vertical Scale: {height_scale}, Horizontal Scale: {width_scale}')
        page.pages[0].add_transformation(scale)

        self.resize_page(page.pages[0], ref_box)

    def apply_transform(self):
        '''Method applies cover_page transform and inserts into eBook.'''
        # need to apply transform ratios, and confirm units
        _dims: RectangleObject = self.get_page_dimensions(self.reader, True)
        # these need to be converted from user space units,
        # or Converter needs a scalar function
        height, width = int(_dims.height), int(_dims.width)
        converter: Converter = Converter(self.image_path, height, width)
        converter.convert_to_pdf()
        with open(converter.pdf_cover_path, 'rb') as f:
            c_reader = PdfReader(f)
            self.transform_page_cover(c_reader)
            self.writer.insert_page(c_reader.pages[0], index=0)

        remove(converter.pdf_cover_path)

    def insert_new_cover(self, replace_cover: bool = False) -> None:
        '''Adds a new book cover to PDF'''
        if replace_cover:
            self.call_rb()
            for page in self.reader.pages[1:]:
                self.writer.add_page(page)
        else:
            self.writer.clone_reader_document_root(self.reader)
            self.writer.add_metadata(self.reader.metadata)

        self.apply_transform()

    def write_to_file(self, output: str = None, insert_cover: bool = False,
                      rebuild_outline_flag: bool = False) -> None:
        '''Writes new metadata to file'''
        print('Writing metadata to file...')
        if rebuild_outline_flag:
            self.call_rb(append=True)
        elif insert_cover:
            self.insert_new_cover(replace_cover=self.replace)
        else:
            self.writer.clone_document_from_reader(self.reader)

        self.add_my_metadata(self.author, self.title)

        output: str = self.input if output is None else output

        with open(output, 'wb') as file:
            self.writer.write(file)

        # self.clean_up()

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
