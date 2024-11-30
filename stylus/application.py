from argparse import ArgumentParser
from pathlib import Path
from shutil import copy
from pypdf import PdfReader, PdfWriter
from imageconvert import ChangeCoverPage
from apicall import GoogleBooksAPICall
from formatmetadata import FormatMetadata, user_metadata_prompt
from writetofile import Write
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


def main():

    parser = ArgumentParser()

    parser.add_argument('file', nargs='?', help='PDF file to modify')
    parser.add_argument('-o', '--output',
                        help='Where to save the modified PDF')
    parser.add_argument('-a', '--author', help='Option to search by author')
    parser.add_argument('-i', '--isbn', type=str,
                        help='Option to search by ISBN')
    parser.add_argument('-c', '--change', action='store_true',
                        help='Changes file cover page')
    parser.add_argument('-d', '--drop', action='store_true',
                        help='Drops PDF cover page')
    parser.add_argument('-b', '--bookmark', action='store_true',
                        help='Flag to reconstruct PDF outline')
    parser.add_argument('-m', '--manual', action='store_true',
                        help='Manually enter PDF metadata')
    parser.add_argument('-s', '--short', action='store_true',
                        help='Don\'t use full title')

    args = parser.parse_args()

    # replace args.drop + args.change with
    # args.add + args.replace?
    if args.drop:
        assert args.change, '-c required when dropping cover page.'

    files = check_txt_file(args.file, args.isbn, args.author)

    isbn: str = args.isbn if args.isbn else ''  # why do I need this?

    for file in files:

        epub_unspprt_assrt(file)

        if args.manual:
            metadata = user_metadata_prompt()
        else:

            metadata = api_handler(file, args.author, isbn)

            _format: FormatMetadata = FormatMetadata(metadata)
            _format.format_metadata(args.short)
            metadata = _format.metadata()

        if args.change:  # should consolidate this
            copy(args.local, 'convert.jpg')
            ChangeCoverPage.convert_to_pdf()

        reader = PdfReader(file)
        writer = PdfWriter()

        write = Write(metadata[0], metadata[1], reader,
                      writer, file, args.drop)
        write.write_to_file(args.output, args.change, args.bookmark)
