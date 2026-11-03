import shlex

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata

DB_META_FILE = "db_meta.json"


def print_help() -> None:
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def welcome() -> None:
    print("Первая попытка запустить проект!")
    print()
    print("***")
    print_help()


def run() -> None:
    welcome()

    while True:
        metadata = load_metadata(DB_META_FILE)

        try:
            user_input = input("Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError as exc:
            print(f"Ошибка разбора команды: {exc}")
            continue

        if not args:
            continue

        command = args[0].lower()
        command_args = args[1:]

        if command == "exit":
            break
        elif command == "help":
            print_help()
        elif command == "create_table":
            if len(command_args) < 2:
                print("Использование: create_table <имя_таблицы> <столбец1:тип> ...")
                continue
            new_metadata = create_table(metadata, command_args[0], command_args[1:])
            save_metadata(DB_META_FILE, new_metadata)
        elif command == "list_tables":
            list_tables(metadata)
        elif command == "drop_table":
            if len(command_args) != 1:
                print("Использование: drop_table <имя_таблицы>")
                continue
            new_metadata = drop_table(metadata, command_args[0])
            save_metadata(DB_META_FILE, new_metadata)
        else:
            print(f"Неизвестная команда: '{command}'. Введите 'help' для справки.")