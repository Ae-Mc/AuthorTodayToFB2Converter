from requests import Session
from bs4 import BeautifulSoup
from os import path, mkdir


OutputFolder = "Output"
try:
    mkdir(OutputFolder)
except FileExistsError:
    pass


class Pages:
    main = "https://author.today"
    login = main + "/account/login"
    personalAccount = main + "/account/my-page"
    purchased = main + "/u/ae_mc/library/purchased"


def GetBookFirstChapter(url: str, session: Session):
    with session.get(url) as reader:
        print(reader.url)
        with open(path.join(OutputFolder,
                            url[url.find("reader") + 7:] + ".php"),
                  "w") as bookFile:
            bookFile.write(reader.text)


with Session() as session:
    with open("./PrivateConfig/mainPassword.txt") as f:
        password = f.readlines()[0]
    data = {
        "Login": "ae_mc@mail.ru",
        "Password": password
    }

    with session.post(Pages.login, data) as loginResponse:
        # print(loginResponse.text)
        pass
    with session.get(Pages.personalAccount) as personalAccountResponse:
        with open(path.join(OutputFolder, "personalAccount.php"),
                  "w") as personalAccountFile:
            personalAccountFile.write(personalAccountResponse.text)

    with session.get(Pages.purchased) as purchasedResponse:
        DOM: BeautifulSoup = BeautifulSoup(purchasedResponse.text,
                                           "html.parser")
        for book in DOM.find_all("div", attrs={"class": "bookcard"}):
            author = book.find(
                "h5", attrs={"class": "bookcard-authors"}).a.text
            title = book.find(
                "h4", attrs={"class": "bookcard-title"}).a.text
            url = Pages.main + book.find("div", attrs={
                "class": "thumb-buttons"}).find_all("a")[1]["href"]
            print(f"{author}. «{title}» ({url})")
            GetBookFirstChapter(url, session)

        with open(path.join(OutputFolder,
                            "purchased.php"),
                  "w") as purchasedFile:
            purchasedFile.write(purchasedResponse.text)
