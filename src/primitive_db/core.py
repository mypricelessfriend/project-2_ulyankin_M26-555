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


def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    if table_name in metadata:
        print(f"Ошибка: таблица '{table_name}' уже существует.")
        return metadata

    parsed = []
    for col in columns:
        if ":" not in col:
            print(f"Ошибка: неверный формат столбца '{col}'. Ожидается имя:тип.")
            return metadata
        name, type_ = (p.strip() for p in col.split(":", 1))
        type_ = type_.lower()
        if not name:
            print(f"Ошибка: пустое имя столбца в '{col}'.")
            return metadata
        if name == "ID":
            print("Ошибка: столбец ID добавляется автоматически.")
            return metadata
        if type_ not in VALID_TYPES:
            print(f"Ошибка: недопустимый тип '{type_}' для столбца '{name}'. Допустимые: int, str, bool.")
            return metadata
        parsed.append({"name": name, "type": type_})

    names = [c["name"] for c in parsed]
    if len(names) != len(set(names)):
        print("Ошибка: есть дублирующиеся имена столбцов.")
        return metadata

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


def drop_table(metadata: dict, table_name: str) -> dict:
    if table_name not in metadata:
        print(f"Ошибка: таблица '{table_name}' не существует.")
        return metadata
    del metadata[table_name]
    print(f"Таблица '{table_name}' удалена.")
    return metadata


def insert(metadata: dict, table_name: str, values: list):
    """Добавляет запись. Возвращает обновлённый список данных или None при ошибке."""
    if table_name not in metadata:
        print(f"Ошибка: таблица '{table_name}' не существует.")
        return None
    columns = metadata[table_name]["columns"]
    expected = len(columns) - 1  # минус ID
    if len(values) != expected:
        print(f"Ошибка: ожидалось {expected} значений, получено {len(values)}.")
        return None

    for col, val in zip(columns[1:], values):
        if not _check_type(val, col["type"]):
            print(f"Ошибка: значение '{val}' не соответствует типу '{col['type']}' столбца '{col['name']}'.")
            return None

    data = load_table_data(table_name)
    new_id = max((row["ID"] for row in data), default=0) + 1
    record = {"ID": new_id}
    for col, val in zip(columns[1:], values):
        record[col["name"]] = val
    data.append(record)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return data


def select(table_data: list, where_clause: dict | None = None) -> list:
    if where_clause is None:
        return list(table_data)
    return [row for row in table_data if all(row.get(k) == v for k, v in where_clause.items())]


def update(table_data: list, set_clause: dict, where_clause: dict):
    """Обновляет записи. Возвращает (data, список обновлённых ID)."""
    updated_ids = []
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            row.update(set_clause)
            updated_ids.append(row["ID"])
    return table_data, updated_ids


def delete(table_data: list, where_clause: dict):
    """Удаляет записи. Возвращает (оставшиеся данные, список удалённых ID)."""
    deleted_ids = []
    remaining = []
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            deleted_ids.append(row["ID"])
        else:
            remaining.append(row)
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