# stylus
A simple command line ebook metadata editor that pulls info from the Google Books Dynamic Links API.

## Description

stylus takes advantage of the [_Google Books Dynamic Links_](https://developers.google.com/books/docs/dynamic-links) API, which according to Google, "allows you to create more customizable, reliable links to Google Books." It does this by passing the eBook file name (and any optional flags) to the API and caching responding metadata. It then prompts the user for correctness before cloning the original eBook metadata and applying updates.

It also supports appending and replacing eBook cover pages, which it will try to resize (retaining original aspect ratio) to the original page width. If the document has varying page widths, stylus will attempt resizing to the most common page width.

Note; stylus is an opinionated program, it will concatenate multiple author names (three or more) to `<first-author> and Others`. It will also remove any [grammatical functors](https://en.wikipedia.org/wiki/Function_word) from the eBook title. By default stylus will return the full title, this can be overwritten by using the `--short` flag. 

## Installation

Run this if git is installed on your computer:
```sh
git clone https://github.com/narqm/stylus.git
cd stylus
```
Alternatively, click on `Code > Download ZIP` and unzip the source files to a directory.
The script requires a number of dependencies. Install them by running:
```sh
pip install -r requirements.txt
```
If pip throws any errors, then just manually install dependencies. stylus is built on `pypdf`, `requests`, and `img2pdf`, installing those should resolve any issues.

## Usage
```
useage: python metadata file [-o OUTPUT] [-a AUTHOR NAME] [-b BOOKMARK PARSER] [-i ISNB] [-m MANUAL ENTRY] [-a APPEND] [-r REPLACE] [-s SHORT]

arguments:
  -h, --help            show this help message and exit
  -o, --output OUTPUT   Path to save your modified eBook to.
  --author AUTHOR       Search by eBook author.
  -i, --isbn ISBN       Search by eBook's ISBN-10 value.
  -r, --replace REPLACE
                        Replace eBook cover with given JPEG file.
  -a, --append APPEND   Appends given JPEG file to cover of eBook.
  -b, --bookmark        Reconstruct eBook table of content.
  -m, --manual          Manually enter PDF metadata.
  -s, --short           Don't use full title
```

Regarding the `--bookmark` argument, it's an optional flag to call the `rebuild_outline` method. This is to deal with string-encoding issues that can arise when `pypdf` reads PDFs with nested outlines (bookmarks).

## Example
The following command will get the metadata for _Statistical Inference_ by George Casella.
```sh
stylus "Statistical Inference.pdf" --author "George Casella" --output "Statistical Inference.pdf"
```
Say you'd like to replace the cover page on a PDF too.
```sh
stylus passions.pdf -i 0300186339
```
If you want to edit a number of files at once, copy the file paths to a _.txt_ file and pass it like any other PDF.
```sh
stylus files_to_update.txt
```
