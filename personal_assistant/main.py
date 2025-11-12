from collections import UserDict
from datetime import datetime, timedelta
import pickle

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Not enough arguments."
        except Exception as e:
            return f"Error: {str(e)}"
    return inner

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone must be 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

    def to_date(self):
        day, month, year = map(int, self.value.split('.'))
        return datetime(year, month, day).date()

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Old phone not found.")

    def add_birthday(self, birthday_str):
        if self.birthday is not None:
            raise ValueError("Birthday already set.")
        self.birthday = Birthday(birthday_str)

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones) if self.phones else "none"
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value.lower()] = record 

    def find(self, name):
        return self.data.get(name.lower())

    def delete(self, name):
        key = name.lower()
        if key in self.data:
            del self.data[key]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []
        for record in self.data.values():
            if not record.birthday:
                continue
            bday = record.birthday.to_date()
            bday_this_year = bday.replace(year=today.year)
            if bday_this_year < today:
                bday_this_year = bday_this_year.replace(year=today.year + 1)
            delta = (bday_this_year - today).days
            if 0 <= delta <= 7:
                congrats_date = bday_this_year
                if congrats_date.weekday() >= 5:  # Сб или Нд → понедельник
                    days_to_monday = 7 - congrats_date.weekday()
                    congrats_date += timedelta(days=days_to_monday)
                upcoming.append({
                    "name": record.name.value,
                    "congratulation_date": congrats_date.strftime("%Y.%m.%d")
                })
        return upcoming


def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        return "Enter name and at least one phone.\nExample: add <name> <phone1> [phone2]..."

    name = args[0]
    phones = args[1:]

    
    if name.isdigit() and len(name) == 50:
        return "Name cannot be a phone number. Use a real name."

    valid_phones = []
    for phone in phones:
        if phone.isdigit() and len(phone) == 10:
            valid_phones.append(phone)
        else:
            return f"Invalid phone '{phone}': must be 10 digits."

    if not valid_phones:
        return "No valid 10-digit phones provided."

    name_lower = name.lower()
    record = book.find(name_lower)

    if record is not None:
        message = f"Contact '{name}' already exists. Adding phone(s)..."
    else:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    added_phones = []
    for phone in valid_phones:
        if any(p.value == phone for p in record.phones):
            continue  
        record.add_phone(phone)
        added_phones.append(phone)

    if added_phones:
        return f"{message} Added: {', '.join(added_phones)}"
    return f"{message} No new phones added."


@input_error
def change_contact(args, book: AddressBook):
    if len(args) != 3:
        return "Usage: change <name> <old_phone> <new_phone>"
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return "Phone changed."


@input_error
def phone_contact(args, book: AddressBook):
    if len(args) != 1:
        return "Usage: phone <name>"
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    if not record.phones:
        return f"{record.name.value} has no phones."
    return f"{record.name.value}: {'; '.join(p.value for p in record.phones)}"


@input_error
def all_contacts(args, book: AddressBook):
    if not book:
        return "No contacts saved."
    sorted_records = sorted(book.data.values(), key=lambda r: r.name.value.lower())
    return "\n".join(str(r) for r in sorted_records)

@input_error
def add_birthday(args, book):
    if len(args) != 2:
        return "Usage: add-birthday <name> <DD.MM.YYYY>"
    name, birthday = args
    record = book.find(name)
    if not record:
        raise KeyError
    if record.birthday:
        return f"Birthday already set for {record.name.value}: {record.birthday.value}"
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    if len(args) != 1:
        return "Usage: show-birthday <name>"
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    if not record.birthday:
        return f"No birthday set for {record.name.value}."
    return f"{record.name.value}'s birthday: {record.birthday.value}"


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    lines = [f"{item['name']} — {item['congratulation_date']}" for item in upcoming]
    return "Upcoming birthdays:\n" + "\n".join(lines)

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Нова книга, якщо файл не існує

def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(phone_contact(args, book))

        elif command == "all":
            print(all_contacts(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()