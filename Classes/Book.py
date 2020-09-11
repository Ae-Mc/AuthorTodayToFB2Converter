from httpx import Client
from typing import List

from .BookHeader import BookHeader
from .Chapter import Chapter


class Book:
    header: BookHeader
    client: Client
    chapters: List[Chapter]

    def __init__(self, client: Client = None, url: str = None):
        if client is None:
            self.client = Client()
        else:
            self.client = client
        self.header = BookHeader()
        if url is not None:
            self.GetBookFromUrl(url)

    def GetBookFromUrl(self, url: str):
        self.header.GetBookHeaderFromUrl(url, self.client)
        self.GetBookChapters()

    def GetBookChapters(self) -> List[Chapter]:
        self.chapters = []
        for chapterHeader in self.header.tableOfContents:
            self.chapters.append(
                Chapter(self.header.GetChapterDataUrl(chapterHeader),
                        chapterHeader,
                        self.client))
        return self.chapters
