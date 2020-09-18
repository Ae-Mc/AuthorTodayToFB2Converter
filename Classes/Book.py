import asyncio
from httpx import AsyncClient
from typing import List, Tuple

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
        tasks: List[asyncio.Task] = []
        user = User("", "", await Chapter.GetUserId(self.client))
        for chapterHeader in self.header.tableOfContents:
            tasks.append(asyncio.create_task(self.GetBookChapter(
                self.header.GetChapterDataUrl(chapterHeader),
                chapterHeader,
                user
            )))
        for task in tasks:
            await task
            self.chapters.append(task.result())
        return self.chapters

    async def GetBookChapter(self,
                             url: str,
                             chapterHeader: ChapterHeader,
                             user: User) -> Tuple[Chapter, int]:
        chapter = Chapter(chapterHeader, self.client, user)
        await chapter.GetChapterFromUrl(url)
        return chapter
