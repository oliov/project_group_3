from collections import UserDict
from datetime import datetime, timedelta
import pickle
import re

from colorama import init, Fore, Style


# ІНІЦІАЛІЗАЦІЯ COLORAMA (ОБОВ'ЯЗКОВО!)
init(autoreset=True)

# КОЛЬОРОВІ КОНСТАНТИ
C_SUCCESS = Fore.GREEN
C_ERROR = Fore.RED
C_WARNING = Fore.YELLOW
C_INFO = Fore.CYAN
C_BRIGHT = Style.BRIGHT
C_RESET = Style.RESET_ALL


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

    def __repr__(self):
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


class Address(Field):
    def __init__(self, value):
        if not value.strip():
            raise ValueError("Address cannot be empty.")
        super().__init__(value.strip())


class Email(Field):
    regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    def __init__(self, value):
        if not value.strip():
            raise ValueError("Email cannot be empty.")
        if not self.regex.match(value.strip()):
            raise ValueError("Invalid email format.")
        super().__init__(value.strip().lower())


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.address = None        # Нове поле
        self.emails = []           # Нове поле (можна кілька)

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

    # Нові методи
    def add_address(self, address_str):
        if self.address is not None:
            raise ValueError("Address already set.")
        self.address = Address(address_str)

    def add_email(self, email_str):
        email = Email(email_str)
        if email in self.emails:
            raise ValueError(f"Email {email.value} already exists.")
        self.emails.append(email)

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones) \
            if self.phones else "none"
        birthday_str = f", birthday: {self.birthday.value}" \
            if self.birthday else ""
        address_str = f", address: {self.address.value}" \
            if self.address else ""
        emails_str = f", emails: {'; '.join(e.value for e in self.emails)}" \
            if self.emails else ""
        return f"Contact name: {self.name.value} \
            , phones: {phones_str}{birthday_str}{address_str}{emails_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value.lower()] = record

    def find(self, name):
        return self.data.get(name.lower())

    def delete(self, name):
        key = name.lower()
        if key in self.data:
            del self.data[key]

    def get_upcoming_birthdays(self, period=7):
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
            if 0 <= delta <= period:
                congrats_date = bday_this_year
                if congrats_date.weekday() >= 5:  # субота або неділя
                    days_to_monday = 7 - congrats_date.weekday()
                    congrats_date += timedelta(days=days_to_monday)
                upcoming.append({
                    "name": record.name.value,
                    "congratulation_date": congrats_date.strftime("%d.%m.%Y")
                })
        return upcoming

    def search(self, query):
        query_lower = query.lower()
        results = []
        for record in self.data.values():
            if query_lower in record.name.value.lower():
                results.append(record)
                continue
            for phone in record.phones:
                if query_lower in phone.value:
                    results.append(record)
                    break
            if record.address and query_lower in record.address.value.lower():
                results.append(record)
            if record.emails and query_lower in record.emails:
                results.append(record)
            if record.birthday and query_lower in record.birthday.value:
                results.append(record)
        return results

    def edit_email(self, *args):
        try:
            name, old_email, new_email = args[0]
            for i, email in enumerate(self.data[name].emails):
                if str(email) == old_email:
                    self.data[name].emails[i] = Email(new_email)
                    break
            return f"Email для '{name}' оновлено"
        except ValueError:
            return 'edit-email <old> <new>'
        except KeyError:
            return "Контакт не знайдено"

    # Редагування адреси
    def edit_address(self, *args):
        try:
            name, *new_address = args[0]
            new_address = ' '.join(new_address)
            self.data[name].address = Address(new_address)
            return f"Адресу для '{name}' оновлено"
        except ValueError:
            return "edit-address <name> <new address>"
        except KeyError:
            return "Контакт не знайдено"


# >>> START OF NOTES MODULE =========================================

class Note:
    def __init__(self, title, content):
        self.title = title.strip()
        self.content = content.strip()
        self.tags = []
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_tag(self, tag):
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False

    def __str__(self):
        tags_str = f", tags: #{', #'.join(self.tags)}" if self.tags else ""
        return f"[{self.title}] {self.content} \
            (created {self.created_at}){tags_str}"


