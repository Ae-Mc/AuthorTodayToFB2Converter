import re
from typing import List, Optional

from bs4 import BeautifulSoup
from httpx import Client

from .Dataclasses import ChapterHeader, Pages, User


class Chapter:
    header: Optional[ChapterHeader]
    paragraphs: List[str]
    userId: int
    client: Client

    def __init__(self,
                 url: str,
                 header: ChapterHeader = None,
                 client: Client = None,
                 user: User = None):
        if client is None:
            self.client = Client()
        else:
            self.client = client
        if user is None:
            self.userId = self._GetUserId(self.client)
        else:
            self.userId = user.userId
        self.header = header
        self.GetChapterFromUrl(url)

    def GetChapterFromUrl(self,
                          url: str):
        chapterResponse = self.client.get(url)
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
            print("Error! Can't get chapter from url «{url}».")
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
    def _GetUserId(client: Client) -> int:
        personalAccountResponse = client.get(Pages.personalAccount)
        personalAccountResponse.raise_for_status()
        responseText = personalAccountResponse.text
        searchResult = re.search(r"ga\('set', 'userId', '(\d*)'\)",
                                 responseText)
        if searchResult is not None:
            return int(searchResult.group(1))
        else:
            return -1

    def _DecodeChapter(self,
                       chapterRawTextData: str,
                       readerSecret: str) -> str:
        cipher = "".join(reversed(readerSecret)) + "@_@"
        if self.userId != -1:
            cipher += str(self.userId)
        chapterText = ""
        for i in range(0, len(chapterRawTextData)):
            chapterText += chr(
                ord(chapterRawTextData[i]) ^ ord(cipher[i % len(cipher)]))
        return chapterText

    def __str__(self):
        return (("" if self.header is None else self.header.title + "\n")
                + "\t" + "\n\t".join(self.paragraphs))
