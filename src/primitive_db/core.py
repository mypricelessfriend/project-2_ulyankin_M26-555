VALID_TYPES = {"int", "str", "bool"}


def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    """Создаёт таблицу. Автоматически добавляет ID:int в начало."""
    if table_name in metadata:
        print(f"Ошибка: таблица '{table_name}' уже существует.")
        return metadata

    parsed = []
    for col in columns:
        if ":" not in col:
            print(f"Ошибка: неверный формат столбца '{col}'. Ожидается имя:тип.")
            return metadata
        name, type_ = (part.strip() for part in col.split(":", 1))
        type_ = type_.lower()
        if not name:
            print(f"Ошибка: пустое имя столбца в '{col}'.")
            return metadata
        if name == "ID":
            print("Ошибка: столбец ID добавляется автоматически.")
            return metadata
        if type_ not in VALID_TYPES:
            print(
                f"Ошибка: недопустимый тип '{type_}' для столбца '{name}'. "
                f"Допустимые типы: int, str, bool."
            )
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
    """Печатает список всех таблиц и их столбцов."""
    if not metadata:
        print("Нет созданных таблиц.")
        return
    print("Список таблиц:")
    for name, info in metadata.items():
        cols = ", ".join(f"{c['name']}:{c['type']}" for c in info["columns"])
        print(f"- {name}: {cols}")


def drop_table(metadata: dict, table_name: str) -> dict:
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        print(f"Ошибка: таблица '{table_name}' не существует.")
        return metadata
    del metadata[table_name]
    print(f"Таблица '{table_name}' удалена.")
    return metadata