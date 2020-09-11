import asyncio
from time import time

from httpx import AsyncClient, Timeout

from Classes.Book import Book
from Classes.Dataclasses import Pages
from Classes.Functions import Authorize, Logoff, SetSessionHeaders


async def main():
    async with AsyncClient(base_url=Pages.main) as client:
        client._timeout = Timeout(3)
        SetSessionHeaders(client)
        t = time()
        if await Authorize(client):
            book: Book = Book(client)
            await book.GetBookFromUrl("work/40323")
            print(book.header)
            print("-----------------\nTable of Contents\n-----------------",
                  end="\n")
            for chapterHeader in book.header.tableOfContents:
                print(chapterHeader)
            if book.header.coverImageData is not None:
                with open("Output/bookCover.jpg", "wb") as f:
                    f.write(book.header.coverImageData)
            await Logoff(client)
        print(f"All requests took {time() - t} seconds.")


asyncio.get_event_loop().run_until_complete(main())
