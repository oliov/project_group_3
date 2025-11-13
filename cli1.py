from search_by_criteria import AddressBook, Record

def main():
    book = AddressBook()

    #тестові записи
    book.add_record(Record("Майко Анатолій", "567785", "maiko@gmail.com"))
    book.add_record(Record("Михайлюк Діана", "93765", "di@gmail.com"))
    book.add_record(Record("Коляда Сергій", "55555", "kolyada.s.i@gmail.com"))

    while True:
        command = input("\n Ведіть команду(add/search/exit):").strip().lower()

        if command == "exit":
            print("Завершення роботи…")
            break

        elif command == "add":
            name = input("Імʼя:")
            phone = input("Телефон:")
            email = input("Email:")
            book.add_record(Record(name, phone, email))
            print("Запис додано")

        elif command == "search":
            query = input("Введіть текст для пошуку:")
            book.search(query)

        else:
            print("Невідома команда")

if __name__ == "__main__":
    main()