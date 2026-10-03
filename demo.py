"""Демонстрация исключений и записи/чтения файлов JSON и XML."""

from exceptions import EditorError
from models import Editor, Font, Heading, Paragraph, User
from storage import JsonStorage, XmlStorage


def demo_exceptions() -> None:
    editor = Editor(User("Анна", "anna@mail.ru"))
    print("--- Обработка исключений ---")
    try:
        editor.create_document("   ")           # пустое название
    except EditorError as exc:
        print(f"[{type(exc).__name__}] {exc}")
    try:
        Font("Arial", 500)                       # плохой размер шрифта
    except EditorError as exc:
        print(f"[{type(exc).__name__}] {exc}")
    try:
        editor.get_document("Нет такого")        # документа нет
    except EditorError as exc:
        print(f"[{type(exc).__name__}] {exc}")
    try:
        doc = editor.create_document("Заметки")
        doc.update_element(3, "текст")           # элемента нет
    except EditorError as exc:
        print(f"[{type(exc).__name__}] {exc}")
    try:
        JsonStorage().load("no_file.json")       # файла нет
    except EditorError as exc:
        print(f"[{type(exc).__name__}] {exc}")
    try:
        User("", "a@mail.ru")                    # встроенное ValueError
    except ValueError as exc:
        print(f"[ValueError] {exc}")
    try:
        print(10 / 0)                            # встроенное исключение
    except ZeroDivisionError as exc:
        print(f"[ZeroDivisionError] {exc}")
    finally:
        print("[finally] выполняется всегда")


def demo_files() -> None:
    editor = Editor(User("Анна", "anna@mail.ru"))
    doc = editor.create_document("Конспект по Python")
    doc.add_element(Heading("Классы и объекты", 1, Font("Arial", 18, True)))
    doc.add_element(Paragraph("ООП опирается на классы и объекты."))
    doc.add_element(Paragraph("Исключения обрабатываются через try/except."))
    doc.add_comment(editor.user, "Добавить пример кода", 1)
    docs = list(editor.documents.values())
    JsonStorage().save(docs, "data/documents.json")
    XmlStorage().save(docs, "data/documents.xml")
    print("\n--- Чтение из файлов ---")
    for storage, path in ((JsonStorage(), "data/documents.json"),
                          (XmlStorage(), "data/documents.xml")):
        for document in storage.load(path):
            print(f"{path}:")
            print(document.show())


if __name__ == "__main__":
    demo_exceptions()
    demo_files()
