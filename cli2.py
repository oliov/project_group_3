from search_by_criteria import AddressBook, Record

def main():
    book = AddressBook()

#тестові контакти
    book.add_record(Record ("Майко Анатолій", "567785", "maiko@gmail.com", "Ізюм", "13.07.1997"))
    book.add_record(Record ("Михайлюк Діана", "93765", "di@gmail.com", "Вишневе", "05.02.2003"))
    book.add_record(Record ("Коляда Сергій", "55555", "kolyada.s.i@gmail.com", "Краматорськ", "25.12.1991"))

    while True: 
        command = input("\n Введіть команду(add/search/delete/edit-email/edit-address/birthdays/exit):").strip().lower()

        if command == "exit":
            print("Завершення роботи…")
            break

        elif command == "add":
            name = input("Імʼя:")
            phone = input("Телефон:")
            email = input("Email:")
            address = input("Адреса:")
            birthday = input("День народження (DD.MM.YYYY):")
            book.add_record(Record(name, phone, email, address, birthday))
            print("Запис створено")

        elif command == "search":
            query = input("Введіть текст для пошуку:")
            book.search(query)

        elif command == "delete":
            name = input("Введіть імʼя для видалення:")
            book.delete(name)

        elif command == "edit-email":
            name = input("Введіть імʼя контакту:")
            new_email = input("Новий email:")
            book.edit_email(name, new_email)

        elif command == "edit-address":
            name = input("Введіть імʼя контакту:")
            new_address = input("Нова адреса:")
            book.edit_address(name, new_address)

        elif command.startswith("birthdays"):
            parts = command.split()
            #якщо користувач вказав кількість днів
            if len(parts) > 1 and parts[1].isdigit():
                days = int(parts[1])
            else:
                days = 7 #за замовчуванням
            book.get_upcoming_birthdays(days)

        else:
            print("Невідома команда")

if __name__ == "__main__":
    main()