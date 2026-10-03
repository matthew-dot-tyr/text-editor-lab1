"""Классы предметной области «Текстовый редактор»."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from exceptions import (
    DocumentNotFoundError,
    EmptyTitleError,
    InvalidFontSizeError,
    InvalidIndexError,
)


class User:
    """Пользователь (автор документа или комментария)."""

    def __init__(self, name: str, email: str) -> None:
        if not name.strip():
            # встроенное исключение ValueError
            raise ValueError("Имя пользователя не может быть пустым")
        self.name = name.strip()
        self.email = email

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "email": self.email}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User":
        return cls(data["name"], data["email"])


class Font:
    """Шрифт: название, размер и жирность."""

    def __init__(self, name: str = "Arial", size: int = 12,
                 bold: bool = False) -> None:
        self.name = name
        self.bold = bold
        self._size = 12
        self.size = size  # проверка выполняется в setter

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        if not 6 <= value <= 72:
            raise InvalidFontSizeError(
                f"Размер шрифта {value} не входит в диапазон 6..72")
        self._size = value

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "size": self.size, "bold": self.bold}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Font":
        return cls(data["name"], int(data["size"]), bool(data["bold"]))


class TextElement(ABC):
    """Абстрактный элемент документа (базовый класс)."""

    def __init__(self, text: str, font: Optional[Font] = None) -> None:
        self.text = text
        self.font = font or Font()

    @abstractmethod
    def get_info(self) -> str:
        """Текст элемента для показа на экране."""

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Преобразование элемента в словарь."""

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "TextElement":
        """Создаёт Paragraph или Heading в зависимости от поля type."""
        font = Font.from_dict(data["font"])
        if data["type"] == "heading":
            return Heading(data["text"], int(data["level"]), font)
        return Paragraph(data["text"], font)


class Paragraph(TextElement):
    """Обычный абзац текста."""

    def get_info(self) -> str:
        return self.text

    def to_dict(self) -> dict[str, Any]:
        return {"type": "paragraph", "text": self.text,
                "font": self.font.to_dict()}


class Heading(TextElement):
    """Заголовок с уровнем (1, 2 или 3)."""

    def __init__(self, text: str, level: int = 1,
                 font: Optional[Font] = None) -> None:
        super().__init__(text, font)
        if level not in (1, 2, 3):
            raise ValueError("Уровень заголовка должен быть 1, 2 или 3")
        self.level = level

    def get_info(self) -> str:
        return f"{'#' * self.level} {self.text}"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "heading", "level": self.level, "text": self.text,
                "font": self.font.to_dict()}


class Comment:
    """Комментарий к элементу документа."""

    def __init__(self, author: User, text: str, element_index: int) -> None:
        self.author = author
        self.text = text
        self.element_index = element_index

    def to_dict(self) -> dict[str, Any]:
        return {"author": self.author.to_dict(), "text": self.text,
                "element_index": self.element_index}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Comment":
        return cls(User.from_dict(data["author"]), data["text"],
                   int(data["element_index"]))


class Document:
    """Документ: список элементов и комментариев."""

    def __init__(self, title: str, author: User) -> None:
        if not title.strip():
            raise EmptyTitleError("Название документа не может быть пустым")
        self.title = title.strip()
        self.author = author
        self.elements: list[TextElement] = []
        self.comments: list[Comment] = []

    def _check_index(self, index: int) -> None:
        """Проверяет номер элемента (нумерация с 0)."""
        if not 0 <= index < len(self.elements):
            raise InvalidIndexError(
                f"Элемента {index + 1} нет (всего {len(self.elements)})")

    # --- CRUD для элементов документа ---
    def add_element(self, element: TextElement) -> None:
        """Create: добавляет элемент в конец документа."""
        self.elements.append(element)

    def get_element(self, index: int) -> TextElement:
        """Read: возвращает элемент по номеру."""
        self._check_index(index)
        return self.elements[index]

    def update_element(self, index: int, text: str) -> None:
        """Update: меняет текст элемента."""
        self._check_index(index)
        self.elements[index].text = text

    def delete_element(self, index: int) -> None:
        """Delete: удаляет элемент."""
        self._check_index(index)
        del self.elements[index]

    # --- остальные операции ---
    def add_comment(self, author: User, text: str, index: int) -> None:
        self._check_index(index)
        self.comments.append(Comment(author, text, index))

    def find(self, query: str) -> list[int]:
        """Возвращает номера элементов (с 1), содержащих строку."""
        return [i + 1 for i, el in enumerate(self.elements)
                if query.lower() in el.text.lower()]

    def replace_all(self, old: str, new: str) -> int:
        """Заменяет текст во всём документе, возвращает число замен."""
        count = 0
        for element in self.elements:
            count += element.text.count(old)
            element.text = element.text.replace(old, new)
        return count

    def show(self) -> str:
        lines = [f"=== {self.title} (автор: {self.author.name}) ==="]
        for number, element in enumerate(self.elements, start=1):
            lines.append(f"{number}. {element.get_info()}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "author": self.author.to_dict(),
                "elements": [e.to_dict() for e in self.elements],
                "comments": [c.to_dict() for c in self.comments]}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Document":
        document = cls(data["title"], User.from_dict(data["author"]))
        document.elements = [TextElement.from_dict(e)
                             for e in data["elements"]]
        document.comments = [Comment.from_dict(c) for c in data["comments"]]
        return document


class Editor:
    """Редактор: хранит документы (CRUD для документов)."""

    def __init__(self, user: User) -> None:
        self.user = user
        self.documents: dict[str, Document] = {}

    def create_document(self, title: str) -> Document:
        """Create: создаёт новый документ."""
        document = Document(title, self.user)
        self.documents[document.title] = document
        return document

    def get_document(self, title: str) -> Document:
        """Read: возвращает документ по названию."""
        if title not in self.documents:
            raise DocumentNotFoundError(f"Документ «{title}» не найден")
        return self.documents[title]

    def rename_document(self, old_title: str, new_title: str) -> None:
        """Update: переименовывает документ."""
        document = self.get_document(old_title)
        if not new_title.strip():
            raise EmptyTitleError("Название документа не может быть пустым")
        del self.documents[old_title]
        document.title = new_title.strip()
        self.documents[document.title] = document

    def delete_document(self, title: str) -> None:
        """Delete: удаляет документ."""
        self.get_document(title)
        del self.documents[title]

    def list_titles(self) -> list[str]:
        return sorted(self.documents)
