from argparse import ArgumentParser
from pypdf import PdfReader, PdfWriter
from .imageconvert import ChangeCoverPage
from .apicall import GoogleBooksAPICall
from .formatmetadata import FormatMetadata, DirectInput
from .gui.viewerwindow import launch
from .epub import EpubReader
from .writetofile import Write
from .utility import Utilities
from pathlib import Path
from sys import exit
from shutil import copy


def check_txt_file(_file: str, isbn: str, author: str) -> list[Path]:

    if _file.endswith('.txt'):
        assert isbn is None, 'ISBN search not supported for .txt'
        assert author is None, 'Search by author isn\'t supported for .txt'
        utility = Utilities()
        files: list[Path] = utility.unpack_text_file(_file)
    else:
        files = [_file]
    return files


def ccp_handler():
    ...


def api_hander(_file: str, author: str, isbn: str) -> None:

    api_call = GoogleBooksAPICall(_file)
    url: str = api_call.build_api_request(author, isbn)  # why doesn't this have a default?

    util = Utilities()

    if not util.check_urls('key.json', url):  # why write url to file, load
                                              # and appnd to sep output file???
        api_call.call_api(url, output='results.json')
        util.add_url_to_json(url, 'key.json')
    return None


def main() -> None:

    parser = ArgumentParser()

    parser.add_argument('file', nargs='?', help='PDF file to modify')
    parser.add_argument('-o', '--output', help='Where to save the modified PDF')
    parser.add_argument('-a', '--author', help='Option to search by author')
    parser.add_argument('-i', '--isbn', type=str, help='Option to search by ISBN')
    parser.add_argument('-c', '--change', action='store_true', help='Changes file cover page')
    parser.add_argument('-d', '--drop', action='store_true', help='Drops PDF cover page')
    parser.add_argument('-b', '--bookmark', action='store_true', help='Flag to reconstruct PDF outline')
    parser.add_argument('-l', '--local', help='Use a local image file for PDF cover page')
    parser.add_argument('-m', '--manual', action='store_true', help='Manually enter PDF metadata')
    parser.add_argument('-s', '--short', action='store_true', help='Don\'t use full title')

    args = parser.parse_args()

    if args.drop: assert args.change is True, '-c required when dropping cover page'  # opinionated
    if args.local: assert args.change is not None, '--change flag is required'  # switch to only local?

    files = check_txt_file(args.file, args.isbn, args.author)

    isbn: str = args.isbn if args.isbn else ''  # why do I need this?

    for file in files:

        if args.manual:
            metadata = DirectInput.user_metadata_prompt()
        else:

            api_hander(file, args.author, isbn)

            _format: FormatMetadata = FormatMetadata()
            _format.format_metadata(short_title_bool=args.short)
            metadata = _format.metadata()

        if file.endswith('.epub'):
            assert args.change is not None, 'This file type doesn\'t support this action'

            epubreader = EpubReader(file, args.output, replace_cover_file=args.change)
            epubreader.update_metadata(author=[metadata[0]], title=metadata[1])

        epub: bool = True if file.endswith('.epub') else False

        if epub and args.change is not True:
            exit()

        if args.change and args.local:
            copy(args.local, 'convert.jpg')
            ChangeCoverPage.convert_to_pdf()

            if epub is True:
                epubreader.replace_epub_cover('convert.jpg')
                exit()

        if args.change and not args.local:
            ccp = ChangeCoverPage()
            ccp.fetch_google_preview_isbn('results.json')
            ccp.format_urls()

            search_term: str = Path(file).stem.lower().replace(' ', '+')
            ccp.fetch_itunes_preview_isbn(search_term)
            ccp.get_apple_artwork()
            ccp.write_previews_to_file()
            launch()

            if epub is not True:
                ccp.convert_to_pdf()
                ccp.delete_artwork()

            if epub is True:
                epubreader.replace_epub_cover('convert.jpg')
                ccp.delete_artwork()
                exit()

        reader = PdfReader(file)
        writer = PdfWriter()

        write = Write(metadata[0], metadata[1], reader, writer, file, args.drop)
        write.write_to_file(args.output, args.change, args.bookmark)
