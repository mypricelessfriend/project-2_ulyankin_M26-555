import re

from prettytable import PrettyTable

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.decorators import create_cacher
from primitive_db.utils import (
    DB_META_FILE,
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

_cache = create_cacher()

INSERT_RE = re.compile(r"^insert\s+into\s+(\S+)\s+values\s*\((.+)\)\s*$", re.IGNORECASE | re.DOTALL)
SELECT_ALL_RE = re.compile(r"^select\s+from\s+(\S+)\s*$", re.IGNORECASE)
SELECT_WHERE_RE = re.compile(r"^select\s+from\s+(\S+)\s+where\s+(.+)$", re.IGNORECASE | re.DOTALL)
UPDATE_RE = re.compile(r"^update\s+(\S+)\s+set\s+(.+?)\s+where\s+(.+)$", re.IGNORECASE | re.DOTALL)
DELETE_RE = re.compile(r"^delete\s+from\s+(\S+)\s+where\s+(.+)$", re.IGNORECASE | re.DOTALL)
INFO_RE = re.compile(r"^info\s+(\S+)\s*$", re.IGNORECASE)
CREATE_RE = re.compile(r"^create_table\s+(\S+)\s+(.+)$", re.IGNORECASE)
DROP_RE = re.compile(r"^drop_table\s+(\S+)\s*$", re.IGNORECASE)


def print_help() -> None:
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.")
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.")
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def welcome() -> None:
    print_help()


def parse_value(raw: str):
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ('"', "'"):
        return raw[1:-1]
    low = raw.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        pass
    raise ValueError(f"не удалось распознать значение: {raw}")


def split_values(s: str) -> list:
    values, current = [], []
    in_quote = None
    escape = False
    for ch in s:
        if escape:
            current.append(ch)
            escape = False
            continue
        if in_quote:
            current.append(ch)
            if ch == in_quote:
                in_quote = None
        elif ch in ('"', "'"):
            in_quote = ch
            current.append(ch)
        elif ch == ",":
            values.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current or s.strip():
        values.append("".join(current).strip())
    return [parse_value(v) for v in values if v != ""]


def parse_condition(s: str) -> tuple[str, object]:
    m = re.match(r"^\s*(\S+)\s*=\s*(.+?)\s*$", s, re.DOTALL)
    if not m:
        raise ValueError(f"не удалось разобрать условие: {s}")
    return m.group(1), parse_value(m.group(2))


def _print_rows(rows: list, columns: list) -> None:
    table = PrettyTable()
    table.field_names = [c["name"] for c in columns]
    for row in rows:
        table.add_row([row.get(c["name"], "") for c in columns])
    print(table)


def _handle_create_table(metadata: dict, user_input: str) -> None:
    m = CREATE_RE.match(user_input)
    if not m:
        print("Использование: create_table <имя_таблицы> <столбец1:тип> ...")
        return
    new_metadata = create_table(metadata, m.group(1), m.group(2).split())
    if new_metadata is not None:
        save_metadata(DB_META_FILE, new_metadata)
        _cache.clear()


def _handle_drop_table(metadata: dict, user_input: str) -> None:
    m = DROP_RE.match(user_input)
    if not m:
        print("Использование: drop_table <имя_таблицы>")
        return
    name = m.group(1)
    new_metadata = drop_table(metadata, name)
    if new_metadata is not None and name not in new_metadata:
        save_metadata(DB_META_FILE, new_metadata)
        delete_table_data(name)
        _cache.clear()


def _handle_insert(metadata: dict, user_input: str) -> None:
    m = INSERT_RE.match(user_input)
    if not m:
        print("Использование: insert into <имя_таблицы> values (<значение1>, <значение2>, ...)")
        return
    table_name = m.group(1)
    try:
        values = split_values(m.group(2))
    except ValueError as exc:
        print(f"Ошибка: {exc}")
        return
    new_data = insert(metadata, table_name, values)
    if new_data is not None:
        save_table_data(table_name, new_data)
        _cache.clear()


def _handle_select(metadata: dict, user_input: str) -> None:
    where = None
    m = SELECT_WHERE_RE.match(user_input)
    if m:
        table_name = m.group(1)
        try:
            col, val = parse_condition(m.group(2))
        except ValueError as exc:
            print(f"Ошибка: {exc}")
            return
        where = {col: val}
    else:
        m = SELECT_ALL_RE.match(user_input)
        if not m:
            print("Использование: select from <имя_таблицы> [where <столбец> = <значение>]")
            return
        table_name = m.group(1)

    if table_name not in metadata:
        print(f"Ошибка: таблица '{table_name}' не существует.")
        return

    key = (table_name, tuple(sorted(where.items())) if where else None)
    rows = _cache(key, lambda: select(table_name, where))
    if rows is None:
        return
    _print_rows(rows, metadata[table_name]["columns"])


def _handle_update(metadata: dict, user_input: str) -> None:
    m = UPDATE_RE.match(user_input)
    if not m:
        print("Использование: update <имя_таблицы> set <столбец> = <значение> where <столбец> = <значение>")
        return
    table_name = m.group(1)
    if table_name not in metadata:
        print(f"Ошибка: таблица '{table_name}' не существует.")
        return
    try:
        set_col, set_val = parse_condition(m.group(2))
        where_col, where_val = parse_condition(m.group(3))
    except ValueError as exc:
        print(f"Ошибка: {exc}")
        return

    data = load_table_data(table_name)
    result = update(data, {set_col: set_val}, {where_col: where_val})
    if result is None:
        return
    new_data, updated_ids = result
    save_table_data(table_name, new_data)
    _cache.clear()
    for rid in updated_ids:
        print(f'Запись с ID={rid} в таблице "{table_name}" успешно обновлена.')


def _handle_delete(metadata: dict, user_input: str) -> None:
    m = DELETE_RE.match(user_input)
    if not m:
        print("Использование: delete from <имя_таблицы> where <столбец> = <значение>")
        return
    table_name = m.group(1)
    if table_name not in metadata:
        print(f"Ошибка: таблица '{table_name}' не существует.")
        return
    try:
        where_col, where_val = parse_condition(m.group(2))
    except ValueError as exc:
        print(f"Ошибка: {exc}")
        return

    data = load_table_data(table_name)
    result = delete(data, {where_col: where_val})
    if result is None:
        return
    new_data, deleted_ids = result
    save_table_data(table_name, new_data)
    _cache.clear()
    for rid in deleted_ids:
        print(f'Запись с ID={rid} успешно удалена из таблицы "{table_name}".')


def _handle_info(metadata: dict, user_input: str) -> None:
    m = INFO_RE.match(user_input)
    if not m:
        print("Использование: info <имя_таблицы>")
        return
    info(metadata, m.group(1))


def _handle_command(metadata: dict, user_input: str) -> None:
    command = user_input.split(maxsplit=1)[0].lower()
    if command == "exit":
        raise SystemExit
    if command == "help":
        print_help()
    elif command == "create_table":
        _handle_create_table(metadata, user_input)
    elif command == "list_tables":
        list_tables(metadata)
    elif command == "drop_table":
        _handle_drop_table(metadata, user_input)
    elif command == "insert":
        _handle_insert(metadata, user_input)
    elif command == "select":
        _handle_select(metadata, user_input)
    elif command == "update":
        _handle_update(metadata, user_input)
    elif command == "delete":
        _handle_delete(metadata, user_input)
    elif command == "info":
        _handle_info(metadata, user_input)
    else:
        print(f"Неизвестная команда: '{command}'. Введите 'help' для справки.")


def run() -> None:
    welcome()
    while True:
        metadata = load_metadata(DB_META_FILE)
        try:
            user_input = input(">>> Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input:
            continue
        try:
            _handle_command(metadata, user_input)
        except SystemExit:
            break
        except Exception as exc:
            print(f"Ошибка: {exc}")
