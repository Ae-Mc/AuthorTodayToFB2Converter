from .BookHeader import BookHeader
from requests import Session
from bs4 import BeautifulSoup


class Book():
    header: BookHeader
    session: Session

    def __init__(self, session: Session = None, url: str = None):
        if session is not None:
            self.session = session
        else:
            self.session = Session()
        self.header = BookHeader()
        if url is not None:
            self.GetBookFromUrl(url)

    def GetBookFromUrl(self, url: str):
        self.header.GetBookHeaderFromUrl(url, self.session)