class NotesBook(UserDict):
    def __init__(self):
        super().__init__()
        self.next_id = 1

    def add_note(self, title, content):
        note = Note(title.strip(), content.strip())
        key = str(self.next_id)
        self.data[key] = note
        self.next_id += 1
        return key

    def edit_note(self, key, new_content):
        if key in self.data:
            self.data[key].content = new_content.strip()
        else:
            raise KeyError("Note not found.")

    def delete_note(self, key):
        if key in self.data:
            del self.data[key]
        else:
            raise KeyError("Note not found.")

    def all_notes(self):
        return [(key, note) for key, note in sorted(self.data.items())]

    def search(self, query):
        query_lower = query.lower()
        results = []
        for key, note in self.data.items():
            title_matches = note.title.lower().count(query_lower)
            content_matches = note.content.lower().count(query_lower)
            tags_matches = sum(1 for tag in note.tags if query_lower in tag)

            total_matches = title_matches + content_matches + tags_matches
            if total_matches > 0:
                results.append((total_matches, key, note))

        results.sort(reverse=True, key=lambda x: x[0])
        return [(key, note) for _, key, note in results]

    def search_by_tags(self, tags):
        tags = {t.strip().lower() for t in tags}
        results = []
        for key, note in self.data.items():
            note_tags = {t.lower() for t in note.tags}
            matches = len(note_tags.intersection(tags))
            if matches > 0:
                results.append((matches, key, note))
        results.sort(reverse=True)  # за кількістю збігів тегів
        return [(key, note) for _, key, note in results]


