import asyncio
from time import time

from httpx import AsyncClient, Timeout

from Classes.Book import Book
from Classes.Dataclasses import Pages
from Classes.FB2Builder import FB2Book
from Classes.Functions import Authorize, Logoff, SetSessionHeaders


async def main():
    async with AsyncClient(base_url=Pages.main) as client:
        client._timeout = Timeout(3)
        SetSessionHeaders(client)
        t = time()
        with open("./PrivateConfig/mainPassword.txt") as f:
            password = f.readlines()[0]
        with open("./PrivateConfig/mail.ru-email.txt") as f:
            email = f.readlines()[0]
        if await Authorize(client, email, password):
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
            with open("Output/test.fb2", 'wb') as f:
                if book.header.coverImageData is None:
                    coverImages = None
                else:
                    coverImages = [book.header.coverImageData]
                if book.header.sequence is None:
                    sequences = None
                else:
                    sequences = [book.header.sequence]
                fb2 = FB2Book(genres=book.header.genres,
                              authors=book.header.authors,
                              title=book.header.title,
                              annotation=book.header.annotation,
                              keywords=book.header.tags,
                              date=book.header.publicationDate,
                              coverPageImages=coverImages,
                              lang="ru",
                              sequences=sequences,
                              chapters=await book.GetBookChapters())
                f.write(FB2Book._PrettifyXml(fb2.GetFB2()))
            await Logoff(client)
        print(f"All requests took {time() - t} seconds.")


asyncio.get_event_loop().run_until_complete(main())
