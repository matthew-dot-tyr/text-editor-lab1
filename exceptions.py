"""Собственные исключения для программы «Текстовый редактор»."""


class EditorError(Exception):
    """Базовое исключение редактора."""


class EmptyTitleError(EditorError):
    """Название документа не может быть пустым."""


class InvalidIndexError(EditorError):
    """Элемента с таким номером нет в документе."""


class InvalidFontSizeError(EditorError):
    """Размер шрифта вне допустимых границ."""


class DocumentNotFoundError(EditorError):
    """Документ не найден."""


class StorageError(EditorError):
    """Ошибка при чтении или записи файла."""
