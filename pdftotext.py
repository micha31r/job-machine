import pymupdf
import sys
import streamlit as st


def pdf_to_text(*file_paths):
    """Takes an input of arbitrary number of pdf files, reads them and outputs the plain text into `output.txt`"""

    out = open("output.txt", "w")  # create new file

    for path in file_paths:
        try:
            doc = pymupdf.open(path)  # open created
            out = open("output.txt", "a")  # create a text output

            for page in doc:  # iterate the document pages
                text = page.get_text()
                out.write(text)  # write text of page
        except pymupdf.FileNotFoundError:
            print(f"{path} reading failed")
            continue
        else:
            print(f"{path} read succesfully")

    out.close()


if __name__ == "__main__":
    pdf_to_text(*sys.argv[1:])
