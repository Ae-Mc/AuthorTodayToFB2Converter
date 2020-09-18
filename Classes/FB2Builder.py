import xml.etree.ElementTree as ET
from base64 import b64encode
from datetime import datetime
from typing import List, Optional
from xml.dom import minidom
from uuid import uuid4

from .Dataclasses import Sequence
from .Chapter import Chapter


class FB2Book():
    genres: List[str]
    authors: List[str]
    title: str
    annotation: Optional[str]
    keywords: Optional[List[str]]
    date: Optional[datetime]
    coverPageImages: Optional[List[bytes]]
    lang: str
    srcLang: Optional[str]
    translators: Optional[List[str]]
    sequences: Optional[List[Sequence]]
    docAuthors: List[str]
    docId: str
    docVersion: str
    chapters: List[Chapter]

    def __init__(self,
                 genres: List[str] = [],
                 authors: List[str] = [],
                 title: str = "",
                 annotation: str = None,
                 keywords: List[str] = None,
                 date: datetime = None,
                 coverPageImages: List[bytes] = None,
                 lang: str = "en",
                 srcLang: str = None,
                 translators: List[str] = None,
                 sequences: List[str] = None,
                 docId: str = str(uuid4()),
                 docAuthors: List[str] = ["Ae-Mc"],
                 docVersion: str = "1.0",
                 chapters: List[Chapter] = None):
        self.genres = genres
        self.authors = authors
        self.title = title
        self.annotation = annotation
        self.keywords = keywords
        self.date = date
        self.coverPageImages = coverPageImages
        self.lang = lang
        self.srcLang = srcLang
        self.translators = translators
        self.sequences = sequences
        self.docAuthors = docAuthors
        self.docId = docId
        self.docVersion = docVersion
        self.chapters = chapters or []

    def GetFB2(self) -> ET.Element:
        fb2Tree = ET.Element("FictionBook", attrib={
            "xmlns": "http://www.gribuser.ru/xml/fictionbook/2.0",
            "xmlns:xlink": "http://www.w3.org/1999/xlink"
        })
        self._AddDescription(fb2Tree)
        self._AddBody(fb2Tree)
        self._AddBinaries(fb2Tree)
        return fb2Tree

    def _AddDescription(self, root: ET.Element) -> None:
        description = ET.SubElement(root, "description")
        self._AddTitleInfo(description)
        self._AddDocumentInfo(description)

    def _AddTitleInfo(self, description: ET.Element) -> None:
        titleInfo = ET.SubElement(description, "title-info")
        for genre in self.genres:
            ET.SubElement(titleInfo, "genre").text = genre
        for author in self.authors:
            titleInfo.append(self.BuildAuthorNameFromStr(author, "author"))
        ET.SubElement(titleInfo, "book-title").text = self.title
        if self.annotation is not None:
            annotationElement = ET.SubElement(titleInfo, "annotation")
            for paragraph in self.annotation.split("\n"):
                ET.SubElement(annotationElement, "p").text = paragraph
        if self.keywords is not None:
            ET.SubElement(titleInfo, "keywords").text = (
                "\n".join(self.keywords))
        if self.date is not None:
            dateElement = ET.SubElement(titleInfo, "date")
            dateElement.attrib["value"] = datetime.strftime(
                self.date, "%Y-%m-%d")
            dateElement.text = self.date.strftime("%Y-%m-%d")
        if self.coverPageImages is not None:
            coverPageElement = ET.SubElement(titleInfo, "coverpage")
            for i in range(len(self.coverPageImages)):
                imageElement = ET.SubElement(coverPageElement, "image")
                imageElement.attrib["xlink:href"] = f"#cover#{i}"
                imageElement.attrib["alt"] = "cover"
        ET.SubElement(titleInfo, "lang").text = self.lang
        if self.srcLang is not None:
            ET.SubElement(titleInfo, "src-lang").text = self.srcLang
        if self.translators is not None:
            for translator in self.translators:
                titleInfo.append(
                    self.BuildAuthorNameFromStr(translator, "translator"))
        if self.sequences is not None:
            sequence: Sequence
            for sequence in self.sequences:
                ET.SubElement(titleInfo, "sequence", attrib={
                    "name": sequence.name,
                    "number": str(sequence.number)
                })

    def _AddDocumentInfo(self, description: ET.Element) -> None:
        documentInfo = ET.SubElement(description, "document-info")
        for author in self.docAuthors:
            documentInfo.append(self.BuildAuthorNameFromStr(author, "author"))
        ET.SubElement(documentInfo, "program-used").text = (
            "FB2creator by Ae-Mc")
        dateElement = ET.SubElement(documentInfo, "date")
        dateElement.text = datetime.now().strftime("%Y-%m-%d")
        dateElement.attrib["value"] = datetime.now().strftime("%Y-%m-%d")
        ET.SubElement(documentInfo, "id").text = self.docId
        ET.SubElement(documentInfo, "version").text = self.docVersion

    def _AddBody(self, root: ET.Element) -> None:
        if len(self.chapters):
            bodyElement = ET.SubElement(root, "body")
            for chapter in self.chapters:
                bodyElement.append(
                    self.BuildSectionFromChapter(chapter, chapter.header.id))

    @staticmethod
    def BuildSectionFromChapter(chapter: Chapter,
                                id: str = None) -> ET.Element:
        sectionElement = ET.Element("section")
        if id is not None:
            sectionElement.attrib["id"] = id
        ET.SubElement(sectionElement, "title").text = chapter.header.title
        for paragraph in chapter.paragraphs:
            ET.SubElement(sectionElement, "p").text = paragraph
        return sectionElement

    def _AddBinaries(self, root: ET.Element) -> None:
        if self.coverPageImages is not None:
            for i, coverImage in enumerate(self.coverPageImages):
                self._AddBinary(root, f"cover#{i}", "image/jpeg", coverImage)

    def _AddBinary(self,
                   root: ET.Element,
                   id: str,
                   contentType: str,
                   data: bytes) -> None:
        binaryElement = ET.SubElement(root, "binary")
        binaryElement.attrib = {"id": id, "content-type": contentType}
        binaryElement.text = b64encode(data).decode("utf-8")

    @staticmethod
    def BuildAuthorNameFromStr(name: str, rootTag: str) -> ET.Element:
        rootElement = ET.Element(rootTag)
        authorNameParts = name.split(' ')
        if len(authorNameParts) == 1:
            ET.SubElement(rootElement, "nickname").text = (
                authorNameParts[0])
        elif len(authorNameParts) == 2:
            ET.SubElement(rootElement, "first-name").text = (
                authorNameParts[0])
            ET.SubElement(rootElement, "last-name").text = (
                authorNameParts[1])
        elif len(authorNameParts) == 3:
            ET.SubElement(rootElement, "first-name").text = (
                authorNameParts[0])
            ET.SubElement(rootElement, "last-name").text = (
                authorNameParts[1])
            ET.SubElement(rootElement, "middle-name").text = (
                authorNameParts[2])
        return rootElement

    @staticmethod
    def _PrettifyXml(element: ET.Element):
        dom = minidom.parseString(ET.tostring(element, "utf-8"))
        return dom.toprettyxml(encoding="utf-8")
