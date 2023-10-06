# RESTful-PDF-Metadata-Updater
A simple command line PDF metadata editor that pulls info from the Google Books Dynamic Links API.

## Description

The Restful PDF Metadata Updater takes advantage of the [_Google Books Dynamic Links_](https://developers.google.com/books/docs/dynamic-links) API, which in their own words, "allows you to create more customizable, reliable links to Google Books."

The script works by taking the PDF filename and user inputs and building an API call around it. It then parses the returned _JSON_ data and prompts the user for correctness. After this it overwrites the PDF's author, title, and moddate fields while retaining everything else.

It also now supports inserting or replacing a PDF cover pages using _Google Books Static Links_ and the [_iTunes Search API_](https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/index.html) to get high resolution cover pages.

## Usage
```
useage: python metadata file [-o OUTPUT] [-a AUTHOR NAME] [-b BOOKMARK PARSER] [-i ISNB] [-c ADD COVERPAGE] [-d DROP COVERPAGE]

arguments:
file FILEPATH                           Your PDF's filepath
-o OUTPUT, --output OUTPUT              Desired output location of the updated PDF,
                                          writes to initial path if omitted
-a AUTHOR NAME, --author                Optional argument to include the author's
                                          name for better search results.
-b BOOKMARK PARSER, --bookmark          Used for instances of erroneous values encoded
                                          in the new documents outline.
-i ISBN, --isbn                         Optional argument to search by ISBN-10/13.
-c ADD COVERPAGE, --change              Optional flag to search for and add a new          
                                          cover page; requires ISBN to function. 
-d DROP COVERPAGE, --drop               Optional flag to drop existing cover page;
                                          requires ADD COVERPAGE to function.
```

The `author` and `isbn` fields are optional, but recommended, as the API supports both search by author and ISBN-10/13. But using them together isn't necessary or advisable since this could cause issues.

Regarding the `--bookmark` argument, it's an optional flag to call the `rebuild_outline` method. This is to deal with string-encoding issues that can arise when `pypdf` reads PDFs with nested outlines (bookmarks). It will also make a noticable impact on performance, since it has to iterate through every bookmark to remove potential encoding issues.

When inserting or replacing a cover page, the ISBN will determine where the script will try and find the image. For ISBN-13 it will default to the _iTunes Search API_, as they usually have higher resolution covers. But the selection of iBooks is severly limited, so the script may check _Google Books_ too. The _Google Books Static Links_ API is used for all ISBN-10's and the script will try and remove the watermark before inserting into your PDF.

## Example
The following command will get the metadata for _Statistical Inference_ by George Casella.
```sh
python metadata "Statistical Inference.pdf" -o "C:\Users\user\Statistical Inference.pdf" -a "George Casella"
```
Say you'd like to replace the cover page on your PDF too.
```
python metadata passions.pdf -i 0300186339 -c -d
```
If you want to edit a number of files at once, copy the file paths to a _.txt_ file and pass it like any other PDF.
```sh
python metadata files_to_update.txt
```