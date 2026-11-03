HELP_TEXT = """<command> exit - выйти из программы
<command> help - справочная информация"""


def welcome() -> None:
    print("Первая попытка запустить проект!")
    print()
    print("***")
    print(HELP_TEXT)

    while True:
        try:
            command = input("Введите команду: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if command == "exit":
            break
        elif command == "help":
            print()
            print(HELP_TEXT)
        