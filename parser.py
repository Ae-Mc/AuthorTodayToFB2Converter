from os import mkdir

from requests import Session

from Classes.Dataclasses import Pages
from Classes.Functions import Authorize, GetChapter, GetUser, GetUsersBooks

OutputFolder = "Output"
try:
    mkdir(OutputFolder)
except FileExistsError:
    pass


with Session() as session:
    if Authorize(session):
        user = GetUser(session)
        print(f"\n[LOG] Successful log in as {user.username} aka {user.email} "
              f"(id: {user.userId})!")
        chapter = GetChapter(session,
                             user,
                             GetUsersBooks(session, Pages.purchased)[0],
                             0)
        print(chapter.header.title)
        print(*chapter.paragraphs, sep="\n")
