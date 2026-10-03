"""Сохранение и чтение документов: JSON и XML."""

import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import Any

from exceptions import EditorError, StorageError
from models import Document


class Storage(ABC):
    """Базовый класс файлового хранилища."""

    @abstractmethod
    def save(self, documents: list[Document], path: str) -> None:
        """Записывает документы в файл."""

    @abstractmethod
    def load(self, path: str) -> list[Document]:
        """Читает документы из файла."""


class JsonStorage(Storage):
    """Хранение в формате JSON."""

    def save(self, documents: list[Document], path: str) -> None:
        data = {"documents": [d.to_dict() for d in documents]}
        try:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except OSError as exc:
            raise StorageError(f"Не удалось записать файл: {exc}") from exc

    def load(self, path: str) -> list[Document]:
        try:
            with open(path, encoding="utf-8") as file:
                data = json.load(file)
            return [Document.from_dict(d) for d in data["documents"]]
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(f"Не удалось прочитать файл: {exc}") from exc
        except (KeyError, TypeError, ValueError, EditorError) as exc:
            raise StorageError(f"Неверные данные в файле: {exc}") from exc


def _font_to_xml(parent: ET.Element, font: dict[str, Any]) -> None:
    ET.SubElement(parent, "font", name=font["name"], size=str(font["size"]),
                  bold=str(font["bold"]))


class XmlStorage(Storage):
    """Хранение в формате XML (ElementTree)."""

    def save(self, documents: list[Document], path: str) -> None:
        root = ET.Element("documents")
        for document in documents:
            data = document.to_dict()
            doc_node = ET.SubElement(root, "document", title=data["title"])
            ET.SubElement(doc_node, "author", **data["author"])
            elements = ET.SubElement(doc_node, "elements")
            for item in data["elements"]:
                node = ET.SubElement(elements, "element", type=item["type"])
                if item["type"] == "heading":
                    node.set("level", str(item["level"]))
                ET.SubElement(node, "text").text = item["text"]
                _font_to_xml(node, item["font"])
            comments = ET.SubElement(doc_node, "comments")
            for item in data["comments"]:
                node = ET.SubElement(comments, "comment",
                                     element_index=str(item["element_index"]))
                ET.SubElement(node, "author", **item["author"])
                ET.SubElement(node, "text").text = item["text"]
        tree = ET.ElementTree(root)
        ET.indent(tree)  # красивые отступы
        try:
            tree.write(path, encoding="utf-8", xml_declaration=True)
        except OSError as exc:
            raise StorageError(f"Не удалось записать файл: {exc}") from exc

    def load(self, path: str) -> list[Document]:
        try:
            root = ET.parse(path).getroot()
        except (OSError, ET.ParseError) as exc:
            raise StorageError(f"Не удалось прочитать файл: {exc}") from exc
        try:
            return [self._read_document(node)
                    for node in root.findall("document")]
        except (KeyError, AttributeError, ValueError, EditorError) as exc:
            raise StorageError(f"Неверные данные в файле: {exc}") from exc

    @staticmethod
    def _read_document(node: ET.Element) -> Document:
        """Собирает словарь из XML-узла и создаёт Document."""
        elements = []
        for item in node.findall("elements/element"):
            font = item.find("font").attrib
            element = {"type": item.attrib["type"],
                       "text": item.findtext("text", ""),
                       "font": {"name": font["name"], "size": font["size"],
                                "bold": font["bold"] == "True"}}
            if "level" in item.attrib:
                element["level"] = item.attrib["level"]
            elements.append(element)
        comments = [{"author": dict(c.find("author").attrib),
                     "text": c.findtext("text", ""),
                     "element_index": c.attrib["element_index"]}
                    for c in node.findall("comments/comment")]
        return Document.from_dict({
            "title": node.attrib["title"],
            "author": dict(node.find("author").attrib),
            "elements": elements, "comments": comments})
