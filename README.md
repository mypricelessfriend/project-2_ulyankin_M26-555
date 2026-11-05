# Primitive DB

Учебный проект: минимальная база данных с таблицами и интерактивным
игровым циклом. Метаданные таблиц хранятся в JSON-файле `db_meta.json`
рядом с местом запуска.

## Установка

Сборка и установка как изолированного CLI-инструмента:

```bash
uv build
uv tool install ./dist/primitive_db-0.3.0-py3-none-any.whl
```

Если `uv` предупредит, что директория с инструментами не добавлена в `PATH`:

```bash
uv tool update-shell
```

и перезапустите терминал.

На Windows вместо `./dist/...` PowerShell не раскрывает маски, поэтому
устанавливайте файл по имени:

```powershell
uv tool install .\dist\primitive_db-0.3.0-py3-none-any.whl --force
```

## Запуск

```bash
database
```

При старте выводится приветствие и подсказка по командам:

```
Первая попытка запустить проект!

***

***Процесс работы с таблицей***
Функции:
<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу
<command> list_tables - показать список всех таблиц
<command> drop_table <имя_таблицы> - удалить таблицу

Общие команды:
<command> exit - выход из программы
<command> help - справочная информация

Введите команду:
```

## Управление таблицами

Все операции выполняются в интерактивном цикле `database`. Команды и их
аргументы разбираются через `shlex.split`, поэтому имена с пробелами
можно брать в кавычки.

| Команда | Описание |
|---|---|
| `create_table <имя_таблицы> <столбец1:тип> [<столбец2:тип> ...]` | Создать таблицу с указанными столбцами. Столбец `ID:int` добавляется автоматически в начало. |
| `list_tables` | Показать список всех таблиц и их столбцов. |
| `drop_table <имя_таблицы>` | Удалить таблицу. |
| `help` | Показать справку. |
| `exit` | Выйти из программы. |

**Допустимые типы столбцов:** `int`, `str`, `bool`. Любой другой тип
приводит к ошибке, таблица не создаётся.

**Проверки при `create_table`:**

- имя таблицы должно быть уникальным;
- формат каждого столбца — `имя:тип`;
- тип столбца должен быть из списка `int | str | bool`;
- имена столбцов не должны повторяться;
- столбец `ID` указывать вручную нельзя — он добавляется автоматически.

**Хранение метаданных.** Информация о таблицах сохраняется в
`db_meta.json` в текущей директории. Файл перечитывается в начале каждой
итерации цикла и перезаписывается после успешных `create_table` и
`drop_table`. Удаление `db_meta.json` равносильно «пустой» базе.

## CRUD-операции

Данные каждой таблицы хранятся в `data/<имя_таблицы>.json`. Все команды выполняются в интерактивном цикле `database`.

| Команда | Описание |
|---|---|
| `insert into <таблица> values (<v1>, <v2>, ...)` | Добавить запись. `ID` генерируется автоматически. |
| `select from <таблица>` | Показать все записи. |
| `select from <таблица> where <столбец> = <значение>` | Показать записи по условию. |
| `update <таблица> set <столбец> = <значение> where <столбец> = <значение>` | Обновить записи. |
| `delete from <таблица> where <столбец> = <значение>` | Удалить записи. |
| `info <таблица>` | Схема таблицы и количество записей. |

**Правила ввода значений:**

- Строки — **всегда в кавычках**: `"Sergei"` или `'Sergei'`.
- Числа — без кавычек: `28`.
- Логические — `true` / `false` (без кавычек).
- В `insert` указываются **все столбцы, кроме `ID`**.
- Все поля обязательны.

Пример:

```text
>>> Введите команду: create_table users name:str age:int is_active:bool
>>> Введите команду: insert into users values ("Sergei", 28, true)
>>> Введите команду: insert into users values ("Anna", 34, false)
>>> Введите команду: select from users
+----+--------+-----+-----------+
| ID |  name  | age | is_active |
+----+--------+-----+-----------+
| 1  | Sergei | 28  |    True   |
| 2  |  Anna  | 34  |   False   |
+----+--------+-----+-----------+
>>> Введите команду: update users set age = 29 where name = "Sergei"
>>> Введите команду: delete from users where ID = 2
>>> Введите команду: info users
Таблица: users
Столбцы: ID:int, name:str, age:int, is_active:bool
Количество записей: 1
```

### Пример использования

