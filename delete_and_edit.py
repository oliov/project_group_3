from datetime import datetime, timedelta

class Record:
    def __init__(self, name, phone=None, email=None, address=None, birthday=None):
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.birthday = birthday  

    def __str__(self):
        return (f"Name: {self.name}, Phone: {self.phone or '-'}, "
                f"Email: {self.email or '-'}, Address: {self.address or '-'}, "
                f"Birthday: {self.birthday or '-'}")


class AddressBook:
    def __init__(self):
        self.records = [] #зберігаємо всі записи

    def add_record(self, record):
        self.records.append(record)

    def search(self, query):
        query = query.lower()
        results = []
        for record in self.records:
            name = record.name.lower() if record.name else ""
            phone = record.phone.lower() if record.phone else ""
            email = record.email.lower() if record.email else ""
            if query in name or query in phone or query in email:
                results.append(record)
        if not results:
            print("Збігів немає")
        else:
            print("Результати:")
            for r in results:
                print(r)

    def delete(self, name): #видалення контактів
        for record in self.records:
            if record.name.lower() == name.lower(): #шукаємо за іменем (регістронезалежно)
                self.records.remove(record)
                print(f"Контакт '{name}' видалено")
                return
        print("Контакт не знайдено")

    #редагування email
    def edit_email(self, name, new_email):
        for record in self.records:
            if record.name.lower() == name.lower():
                record.email = new_email
                print(f"Email для '{name}' оновлено")
                return
        print("Контакт не знайдено")

    #редагування адреси
    def edit_address(self, name, new_address):
        for record in self.records:
            if record.name.lower() == name.lower():
                record.address = new_address
                print(f"Адресу для '{name}' оновлено")
                return
        print("Контакт не знайдено")

    #метод для отримання майбутніх днів народження
    def get_upcoming_birthdays(self, days=7):
        today = datetime.today().date()  #пошук др у межах n днів
        upcoming = []

        for record in self.records:
            if record.birthday:
                try:
                    bday = datetime.strptime(record.birthday, "%Y-%m-%d").date() 
                    bday_this_year = bday.replace(year=today.year)  #дата др у поточному році
                    delta = (bday_this_year - today).days

                    if 0 <= delta <= days:
                        upcoming.append((record.name, record.birthday))
                except ValueError:
                    pass 

        if not upcoming:
            print("Відсутні записи у вказаний період")
        else:
            print(f"Дні народження у найближчі {days}:")
            for name, date_str in upcoming:
                print(f" - {name}: {date_str}")