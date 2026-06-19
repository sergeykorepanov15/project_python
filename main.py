"""
main.py — пользовательский интерфейс программы «Игра в слова».
"""

import os
import sys

from logic import (
    LinkedList,
    find_chain,
    read_words_from_file,
    write_chain_to_file,
)


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_header() -> None:
    print("=" * 35)
    print("        ИГРА В СЛОВА ")
    print("=" * 35)


def print_menu() -> None:
    print("\n--- ГЛАВНОЕ МЕНЮ ---")
    print("  1. Загрузить слова из файла")
    print("  2. Ввести слова вручную")
    print("  3. Найти цепочку слов")
    print("  4. Сохранить результат в файл")
    print("  5. Показать текущее состояние")
    print("  0. Выход")
    print()


def get_menu_choice() -> str:
    while True:
        choice = input("Выберите пункт меню: ").strip()
        if choice in {"0", "1", "2", "3", "4", "5"}:
            return choice
        print("  [!] Введите число от 0 до 5.")


def press_enter_to_continue() -> None:
    input("\nНажмите Enter, чтобы вернуться в меню...")


def validate_words(words: list[str]) -> tuple[bool, list[str]]:
    """Проверяет слова на допустимые символы и дубликаты."""
    allowed = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
    invalid = []
    for w in words:
        if not w:
            continue
        if not all(ch in allowed for ch in w):
            invalid.append(w)

    if invalid:
        return False, invalid

    if len(words) != len(set(words)):
        return False, ["Обнаружены дублирующиеся слова"]

    return True, []


def menu_load_from_file(state: dict) -> None:
    filepath = input("Введите путь к входному файлу: ").strip()
    if not filepath:
        print("  [!] Путь не может быть пустым.")
        press_enter_to_continue()
        return

    try:
        words = read_words_from_file(filepath)

        valid, errors = validate_words(words)
        if not valid:
            if "Обнаружены дублирующиеся слова" in errors:
                print("  [!] Обнаружены дублирующиеся слова.")
            else:
                print(f"  [!] Недопустимые символы: {', '.join(errors)}")
                print("      Допускаются только строчные буквы русского алфавита.")
            press_enter_to_continue()
            return

        state["words"] = words
        state.pop("chain", None)
        print(f"  [✓] Загружено слов: {len(words)}")
        print(f"  Слова: {' '.join(words)}")
    except FileNotFoundError:
        print(f"  [!] Файл не найден: {filepath}")
    except ValueError as e:
        print(f"  [!] Ошибка содержимого файла: {e}")
    except OSError as e:
        print(f"  [!] Ошибка при открытии файла: {e}")

    press_enter_to_continue()


def menu_input_manually(state: dict) -> None:
    print("Введите слова через пробел (строчными буквами русского алфавита):")
    raw = input("> ").strip()

    if not raw:
        print("  [!] Строка не может быть пустой.")
        press_enter_to_continue()
        return

    words = raw.split()

    valid, errors = validate_words(words)
    if not valid:
        if "Обнаружены дублирующиеся слова" in errors:
            print("  [!] Обнаружены дублирующиеся слова.")
        else:
            print(f"  [!] Недопустимые символы: {', '.join(errors)}")
            print("      Допускаются только строчные буквы русского алфавита.")
        press_enter_to_continue()
        return

    state["words"] = words
    state.pop("chain", None)
    print(f"  [✓] Принято слов: {len(words)}")

    press_enter_to_continue()


def menu_find_chain(state: dict) -> None:
    words = state.get("words")
    if not words:
        print("  [!] Сначала загрузите или введите слова.")
        press_enter_to_continue()
        return

    print("  Поиск цепочки...")
    chain = find_chain(words)
    state["chain"] = chain

    if chain is None:
        print("  Решения не существует.")
    else:
        print(f"  [✓] Цепочка найдена:\n  {' '.join(chain.to_list())}")

    press_enter_to_continue()


def menu_save_to_file(state: dict) -> None:
    chain = state.get("chain")
    words = state.get("words")

    if words is None:
        print("  [!] Нет данных для сохранения.")
        press_enter_to_continue()
        return

    if chain is None and "chain" not in state:
        print("  [!] Сначала выполните поиск цепочки (пункт 3).")
        press_enter_to_continue()
        return

    filepath = input("Введите путь к выходному файлу: ").strip()
    if not filepath:
        print("  [!] Путь не может быть пустым.")
        press_enter_to_continue()
        return

    try:
        write_chain_to_file(filepath, chain)
        print(f"  [✓] Результат сохранён в: {filepath}")
    except OSError as e:
        print(f"  [!] Ошибка при записи файла: {e}")

    press_enter_to_continue()


def menu_show_state(state: dict) -> None:
    words = state.get("words")
    chain = state.get("chain")

    print("\n--- ТЕКУЩЕЕ СОСТОЯНИЕ ---")

    if words is None:
        print("  Слова: не загружены.")
    else:
        print(f"  Слова ({len(words)} шт.): {' '.join(words)}")

    if "chain" not in state:
        print("  Цепочка: поиск ещё не выполнялся.")
    elif chain is None:
        print("  Цепочка: решения не существует.")
    else:
        print(f"  Цепочка: {' '.join(chain.to_list())}")

    press_enter_to_continue()


def main() -> None:
    state: dict[str, list[str] | LinkedList | None] = {}

    while True:
        clear_screen()
        print_header()
        print_menu()
        choice = get_menu_choice()

        if choice == "1":
            menu_load_from_file(state)
        elif choice == "2":
            menu_input_manually(state)
        elif choice == "3":
            menu_find_chain(state)
        elif choice == "4":
            menu_save_to_file(state)
        elif choice == "5":
            menu_show_state(state)
        elif choice == "0":
            print("\nДо свидания!")
            sys.exit(0)


if __name__ == "__main__":
    main()