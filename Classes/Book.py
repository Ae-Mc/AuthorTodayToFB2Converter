from Classes.Functions import SearchGroupOne
import asyncio
from httpx import AsyncClient
from typing import List

from .BookHeader import BookHeader
from .Chapter import Chapter
from .Dataclasses import ChapterHeader, User


class Book:
    header: BookHeader
    client: AsyncClient
    chapters: List[Chapter]

    def __init__(self, client: AsyncClient):
        if client is None:
            self.client = AsyncClient()
        else:
            self.client = client
        self.header = BookHeader()

    async def GetBookFromUrl(self, url: str):
        await self.header.GetBookHeaderFromUrl(url, self.client)
        await self.GetBookChapters()

    async def GetBookChapters(self) -> List[Chapter]:
        self.chapters = []
        user = User("", "", await Chapter.GetUserId(self.client))
        if len(self.header.tableOfContents) > 1:
            await self.getMultipleChapters(user)
        else:
            await self.getSingleChapter(user)
        return self.chapters

    async def getMultipleChapters(self, user: User):
        tasks: List[asyncio.Task] = []
        for chapterHeader in self.header.tableOfContents:
            tasks.append(
                asyncio.create_task(
                    self.GetBookChapter(
                        self.header.GetChapterDataUrl(chapterHeader),
                        chapterHeader,
                        user,
                    )
                )
            )
        for task in tasks:
            await task
            self.chapters.append(task.result())

    async def getSingleChapter(self, user: User):
        readerPage = await self.client.get(self.header.GetReaderUrl())
        readerPage.raise_for_status()
        chapterId = int(SearchGroupOne(r"chapterId: (\d+),", readerPage.text))
        chapterHeader = ChapterHeader(self.header.title, chapterId)
        self.chapters.append(
            await self.GetBookChapter(
                self.header.GetChapterDataUrl(chapterHeader),
                chapterHeader,
                user,
            )
        )

    async def GetBookChapter(
        self, url: str, chapterHeader: ChapterHeader, user: User
    ) -> Chapter:
        chapter = Chapter(chapterHeader, self.client, user)
        await chapter.GetChapterFromUrl(url)
        return chapter
