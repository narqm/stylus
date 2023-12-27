from os import remove
from xml.etree import ElementTree as ET
from zipfile import ZipFile
from typing import List, Optional

class EpubReader:

    def __init__(self, epub: str, output: Optional[str] = None,
                 replace_cover_file: Optional[bool] = False):

        if output is None:
            self.output = epub
        else: self.output = output
        self.epub_zip: ZipFile = ZipFile(epub, 'r')
        self.epub: str = epub
        self.replace: bool = replace_cover_file

    def contents(self) -> bytes:
        '''Returns contents of the content.opf metadata file'''

        for file_info in self.epub_zip.infolist():

            if 'content.opf' not in file_info.filename:
                continue

            with self.epub_zip.open(file_info) as file:
                return file.read()

    def _update_metadata(self, content: str, authors: List[str], title: str) -> str:
        '''Updates content.opf metadata'''

        opf_root: bytes = ET.fromstring(content)

        substr: str = '{http://purl.org/dc/elements/1.1/}'
        metastr: str = './/{http://www.idpf.org/2007/opf}metadata'

        title_element: Optional[int] = opf_root.find(f'.//{substr}title')
        if title_element is not None:
            title_element.text = title

        for element in opf_root.findall(f'.//{substr}creator'):
            opf_root.find(metastr).remove(element)

        for author in authors:
            creator_element = ET.Element(f'{substr}creator')
            creator_element.text = author
            opf_root.find(metastr).append(creator_element)

        return ET.tostring(opf_root, encoding='utf-8', method='xml')

    def _rebuild_epub_contents(self) -> None:
        '''Creates a copy epub without content.opf'''

        all_files: List[str] = self.epub_zip.namelist()

        if not self.replace:
            files_to_copy: List[str] = [file for file in all_files if file != 'content.opf']
        else:
            files_to_copy = [file for file in all_files if file not in ['content.opf', 'cover.jpeg']]

        with ZipFile(self.output, 'w') as new_zip:

            for file in files_to_copy:

                file_content = self.epub_zip.read(file)
                new_zip.writestr(file, file_content)

    def update_metadata(self, author: List[str], title: str) -> None:
        '''Writes ebook metadata to content.opf and appends to new epub'''

        self._rebuild_epub_contents()

        content_opf: bytes = self.contents()
        if content_opf:

            update_content = self._update_metadata(content=content_opf,
                authors=author, title=title)

            with ZipFile(self.output, 'a') as zip_ref:
                zip_ref.writestr('content.opf', update_content)

            print('Epub metadata successfully updated.')

    def replace_epub_cover(self, jpeg: str) -> None:
        '''Replace cover.jpeg with a new image'''
        with open(jpeg, 'rb') as img:
            img_binary = img.read()

        with ZipFile(self.output, 'a') as zip_ref:
            zip_ref.writestr('cover.jpeg', img_binary)

        print('Epub cover.jpeg has been changed.')
        remove('convert.jpg')

    def __del__(self):
        self.epub_zip.close()