```text
Введите команду: create_table users name:str age:int active:bool
Таблица 'users' успешно создана.

Введите команду: list_tables
Список таблиц:
- users: ID:int, name:str, age:int, active:bool

Введите команду: create_table users name:str
Ошибка: таблица 'users' уже существует.

Введите команду: create_table bad name:float
Ошибка: недопустимый тип 'float' для столбца 'name'. Допустимые типы: int, str, bool.

Введите команду: create_table orders "user id:int" amount:int
Таблица 'orders' успешно создана.

Введите команду: list_tables
Список таблиц:
- users: ID:int, name:str, age:int, active:bool
- orders: ID:int, user id:int, amount:int

Введите команду: drop_table users
Таблица 'users' удалена.

Введите команду: list_tables
Список таблиц:
- orders: ID:int, user id:int, amount:int

Введите команду: exit
```

После этого `db_meta.json` выглядит так:

```json
{
  "orders": {
    "columns": [
      { "name": "ID", "type": "int" },
      { "name": "user id", "type": "int" },
      { "name": "amount", "type": "int" }
    ]
  }
}
```
## CRUD-операции

Данные каждой таблицы хранятся в `data/<имя_таблицы>.json`. Все команды выполняются в интерактивном цикле `database`.

| Команда | Описание |
|---|---|
| `insert into <таблица> values (<v1>, <v2>, ...)` | Добавить запись. `ID` генерируется автоматически. |
| `select from <таблица>` | Показать все записи. |
| `select from <таблица> where <столбец> = <значение>` | Показать записи по условию. |
| `update <таблица> set <столбец> = <значение> where <столбец> = <значение>` | Обновить записи. |
| `delete from <таблица> where <столбец> = <значение>` | Удалить записи. |
| `info <таблица>` | Схема таблицы и количество записей. |

**Правила ввода значений:**

- Строки — **всегда в кавычках**: `"Sergei"` или `'Sergei'`.
- Числа — без кавычек: `28`.
- Логические — `true` / `false` (без кавычек).
- В `insert` указываются **все столбцы, кроме `ID`**.
- Все поля обязательны.

Пример:

```text
>>> Введите команду: create_table users name:str age:int is_active:bool
>>> Введите команду: insert into users values ("Sergei", 28, true)
>>> Введите команду: insert into users values ("Anna", 34, false)
>>> Введите команду: select from users
+----+--------+-----+-----------+
| ID |  name  | age | is_active |
+----+--------+-----+-----------+
| 1  | Sergei | 28  |    True   |
| 2  |  Anna  | 34  |   False   |
+----+--------+-----+-----------+
>>> Введите команду: update users set age = 29 where name = "Sergei"
>>> Введите команду: delete from users where ID = 2
>>> Введите команду: info users
Таблица: users
Столбцы: ID:int, name:str, age:int, is_active:bool
Количество записей: 1
```

## Обработка ошибок и подтверждения

- Все операции с БД обёрнуты декоратором `handle_db_errors`: ошибки
  (`KeyError`, `ValueError`, `FileNotFoundError`) перехватываются
  централизованно и печатаются сообщением, программа не падает.
- Опасные операции (`drop_table`, `delete`) защищены декоратором
  `confirm_action`: перед выполнением запрашивается подтверждение
  `[y/n]`. Любой ответ, кроме `y`, отменяет операцию.
- Медленные операции (`insert`, `select`) обёрнуты декоратором
  `log_time`: после выполнения печатается
  `Функция <имя> выполнилась за X.XXX секунд.`
- Результаты `select` кэшируются в замыкании `create_cacher()`.
  Кэш сбрасывается после любых изменений (`insert`, `update`, `delete`,
  `create_table`, `drop_table`), поэтому данные всегда актуальны.

## Структура проекта

```text
project-2_ulyankin_-26-555/
├── pyproject.toml
├── README.md
├── .gitignore
└── src/
    └── primitive_db/
        ├── __init__.py
        ├── core.py     # create_table / list_tables / drop_table
        ├── engine.py   # welcome / print_help / run
        ├── utils.py    # load_metadata / save_metadata
        └── main.py     # точка входа (entry point database)
```

## Демонстрация

[![asciicast](https://asciinema.org/a/PQsqFyeT6ry15AyG.svg)] (https://asciinema.org/a/PQsqFyeT6ry15AyG)

[![asciicast](https://asciinema.org/a/Me2an1S9Z567BJCK.svg)](https://asciinema.org/a/Me2an1S9Z567BJCK)

[![asciicast](https://asciinema.org/a/YxGtBPN1MGIyqBF3.svg)](https://asciinema.org/a/YxGtBPN1MGIyqBF3)