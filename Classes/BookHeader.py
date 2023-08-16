from datetime import datetime
from typing import List, Optional

from bs4 import BeautifulSoup, Tag
from httpx import AsyncClient

from .Dataclasses import ChapterHeader, Pages, Sequence
from .Functions import SearchGroupOne


class BookHeader:
    title: str
    annotation: str
    bookId: int
    sequence: Optional[Sequence]
    genres: List[str]
    authors: List[str]
    tags: List[str]
    tableOfContents: List[ChapterHeader]
    coverImageData: Optional[bytes]
    publicationDate: datetime

    def __init__(self):
        self.authors = []

    async def GetBookHeaderFromUrl(
        self, url: str, client: AsyncClient
    ) -> None:
        bookPageResponse = await client.get(url)
        print(bookPageResponse.headers)
        bookPageResponse.raise_for_status()
        DOM: BeautifulSoup = BeautifulSoup(
            bookPageResponse.text, "html.parser"
        )
        bookPanel = DOM.select_one(".book-panel > .panel-body")
        if bookPanel:
            await self._GetBookHeaderFromBookPanel(bookPanel, client)

    def GetReaderUrl(self) -> str:
        return Pages.baseReaderUrl + "/" + str(self.bookId)

    def GetChapterReaderUrl(self, chapter: ChapterHeader) -> str:
        return Pages.baseReaderUrl + f"/{self.bookId}?chapterId={chapter.id}"

    def GetChapterDataUrl(self, chapter: ChapterHeader) -> str:
        return Pages.baseReaderUrl + f"/{self.bookId}/chapter?id={chapter.id}"

    async def _GetBookHeaderFromBookPanel(
        self, bookPanel: Tag, client: AsyncClient
    ) -> None:
        bookTitle = bookPanel.select_one(".book-title")
        self.title = bookTitle.text.strip() if bookTitle else ""
        for author in bookPanel.select(".book-authors > span > meta"):
            self.authors.append(author.attrs["content"])
        bookAnnotation = bookPanel.select_one(".annotation > .rich-content")
        self.annotation = bookAnnotation.text.strip() if bookAnnotation else ""
        bookReaderLink = bookPanel.select_one(
            ".book-cover > a.book-cover-content"
        )
        self.bookId = (
            int(bookReaderLink.attrs["href"].split("/")[-1])
            if bookReaderLink
            else -1
        )
        self.tableOfContents = self._GetBookTableOfContentsFromBookPanel(
            bookPanel
        )
        self.coverImageData = await self._GetBookCoverFromBookPanel(
            bookPanel, client
        )
        self.sequence = self._GetBookSequenceFromBookPanel(bookPanel)
        self.genres = [a.text for a in bookPanel.select(".book-genres > a")]
        self.tags = [a.text for a in bookPanel.select(".tags > a")]
        bookPublicationDate = bookPanel.find(
            "span",
            attrs={"class": "hint-top", "data-format": "calendar-short"},
        )
        self.publicationDate = (
            datetime.fromisoformat(
                bookPublicationDate.attrs["data-time"][:-2].replace("T", " ")
            )
            if bookPublicationDate
            else datetime.fromtimestamp(0)
        )

    def _GetBookTableOfContentsFromBookPanel(
        self, bookPanel: Tag
    ) -> List[ChapterHeader]:
        tableOfContents = []
        toc = bookPanel.select_one("ul.table-of-content")
        if toc:
            if len(toc.select("li > a")) < len(toc.select("li")):
                print(
                    f"WARNING! Book «{self.title}» has blocked chapters!"
                    " Maybe you didn't authorize or didn't purchase it?"
                )
            for row in toc.select("li > a"):
                tableOfContents.append(
                    ChapterHeader(row.text, row.attrs["href"].split("/")[-1])
                )
        return tableOfContents

    async def _GetBookCoverFromBookPanel(
        self, bookPanel: Tag, client: AsyncClient
    ) -> Optional[bytes]:
        coverImageTag = bookPanel.select_one(
            ".book-action-panel .book-cover .cover-image"
        )
        if coverImageTag is None:
            return None
        else:
            imageUrl = coverImageTag.attrs["src"].split("?")[0]
            coverImageResponse = await client.get(imageUrl)
            coverImageResponse.raise_for_status()
            coverImageData = bytes(coverImageResponse.content)
            return coverImageData

    def _GetBookSequenceFromBookPanel(
        self, bookPanel: Tag
    ) -> Optional[Sequence]:
        seqSpan = bookPanel.find(
            "span", attrs={"class": "text-muted"}, text="Цикл: "
        )
        if seqSpan is None:
            return None

        seqName = seqSpan.findNext("a")
        seqNumber = seqName.findNext("span")
        sequence = Sequence(
            seqName.text, int(SearchGroupOne(r"(\d+)", seqNumber.text))
        )
        if len(sequence.name) == 0 or sequence.number == 0:
            return None
        return sequence

    def __str__(self):
        return (
            "{}. «{}» (".format(", ".join(self.authors), self.title)
            + (
                "sequence: {} #{}, ".format(
                    self.sequence.name, self.sequence.number
                )
                if self.sequence is not None
                else ""
            )
            + "id: {}, publication date: {})"
            "\nGenres: {}\nTags: {}\nAnnotation: {}"
        ).format(
            self.bookId,
            self.publicationDate,
            ", ".join(self.genres),
            ", ".join(self.tags),
            self.annotation,
        )

    def __repr__(self):
        return (
            "{}. «{}» (".format(", ".join(self.authors), self.title)
            + "sequence: {} #{}, ".format(
                self.sequence.name, self.sequence.number
            )
            if self.sequence is not None
            else "" + "id: {}, publication date: {})"
            "\nGenres: {}\nTags: {}\nAnnotation: {}"
        ).format(
            self.bookId,
            self.publicationDate,
            ", ".join(self.genres),
            ", ".join(self.tags),
            self.annotation,
        )
