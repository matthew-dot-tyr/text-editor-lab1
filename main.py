"""Лабораторная работа № 1, вариант 16: текстовый редактор (меню)."""

from typing import Optional

from exceptions import EditorError
from models import Document, Editor, Heading, Paragraph, User
from storage import JsonStorage, Storage, XmlStorage

MENU = """
===== Текстовый редактор =====
1. Создать документ         9. Найти текст
2. Открыть документ        10. Заменить текст
3. Список документов       11. Добавить комментарий
4. Переименовать документ  12. Сохранить в файл
5. Удалить документ        13. Загрузить из файла
6. Добавить абзац          14. Показать документ
7. Добавить заголовок       0. Выход
8. Изменить элемент (пустой текст = удалить элемент)"""


class ConsoleMenu:
    """Консольное меню. Ошибки выводятся, программа не завершается."""

    def __init__(self, editor: Editor) -> None:
        self.editor = editor
        self.current: Optional[Document] = None  # открытый документ

    def _document(self) -> Document:
        if self.current is None:
            raise EditorError("Сначала создайте или откройте документ")
        return self.current

    @staticmethod
    def _storage(path: str) -> Storage:
        return XmlStorage() if path.endswith(".xml") else JsonStorage()

    def run(self) -> None:
        while True:
            print(MENU)
            try:
                choice = input("Выберите пункт: ").strip()
                if choice == "0":
                    print("До свидания!")
                    break
                self.handle(choice)
            except EditorError as exc:  # собственные исключения
                print(f"Ошибка: {exc}")
            except ValueError as exc:  # например, ввели не число
                print(f"Неверный ввод: {exc}")
            except (EOFError, KeyboardInterrupt):
                print("\nВвод прерван")
                break

    def handle(self, choice: str) -> None:
        if choice == "1":
            self.current = self.editor.create_document(input("Название: "))
        elif choice == "2":
            self.current = self.editor.get_document(input("Название: "))
        elif choice == "3":
            print("\n".join(self.editor.list_titles()) or "(пусто)")
        elif choice == "4":
            self.editor.rename_document(input("Старое название: "),
                                        input("Новое название: "))
        elif choice == "5":
            self.editor.delete_document(input("Название: "))
            self.current = None
        elif choice == "6":
            self._document().add_element(Paragraph(input("Текст: ")))
        elif choice == "7":
            text = input("Текст: ")
            level = int(input("Уровень (1-3): "))
            self._document().add_element(Heading(text, level))
        elif choice == "8":
            index = int(input("Номер элемента: ")) - 1
            text = input("Новый текст: ")
            if text:
                self._document().update_element(index, text)
            else:
                self._document().delete_element(index)
        elif choice == "9":
            print(self._document().find(input("Что искать: ")) or "Не найдено")
        elif choice == "10":
            count = self._document().replace_all(input("Что заменить: "),
                                                 input("Чем заменить: "))
            print(f"Замен: {count}")
        elif choice == "11":
            index = int(input("Номер элемента: ")) - 1
            self._document().add_comment(self.editor.user,
                                         input("Комментарий: "), index)
        elif choice == "12":
            path = input("Файл (.json или .xml): ")
            self._storage(path).save(list(self.editor.documents.values()),
                                     path)
            print("Сохранено")
        elif choice == "13":
            path = input("Файл (.json или .xml): ")
            for document in self._storage(path).load(path):
                self.editor.documents[document.title] = document
            self.current = None
            print("Загружено")
        elif choice == "14":
            print(self._document().show())
        else:
            print("Нет такого пункта")


if __name__ == "__main__":
    ConsoleMenu(Editor(User("Матвей", "kuftin.m@list.ru"))).run()