def save_notes(notes, filename="notes.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(notes, f)


def load_notes(filename="notes.pkl"):
    try:
        with open(filename, "rb") as f:
            notes = pickle.load(f)
        if notes.data:
            notes.next_id = max(map(int, notes.data.keys())) + 1
        else:
            notes.next_id = 1
        return notes
    except FileNotFoundError:
        return NotesBook()


@input_error
def delete_contact(args, book):
    if len(args) != 1:
        return f"{C_ERROR}Використання: delete <ім'я>{C_RESET}"
    name = args[0]
    if book.find(name.lower()):
        book.delete(name.lower())
        return f"{C_SUCCESS}Контакт видалено.{C_RESET}"
    raise KeyError


# ==================== CLI Commands ====================

def add_note(args, notes):
    if len(args) < 2:
        return "Usage: add-note <title> <content>"
    title = args[0]
    content = ' '.join(args[1:])
    key = notes.add_note(title, content)
    return f"Note '{title}' added with id {key}."


def show_note(args, notes):
    if len(args) != 1:
        return "Usage: show-note <id>"
    key = args[0]
    if key in notes.data:
        return f"{key}: {notes.data[key]}"
    return "Note not found."


def all_notes_func(args, notes):
    result = notes.all_notes()
    if not result:
        return "No notes found."
    return "\n".join([f"{key}: {note}" for key, note in result])


def edit_note(args, notes):
    if len(args) < 2:
        return "Usage: edit-note <id> <new content>"
    key = args[0]
    new_content = ' '.join(args[1:])
    notes.edit_note(key, new_content)
    return "Note edited."


def delete_note(args, notes):
    if len(args) != 1:
        return "Usage: delete-note <id>"
    key = args[0]
    notes.delete_note(key)
    return "Note deleted."


def find_notes(args, notes):
    if not args:
        return "Usage: find-notes <text>"
    query = ' '.join(args)
    found = notes.search(query)
    if not found:
        return "No matches."
    return "\n".join([f"{key}: {note}" for key, note in found])


def add_tag(args, notes):
    if len(args) < 2:
        return "Usage: add-tag <id> <tag1> [tag2]..."
    key = args[0]
    tags = args[1:]
    if key not in notes.data:
        return "Note not found."
    for tag in tags:
        notes.data[key].add_tag(tag)
    return f"Tags added to note {key}: {', '.join(tags)}"


def find_by_tag(args, notes):
    if len(args) != 1:
        return "Usage: find-by-tag <tag>"
    results = notes.search_by_tags(args)
    if not results:
        return "No notes found with this tag."
    return "\n".join([f"{key}: {note}" for key, note in results])


def remove_tag(args, notes):
    if len(args) != 2:
        return "Usage: remove-tag <id> <tag>"
    key, tag_to_remove = args
    if key not in notes.data:
        return "Note not found."
    note = notes.data[key]
    if note.remove_tag(tag_to_remove):
        return f"Tag '#{tag_to_remove}' removed from note {key}."
    return f"Tag '#{tag_to_remove}' not found in note {key}."


def search_notes(args, notes):
    if not args:
        return "Usage: search-notes <query>"
    query = ' '.join(args)
    results = notes.search(query)
    if not results:
        return f"No results for: '{query}'"
    return "Search results:\n" + "\n".join(f"{k}: {n}" for k, n in results)


def filter_notes_by_tag(args, notes):
    if not args:
        return "Usage: filter-notes-by-tag <tag1> [tag2] ..."
    results = notes.search_by_tags(args)
    if not results:
        return f"No notes with tags: {', '.join('#' + t for t in args)}"
    return "Found by tags:\n" + "\n".join(f"{k}: {n}" for k, n in results)

# <<< END OF NOTES MODULE ===========================================


def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


@input_error  # Рішення: дозволити створювати контакт без телефону
def add_contact(args, book: AddressBook):
    if len(args) < 1:
        return "Enter at least a name.\n \
            Example: add <name> [phone1] [phone2]..."

    name = args[0]
    phones = args[1:]

    # Перевірка, щоб ім'я не виглядало як телефон
    if name.isdigit() and len(name) == 10:
        return "Name cannot be a 10-digit number. Use a real name."

    valid_phones = []
    for phone in phones:
        if phone.isdigit() and len(phone) == 10:
            valid_phones.append(phone)
        else:
            return f"Invalid phone '{phone}': must be exactly 10 digits."

    name_lower = name.lower()
    record = book.find(name_lower)

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    else:
        message = f"Contact '{name}' already exists."

    added_phones = []
    for phone in valid_phones:
        if any(p.value == phone for p in record.phones):
            continue
        record.add_phone(phone)
        added_phones.append(phone)

    if added_phones:
        return f"{message} Added phones: {', '.join(added_phones)}"
    else:
        return message + (" No new phones added." if valid_phones else "")


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
    sorted_records = sorted(
        book.data.values(), key=lambda r: r.name.value.lower()
    )
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
        return f"Birthday already set for {record.name.value}: \
            {record.birthday.value}"
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
    period = 7
    if args:
        try:
            period = int(args[0])
            if period < 0:
                raise ValueError
        except ValueError:
            return f"{C_ERROR}Невірна кількість днів.{C_RESET}"
    upcoming = book.get_upcoming_birthdays(period)
    if not upcoming:
        return f"{C_INFO}Немає днів народження \
            протягом наступних {period} днів.{C_RESET}"

    lines = [
                f"{C_BRIGHT}{item['name']}{C_RESET} \
                — {item['congratulation_date']}"
                for item in upcoming
            ]

    return f"{C_SUCCESS}Найближчі дні народження:\n" \
        + "\n".join(lines) + C_RESET


@input_error
def add_address(args, book):
    if len(args) < 2:
        return f"{C_ERROR}Usage: add-address <name> <address...>{C_RESET}"
    name = args[0]
    address = ' '.join(args[1:])
    record = book.find(name.lower())
    if not record:
        raise KeyError("Contact not found.")
    record.add_address(address)
    return f"{C_SUCCESS}Address added for '{name}'{C_RESET}"

@input_error
def add_email(args, book):
    if len(args) != 2:
        return "Usage: add-email <name> <email>"
    name, email = args
    record = book.find(name)
    if not record:
        raise KeyError("Contact not found.")
    record.add_email(email)
    return "Email added."

@input_error
def edit_address(args, book):
    if len(args) < 2:
        return f"{C_ERROR}Usage: edit-address <name> <new address...>{C_RESET}"
    name, new_address = args[0], ' '.join(args[1:])
    record = book.find(name.lower())
    if not record:
        raise KeyError("Contact not found.")
    if record.address is None:
        return f"{C_ERROR}No address to edit. Use 'add-address' first.{C_RESET}"
    record.address = Address(new_address)
    return f"{C_SUCCESS}Address updated.{C_RESET}"


@input_error
def edit_email(args, book):
    if len(args) != 3:
        return f"{C_ERROR}Usage: edit-email <name> <old email> <new email>{C_RESET}"
    name, old_email, new_email = args
    record = book.find(name.lower())
    if not record:
        raise KeyError("Contact not found.")
    
    old_email = old_email.lower()
    for i, email in enumerate(record.emails):
        if email.value == old_email:
            record.emails[i] = Email(new_email)
            return f"{C_SUCCESS}Email updated: {old_email} → {new_email}{C_RESET}"
    
    return f"{C_ERROR}Email '{old_email}' not found.{C_RESET}"

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Нова книга, якщо файл не існує


@input_error
def search_contacts(args, book):
    if not args:
        return f"{C_ERROR}Використання: search <запит>{C_RESET}"
    query = ' '.join(args)
    results = book.search(query)
    if not results:
        return f"{C_WARNING}Збігів не знайдено.{C_RESET}"
    return "\n".join(str(r) for r in results)


# ==================== МЕНЮ ДОВІДКИ ====================
def show_help():
    help_text = f"""
{C_BRIGHT}{C_WARNING}=== ДОСТУПНІ КОМАНДИ ==={C_RESET}

{C_INFO}Контакти:{C_RESET}
  {C_BRIGHT}add <ім'я> <телефон1> [телефон2]...{C_RESET} \
— додати контакт або телефон
  {C_BRIGHT}change <ім'я> <старий> <новий>{C_RESET}      \
— змінити телефон
  {C_BRIGHT}phone <ім'я>{C_RESET}                        \
— показати телефони
  {C_BRIGHT}all{C_RESET}                                 \
— показати всі контакти
  {C_BRIGHT}delete <ім'я>{C_RESET}                       \
— видалити контакт
  {C_BRIGHT}search <текст>{C_RESET}                      \
— пошук за ім'ям, телефоном, адресою, email

{C_INFO}Дні народження:{C_RESET}
  {C_BRIGHT}add-birthday <ім'я> <ДД.ММ.РРРР>{C_RESET}    \
— додати день народження
  {C_BRIGHT}show-birthday <ім'я>{C_RESET}                \
— показати день народження
  {C_BRIGHT}birthdays [днів]{C_RESET}                    \
— найближчі дні народження (за замовчуванням 7)

{C_INFO}Додатково:{C_RESET}
  {C_BRIGHT}add-address <ім'я> <адреса>{C_RESET}         \
— додати адресу
  {C_BRIGHT}edit-address <ім'я> <нова адреса>{C_RESET}     — змінити адресу
  {C_BRIGHT}add-email <ім'я> <email>{C_RESET}            \
— додати email
  {C_BRIGHT}edit-email <ім'я> <старий> <новий>{C_RESET}  — змінити email
 
{C_INFO}Нотатки:{C_RESET}
  {C_BRIGHT}add-note <заголовок> <текст нотатки...>{C_RESET}  — створити нотатку
  {C_BRIGHT}search-notes <текст>{C_RESET}                \
— пошук за текстом
  {C_BRIGHT}edit-note <id> <новий текст>{C_RESET}        \
— редагувати нотатку
  {C_BRIGHT}delete-note <id>{C_RESET}                    \
— видалити нотатку
  {C_BRIGHT}all-notes{C_RESET}                           \
— показати всі нотатки
  {C_BRIGHT}add-tag <id> <тег1> [тег2]...{C_RESET}       \
— додати теги
  {C_BRIGHT}find-by-tag <тег>{C_RESET}                   \
— пошук за тегом
  {C_BRIGHT}filter-notes-by-tag <тег> [тег2]{C_RESET}    \
— відфільтрувати нотатки за тегами

{C_INFO}Система:{C_RESET}
  {C_BRIGHT}hello{C_RESET}                                — привітання
  {C_BRIGHT}help{C_RESET}                                 — це меню
  {C_BRIGHT}close / exit{C_RESET}                         — вийти та зберегти

{C_BRIGHT}Приклад: add John 1234567890{C_RESET}
"""
    return help_text.strip().ljust(40)


def main():
    book = load_data()
    notes = load_notes()

    print("Welcome to the assistant bot!")
    print(f"{C_INFO}Enter 'help' to see commands.{C_RESET}")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            save_notes(notes)
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

        elif command == "add-address":
            print(add_address(args, book))
            
        elif command == "edit-address":
            print(edit_address(args, book))
                   
        elif command == "add-email":
            print(add_email(args, book))

        elif command == "edit-email":
            print(edit_email(args, book))

        elif command in ["search", "find"]:
            print(search_contacts(args, book)) 

        elif command == "help":
            print(show_help())

        elif command == "delete":
            print(delete_contact(args, book))

               
# >>> Notes CLI Commands

        elif command == "add-note":
            print(add_note(args, notes))

        elif command == "show-note":
            print(show_note(args, notes))

        elif command in ["all-notes", "notes"]:
            print(all_notes_func(args, notes))

        elif command == "edit-note":
            print(edit_note(args, notes))

        elif command == "delete-note":
            print(delete_note(args, notes))

        elif command == "add-tag":
            print(add_tag(args, notes))

        elif command == "remove-tag":
            print(remove_tag(args, notes))

        elif command == "find-by-tag":
            print(find_by_tag(args, notes))

        elif command in ["search-notes", "find-notes"]:     # <<< ВИПРАВЛЕНО
            print(find_notes(args, notes))

        elif command == "filter-notes-by-tag":
            print(filter_notes_by_tag(args, notes))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
