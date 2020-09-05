import re
from json import loads
from typing import List

from bs4 import BeautifulSoup
from httpx import Client, Response

from .Dataclasses import Chapter, ChapterHeader, Pages, User
from .BookHeader import BookHeader


def SetSessionHeaders(client: Client):
    client.headers
    client.headers["User-Agent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/85.0.4183.83 Safari/537.36")
    client.headers["dnt"] = '1'
    client.headers["cache"] = "no-cache"
    client.headers["pragma"] = "no-cache"
    client.headers["Upgrade-Insecure-Requests"] = "1"
    client.headers["Sec-Fetch-Dest"] = "document"
    client.headers["Sec-Fetch-Mode"] = "navigate"
    client.headers["Sec-Fetch-Site"] = "same-origin"
    client.headers["Sec-Fetch-User"] = "?0"


def GetBookTableOfContents(client: Client, url: str) -> List[ChapterHeader]:
    readerResponse = client.get(url)
    responseText = readerResponse.text
    searchResult = re.search(
        r"app.init\(\"readerIndex\", \{.*chapters: "
        r"(\[.*\])"
        r",[ \n\r]*chapterProgress",
        responseText,
        re.DOTALL)
    chapters: List[ChapterHeader] = []
    if searchResult is not None and readerResponse.status_code == 200:
        rawChapters = loads(searchResult.group(1))
        for rawChapter in rawChapters:
            chapters.append(ChapterHeader(rawChapter["title"],
                                          rawChapter["id"],
                                          rawChapter["textLength"]))
    else:
        print("Error! Can't get chapters from url {url}!")
    return chapters


def GetRequestVerificationToken(response: Response) -> str:
    DOM: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
    return DOM.select_one("form#logoffForm > input").attrs["value"]


def SearchGroupOne(pattern: str, text: str) -> str:
    expr = re.compile(pattern)
    searchResult = expr.search(text)
    if searchResult is not None:
        return searchResult.group(1)
    else:
        return ""


def GetUser(client: Client) -> User:
    personalAccountResponse = client.get(Pages.personalAccount)
    responseText = personalAccountResponse.text
    user = User()
    user.username = SearchGroupOne(
        r"ChatraIntegration.name = ['\"](.*)['\"]", responseText)
    user.email = SearchGroupOne(
        r"ChatraIntegration.email = ['\"](.*)['\"]", responseText)
    searchResult = SearchGroupOne(
        r"ga\('set', 'userId', '(\d*)'\)", responseText)
    user.userId = -1 if len(searchResult) == 0 else int(searchResult)
    return user


def Authorize(client: Client) -> bool:
    with open("./PrivateConfig/mainPassword.txt") as f:
        password = f.readlines()[0]
    with open("./PrivateConfig/mail.ru-email.txt") as f:
        email = f.readlines()[0]
    data = {
        "Login": email,
        "Password": password
    }
    requestVerificationToken = GetRequestVerificationToken(
        client.get(Pages.login))
    client.headers["__RequestVerificationToken"] = requestVerificationToken
    loginResponse = client.post(Pages.login, data=data)
    del client.headers["__RequestVerificationToken"]
    if loginResponse.status_code != 200:
        print("Error! Can't log in!"
              f" Error code: {loginResponse.status_code}")
        return False
    return True


def GetUsersBooks(client: Client, url: str) -> List[BookHeader]:
    books: List[BookHeader] = []
    purchasedResponse = client.get(url)
    DOM: BeautifulSoup = BeautifulSoup(purchasedResponse.text,
                                       "html.parser")
    if purchasedResponse.status_code == 200 and DOM is not None:
        bookShelf = DOM.select_one("div.book-shelf")
        for book in bookShelf.find_all("div", attrs={"class": "bookcard"}):
            title = book.select_one(".bookcard-title > a").text
            author = book.select_one(".bookcard-authors > a").text
            url = Pages.main + book.select(
                ".thumb-buttons > a")[1]["href"]
            bookId = int(url.split("/")[-1])
            tableOfContents = GetBookTableOfContents(client, url)
            books.append(
                BookHeader(title, author, tableOfContents, bookId))
    return books


def DecodeChapter(chapterRawTextData: str,
                  user: User,
                  readerSecret: str) -> str:
    cipher = "".join(reversed(readerSecret)) + "@_@"
    if user.userId != -1:
        cipher += str(user.userId)
    chapterText = ""
    for i in range(0, len(chapterRawTextData)):
        chapterText += chr(
            ord(chapterRawTextData[i]) ^ ord(cipher[i % len(cipher)]))
    return chapterText


def GetChapter(client: Client,
               user: User,
               book: BookHeader,
               chapterNumber: int) -> Chapter:
    chapter = Chapter(book.tableOfContents[chapterNumber], [])
    chapterResponse = client.get(
        book.GetReaderUrl()
        + "/chapter?id="
        + str(book.tableOfContents[chapterNumber].chapterId))
    data = loads(chapterResponse.text)
    if chapterResponse.status_code == 200 and data["isSuccessful"] is True:
        text = data["data"]["text"]
        readerSecret = chapterResponse.headers["Reader-Secret"]
        chapterText = DecodeChapter(text, user, readerSecret)
        DOM: BeautifulSoup = BeautifulSoup(chapterText, "html.parser")
        for paragraph in DOM.find_all("p"):
            chapter.paragraphs.append(paragraph.text)
    else:
        print("Error! Can't get chapter"
              f" «{book.tableOfContents[chapterNumber].title}»"
              f" from book «{book.title}».")
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
    return chapter


def Logoff(client: Client) -> bool:
    requestVerificationToken = GetRequestVerificationToken(
        client.get(Pages.main))
    client.headers["__RequestVerificationToken"] = requestVerificationToken
    logoffResponse = client.post(Pages.logoff, allow_redirects=False)
    if logoffResponse.status_code != 302:
        print("Error! Can't log off!"
              f" Error code: {logoffResponse.status_code}")
        return False
    return True
