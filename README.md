# RESTful-PDF-Metadata-Updater
A simple command line ebook metadata editor that pulls info from the Google Books Dynamic Links API.

## Description

The Restful PDF Metadata Updater takes advantage of the [_Google Books Dynamic Links_](https://developers.google.com/books/docs/dynamic-links) API, which according to Google, "allows you to create more customizable, reliable links to Google Books."

The script works by taking file name and user inputs and building an API call around it. Then formatting the returned _JSON_ and prompting the user for correctness. After this it overwrites the ebooks's author, title, and modification date fields with new values.

It also supports inserting or replacing an ebook cover page using _Google Books Static Links_ and the [_iTunes Search API_](https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/index.html) or a local file to get high resolution cover pages.

## Installation
This script requires Python 3 to run, you can get it [here](https://www.python.org/downloads/).

Run this if git is installed on your computer:
```sh
git clone https://github.com/narqm/RESTful-Ebook-Metadata-Updater.git
cd RESTful-PDF-Metadata-Updater
```
Alternatively, click on `Code > Download ZIP` and unzip the source files to a directory.
The script requires a number of dependencies. Install them by running:
```sh
pip install -r requirements.txt
```

## Usage
```
useage: python metadata file [-o OUTPUT] [-a AUTHOR NAME] [-b BOOKMARK PARSER] [-i ISNB] [-c ADD COVERPAGE] [-d DROP COVERPAGE] [-l LOCAL IMAGE] [-m MANUAL ENTRY]

arguments:
file FILEPATH                           Your files's path
-o OUTPUT, --output OUTPUT              Desired output location of the updated ebook,
                                          writes to initial path if omitted
-a AUTHOR NAME, --author                Optional argument to include the author's
                                          name for better search results.
-b BOOKMARK PARSER, --bookmark          Used for instances of erroneous values encoded
                                          in the new documents outline.
-i ISBN, --isbn                         Optional argument to search by ISBN-10/13.
-c ADD COVER PAGE, --change              Optional flag to search for and add a new          
                                          cover page; requires ISBN to function. 
-d DROP COVER PAGE, --drop              Optional flag to drop existing cover page;
                                          requires ADD COVER PAGE to function.
-l LOCAL IMAGE, --local                 Option to add a local image as cover page,
                                          requires the ADD COVER PAGE flag to be set.
-m MANUAL ENTRY, --manual               Manually enter ebook metadata.
```

Regarding the `--bookmark` argument, it's an optional flag to call the `rebuild_outline` method. This is to deal with string-encoding issues that can arise when `pypdf` reads PDFs with nested outlines (bookmarks). It will also make a noticable impact on performance, since it has to iterate through every bookmark to remove potential encoding issues.

## Example
The following command will get the metadata for _Statistical Inference_ by George Casella.
```sh
python metadata "Statistical Inference.pdf" -o "C:\Users\user\Statistical Inference.pdf" -a "George Casella"
```
Say you'd like to replace the cover page on a PDF too.
```sh
python metadata passions.pdf -i 0300186339 -c -d
```
If you want to edit a number of files at once, copy the file paths to a _.txt_ file and pass it like any other PDF.
```sh
python metadata files_to_update.txt
```
