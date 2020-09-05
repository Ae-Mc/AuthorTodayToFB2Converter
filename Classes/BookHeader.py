from typing import List
from bs4 import BeautifulSoup, Tag
from httpx import Client
from sys import stderr
from .Dataclasses import ChapterHeader, Pages


class BookHeader:
    title: str
    authors: List[str]
    tableOfContents: List[ChapterHeader]
    bookId: int
    coverImageData: bytes

    def __init__(self):
        self.authors = []
        pass

    def GetBookHeaderFromUrl(self, url: str, client: Client) -> None:
        bookPageResponse = client.get(url)
        if bookPageResponse.status_code != 200:
            print("Error! Can't get book page! Check url "
                  f"(current url: {url}).\n"
                  f"Error code: {bookPageResponse.status_code}")
            return
        DOM: BeautifulSoup = BeautifulSoup(
            bookPageResponse.text, "html.parser")
        bookPanel = DOM.select_one(".book-panel > .panel-body")
        self._GetBookHeaderFromBookPanel(bookPanel, client)

    def GetReaderUrl(self) -> str:
        return Pages.baseReaderUrl + '/' + str(self.bookId)

    def _GetBookHeaderFromBookPanel(self,
                                    bookPanel: Tag,
                                    client: Client) -> None:
        self.title = bookPanel.select_one(".book-title").text.strip()
        for author in bookPanel.select(".book-authors > span > meta"):
            self.authors.append(author.attrs["content"])
        self.annotation = (
            bookPanel.select_one(".annotation > .rich-content").text.strip())
        self.bookId = int(bookPanel.select_one(
            ".book-cover > a.book-cover-content"
        ).attrs["href"].split('/')[-1])
        self.tableOfContents = []
        toc = bookPanel.select_one("ul.table-of-content")
        if len(toc.select("li > a")) < len(toc.select("li")):
            print(f"WARNING! Book «{self.title}» has blocked chapters!"
                  " Maybe you didn't authorize or didn't purchase it?")
        for row in toc.select("li > a"):
            self.tableOfContents.append(
                ChapterHeader(row.text, row.attrs["href"].split('/')[-1], -1))
        self.coverImageData = self._GetBookCoverFromBookPanel(bookPanel,
                                                              client)

    def _GetBookCoverFromBookPanel(self,
                                   bookPanel: Tag,
                                   client: Client) -> bytes:
        coverImageTag = bookPanel.select_one(
            ".book-action-panel .book-cover .cover-image")
        imageUrl = (Pages.main
                    + coverImageTag.attrs["src"].split("?")[0])
        coverImageResponse = client.get(imageUrl)
        if coverImageResponse.status_code == 200:
            coverImageData = bytes(coverImageResponse.content)
        else:
            print("Error! Can't get book cover image!"
                  f" Error code: {coverImageResponse}",
                  file=stderr)
            coverImageData = bytes([])
        return coverImageData

    def __str__(self):
        return "{}. «{}» (id: {})\nAnnotation: {}".format(
            ", ".join(self.authors),
            self.title,
            self.bookId,
            self.annotation)

    def __repr__(self):
        return "{}. «{}» (id: {})\nAnnotation: {}".format(
            ", ".join(self.authors),
            self.title,
            self.bookId,
            self.annotation)
