import json
import os

DB_META_FILE = "db_meta.json"
DATA_DIR = "data"


def load_metadata(filepath: str) -> dict:
    """Загружает метаданные из JSON-файла. Если файла нет — пустой словарь."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _table_path(table_name: str) -> str:
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name: str) -> list:
    """Загружает данные таблицы из data/<table_name>.json. Нет файла — пустой список."""
    try:
        with open(_table_path(table_name), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list) -> None:
    """Сохраняет данные таблицы в data/<table_name>.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(_table_path(table_name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def delete_table_data(table_name: str) -> None:
    """Удаляет файл данных таблицы, если он существует."""
    try:
        os.remove(_table_path(table_name))
    except FileNotFoundError:
        pass
