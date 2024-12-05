from argparse import ArgumentParser
from pathlib import Path
from shutil import copy
from pypdf import PdfReader, PdfWriter
from image_convert import ChangeCoverPage
from apicall import GoogleBooksAPICall
from format_metadata import FormatMetadata, user_metadata_prompt
from write_to_file import Write
from utility import Utilities


def check_txt_file(_file: str, isbn: str, author: str) -> list[Path]:
    '''Function checks filepath extension and returns list obj'''
    if _file.endswith('.txt'):
        assert isbn is None, 'ISBN search not supported for .txt'
        assert author is None, 'Search by author isn\'t supported for .txt'
        utility = Utilities()
        files: list[Path] = utility.unpack_text_file(_file)
    else:
        files = [_file]
    return files


def api_handler(_file: str, author: str, isbn: str):
    '''Function handles api_call and write to file'''
    api_call = GoogleBooksAPICall(_file)
    url: str = api_call.build_api_request(author, isbn)  # why doesn't this have a default?

    # util = Utilities()

    return api_call.call_api(url)

    # if not util.check_urls('key.json', url):  # why write url to file, load
                                                # and appnd to sep output file???
    #     return api_call.call_api(url)


def epub_unspprt_assrt(_file: str):
    '''Assert file extension is not epub,
       epub support has been deprecated'''
    epub: bool = _file.endswith('.epub')
    assert not epub, 'stylus not longer supports .epub.'


def cover_page_setup(_replace: str):
    '''Function setup local files for ChangeCoverPage.'''
    if _replace:
        copy(_replace, 'convert.jpg')
        ChangeCoverPage.convert_to_pdf()

def main():

    parser = ArgumentParser()

    parser.add_argument('file', nargs='?', help='Path to your eBook.')
    parser.add_argument('-o', '--output',
                        help='Path to save your modified eBook to.')
    parser.add_argument('--author', help='Search by eBook author.')
    parser.add_argument('-i', '--isbn', type=str,
                        help='Search by eBook\'s ISBN-10 value.')
    # needs to to accpt image path
    parser.add_argument('-r', '--replace', action='store',
                        help='Replace eBook cover with given JPEG file.')
    parser.add_argument('-a', '--append', action='store',
                        help='Appends given JPEG file to cover of eBook.')
    parser.add_argument('-b', '--bookmark', action='store_true',
                        help='Reconstruct eBook table of content.')
    parser.add_argument('-m', '--manual', action='store_true',
                        help='Manually enter PDF metadata.')
    parser.add_argument('-s', '--short', action='store_true',
                        help='Don\'t use full title')

    args = parser.parse_args()

    # replace args.drop + args.change with
    # args.add + args.replace?

    files = check_txt_file(args.file, args.isbn, args.author)

    isbn: str = args.isbn if args.isbn else ''  # why do I need this?
    # issue passwing reader2writer metadata without args.replace
    _insert_cover: bool = True if (args.replace or args.append) else False
    _drop: bool = False
    if args.replace:
        _drop = True

    if (args.replace or args.append):
        _filepath: str = args.replace if args.replace else args.append
    else:
        _filepath = ''

    for file in files:

        epub_unspprt_assrt(file)

        if args.manual:
            metadata = user_metadata_prompt()
        else:

            metadata = api_handler(file, args.author, isbn)

            _format: FormatMetadata = FormatMetadata(metadata)
            _format.format_metadata(args.short)
            metadata = _format.metadata()

        # cover_page_setup(_filepath)

        _reader = PdfReader(file)
        _writer = PdfWriter()

        write = Write(author=metadata[0], title=metadata[1], reader=_reader,
                      writer=_writer, _input=file, replace=_drop, image_path=_filepath)
        write.write_to_file(output=args.output, insert_cover=_insert_cover,
                            rebuild_outline_flag=args.bookmark)
