import re
from typing import List, Optional

from bs4 import BeautifulSoup
from httpx import AsyncClient

from .Dataclasses import ChapterHeader, Pages, User


class Chapter:
    header: Optional[ChapterHeader]
    paragraphs: List[str]
    userId: int
    client: AsyncClient

    def __init__(self,
                 header: ChapterHeader,
                 client: AsyncClient = None,
                 user: User = None):
        self.client = client if client else AsyncClient()
        self.userId = user.userId if user else -1
        self.header = header

    async def GetChapterFromUrl(self,
                                url: str):
        chapterResponse = await self.client.get(url)
        chapterResponse.raise_for_status()
        data = chapterResponse.json()
        if data["isSuccessful"] is True:
            text = data["data"]["text"]
            readerSecret = chapterResponse.headers["Reader-Secret"]
            chapterText = self._DecodeChapter(text, readerSecret)
            DOM: BeautifulSoup = BeautifulSoup(chapterText, "html.parser")
            self.paragraphs = []
            for paragraph in DOM.find_all("p"):
                self.paragraphs.append(paragraph.text)
        else:
            print(f"Error! Can't get chapter from url «{url}».")
            if "messages" in data and len(data["messages"]) > 0:
                if data["messages"][0] == "Paid":
                    print("Error! Book not purchased!")
                elif data["messages"][0] == "Unauthorized":
                    print("Error! Unauthorized!")
                else:
                    print(f"Error messages: ", end="")
                    print(*data['messages'],
                          sep=", ",
                          end="\n" if data['messages'][-1].endswith('.')
                          else ".\n")

    @staticmethod
    async def GetUserId(client: AsyncClient) -> int:
        personalAccountResponse = await client.get(Pages.personalAccount)
        personalAccountResponse.raise_for_status()
        responseText = personalAccountResponse.text
        searchResult = re.search(r"ga\('set', 'userId', '(\d*)'\)",
                                 responseText)
        if searchResult is not None:
            userId = int(searchResult.group(1))
        else:
            userId = -1
        return userId

    def _DecodeChapter(self,
                       chapterRawTextData: str,
                       readerSecret: str) -> str:
        cipher = "".join(reversed(readerSecret)) + "@_@"
        if self.userId != -1:
            cipher += str(self.userId)
        # encode and remove header
        l = list(chapterRawTextData.encode('utf-16'))[2:]
        # concatenate two adjacent bytes
        chapterEBytes = [(b<<8)|a for a,b in zip(l[0::2],l[1::2])]
        # utf-16 header
        chapterDBytes = [65279]
        for i in range(0, len(chapterEBytes)):
            chapterDBytes.append(chapterEBytes[i] ^ ord(cipher[i % len(cipher)]))
        # split by bytes, concatenate sequences and decode
        return bytes([b for a in chapterDBytes for b in [a>>8, a&0xff]]).decode('utf-16')

    def __str__(self):
        return (("" if self.header is None else self.header.title + "\n")
                + "\t" + "\n\t".join(self.paragraphs))
