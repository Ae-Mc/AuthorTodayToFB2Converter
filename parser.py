from os import mkdir
from time import time

from httpx import Client, Timeout

from Classes.Book import Book
from Classes.Dataclasses import Pages
from Classes.Functions import Authorize, Logoff, SetSessionHeaders

OutputFolder = "Output"
try:
    mkdir(OutputFolder)
except FileExistsError:
    pass


with Client(base_url=Pages.main) as client:
    client._timeout = Timeout(3)
    SetSessionHeaders(client)
    t = time()
    if Authorize(client):
        book: Book = Book(client, "work/40323")
        print(book.header)
        print("-----------------\nTable of Contents\n-----------------",
              end="\n    ")
        print(*book.header.tableOfContents, sep="\n    ", end="\n\n")
        if book.header.coverImageData is not None:
            with open("Output/bookCover.jpg", "wb") as f:
                f.write(book.header.coverImageData)
        Logoff(client)
    print(f"All requests took {time() - t} seconds.")
    client.close()
