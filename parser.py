from os import mkdir
from time import time

from httpx import Timeout
from Classes.DDOSClient import Client

from Classes.Dataclasses import Pages
from Classes.Functions import Authorize, GetChapter, GetUser, GetUsersBooks
from Classes.Functions import Logoff, SetSessionHeaders
from Classes.Book import Book

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
        book = Book(client, "/work/40323")
        print(book.header)
        print("-----------------\nTable of Contents\n-----------------",
              end="\n    ")
        print(*book.header.tableOfContents, sep="\n    ", end="\n\n")
        with open("Output/bookCover.jpg", "wb") as f:
            f.write(book.header.coverImageData)
        Logoff(client)
    print(f"All requests took {time() - t} seconds.")
    client.close()
