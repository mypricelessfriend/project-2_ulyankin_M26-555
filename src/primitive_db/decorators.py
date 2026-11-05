import functools
import time


def handle_db_errors(func):
    """Централизованная обработка ошибок операций с БД."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: файл данных не найден. Возможно, база данных не инициализирована.")
        except KeyError as e:
            print(f"Ошибка: не найдено: {e}.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
        return None

    return wrapper


def confirm_action(action_name):
    """Фабрика декораторов: запрашивает подтверждение перед опасной операцией."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                answer = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
            except (EOFError, KeyboardInterrupt):
                print()
                print("Операция отменена.")
                return None
            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Замеряет время выполнения функции и печатает его."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - start
            print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")

    return wrapper


def create_cacher():
    """Возвращает cache_result(key, value_func) с кэшем в замыкании."""
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        result = value_func()
        # не кэшируем None (например, если функция вернула ошибку через декоратор)
        if result is not None:
            cache[key] = result
        return result

    def clear():
        cache.clear()

    cache_result.clear = clear
    return cache_result
