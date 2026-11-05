from primitive_db.decorators import confirm_action, handle_db_errors, log_time
from primitive_db.utils import load_table_data

VALID_TYPES = {"int", "str", "bool"}


def _check_type(value, type_name: str) -> bool:
    if type_name == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    if type_name == "str":
        return isinstance(value, str)
    if type_name == "bool":
        return isinstance(value, bool)
    return False


@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    if table_name in metadata:
        raise KeyError(f"таблица '{table_name}' уже существует")

    parsed = []
    seen = set()
    for col in columns:
        if ":" not in col:
            raise ValueError(f"неверный формат столбца '{col}'. Ожидается имя:тип")
        name, type_ = (p.strip() for p in col.split(":", 1))
        type_ = type_.lower()
        if not name:
            raise ValueError(f"пустое имя столбца в '{col}'")
        if name == "ID":
            raise ValueError("столбец ID добавляется автоматически")
        if type_ not in VALID_TYPES:
            raise ValueError(f"недопустимый тип '{type_}' для столбца '{name}'. Допустимые типы: int, str, bool")
        if name in seen:
            raise ValueError(f"дублирующееся имя столбца '{name}'")
        seen.add(name)
        parsed.append({"name": name, "type": type_})

    parsed.insert(0, {"name": "ID", "type": "int"})
    metadata[table_name] = {"columns": parsed}
    print(f"Таблица '{table_name}' успешно создана.")
    return metadata


def list_tables(metadata: dict) -> None:
    if not metadata:
        print("Нет созданных таблиц.")
        return
    print("Список таблиц:")
    for name, info in metadata.items():
        cols = ", ".join(f"{c['name']}:{c['type']}" for c in info["columns"])
        print(f"- {name}: {cols}")


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> dict:
    if table_name not in metadata:
        raise KeyError(f"таблица '{table_name}' не существует")
    del metadata[table_name]
    print(f"Таблица '{table_name}' удалена.")
    return metadata


@handle_db_errors
@log_time
def insert(metadata: dict, table_name: str, values: list) -> list:
    if table_name not in metadata:
        raise KeyError(f"таблица '{table_name}' не существует")
    columns = metadata[table_name]["columns"]
    expected = len(columns) - 1
    if len(values) != expected:
        raise ValueError(f"ожидалось {expected} значений, получено {len(values)}")
    for col, val in zip(columns[1:], values):
        if not _check_type(val, col["type"]):
            raise ValueError(f"значение '{val}' не соответствует типу '{col['type']}' столбца '{col['name']}'")

    data = load_table_data(table_name)
    new_id = max((row["ID"] for row in data), default=0) + 1
    record = {"ID": new_id}
    for col, val in zip(columns[1:], values):
        record[col["name"]] = val
    data.append(record)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return data


@handle_db_errors
@log_time
def select(table_name: str, where_clause: dict | None = None) -> list:
    data = load_table_data(table_name)
    if where_clause is None:
        return list(data)
    return [row for row in data if all(row.get(k) == v for k, v in where_clause.items())]


@handle_db_errors
def update(table_data: list, set_clause: dict, where_clause: dict):
    matched = [row for row in table_data if all(row.get(k) == v for k, v in where_clause.items())]
    if not matched:
        raise ValueError("ни одна запись не подходит под условие")
    updated_ids = []
    for row in matched:
        row.update(set_clause)
        updated_ids.append(row["ID"])
    return table_data, updated_ids


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data: list, where_clause: dict):
    deleted_ids = []
    remaining = []
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            deleted_ids.append(row["ID"])
        else:
            remaining.append(row)
    if not deleted_ids:
        raise ValueError("ни одна запись не подходит под условие")
    return remaining, deleted_ids


def info(metadata: dict, table_name: str) -> None:
    if table_name not in metadata:
        print(f"Ошибка: таблица '{table_name}' не существует.")
        return
    columns = metadata[table_name]["columns"]
    data = load_table_data(table_name)
    print(f"Таблица: {table_name}")
    print("Столбцы: " + ", ".join(f"{c['name']}:{c['type']}" for c in columns))
    print(f"Количество записей: {len(data)}")
