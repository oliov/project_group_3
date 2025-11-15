class Record:
    def __init__(self, name, phone=None, email=None, address=None, birthday=None):
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.birthday = birthday  

    def __str__(self):
        return f"Name: {self.name}, Phone: {self.phone or '-'}, Email: {self.email or '-'}"
    
class AddressBook:
    def __init__(self):
        self.records = [] #список записів
    def add_record(self, record):
        self.records.append(record) #додаємо запис
    def search(self, query): #пошук записів

        query = query.lower() #зап для нечутл до регістру

        results = [] #список для результатів

        for record in self.records:
            name = record.name.lower() if record.name else ""
            phone = record.phone.lower() if record.phone else ""
            email = record.email.lower() if record.email else ""

            if (query in name) or (query in phone) or (query in email): #співпадіння в будь-якому полі
                results.append(record)

        if not results:
            print("Збігів немає")        
        else:
            print("Результати:")
            for r in results:
                print(r)
                