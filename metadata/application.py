from pypdf import PdfReader, PdfWriter
from api_call import GoogleBooksAPICall
from format_metadata import FormatMetadata
from write_to_file import Write
from utility import Utilities
import argparse

def main():
    
    parser = argparse.ArgumentParser()

    parser.add_argument('file', nargs='?', help='PDF file to modify')
    parser.add_argument('-o', '--output', help='Where to save the modified PDF')
    parser.add_argument('-a', '--author', help='Option to search by author')
    parser.add_argument('-i', '--isbn', type=str, help='Option to search by ISBN')
    parser.add_argument('-b', '--bookmark', action='store_true', 
                        help='Flag to reconstruct PDF outline')

    args = parser.parse_args()
        
    if args.isbn is None:
        isbn = ''
    else: isbn = args.isbn

    if args.file.endswith('.txt'):
        assert args.isbn is None, 'ISBN search not supported for .txt'
        assert args.author is None, 'Search by author isn\'t supported for .txt'
        utility = Utilities()
        file = utility.unpack_text_file(args.file)
    else: file = [args.file]

    for file in file:
        api_call = GoogleBooksAPICall(file)
        url = api_call.build_api_request(args.author, isbn)

        api_call.call_api(url, output='results.json')

        _format = FormatMetadata()
        _format.format_metadata()
        metadata = _format.metadata()

        reader = PdfReader(file)
        writer = PdfWriter()

        write = Write(metadata[0], metadata[1], reader, writer, file)
        write.write_to_file(args.output, args.bookmark)