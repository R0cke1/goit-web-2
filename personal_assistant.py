from collections import defaultdict, UserDict
from datetime import datetime, timedelta
import pickle
from abc import ABC, abstractmethod

class Interface(ABC):
    @abstractmethod
    def send_message(self, message):
        pass 

class ConsoleInterface(Interface):
    def send_message(self, message):
        print(message)

class WebInterface(Interface):
    def send_message(self, message):
        print(f'FAKEWEB {message}')

    
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)  
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if len(value) == 10 and value.isdigit():
            self.__value = value
        else:
            raise ValueError('Invalid phone number')


class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            pass


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def delete_phone(self, phone):
        self.phones.remove(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for index in range(len(self.phones)):
            if self.phones[index].value == old_phone:
                self.phones[index] = Phone(new_phone)
            break

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p.value
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def find(self, name):
        if name in self.data:
            return self.data[name]
        return None

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.now()
        next_week = today + timedelta(days=7)

        for contact in self.data.values():
            if contact.birthday and contact.birthday.date:
                contact_birthday = datetime.strptime(contact.birthday.value, "%d.%m.%Y").date()
                contact_birthday = datetime.combine(contact_birthday, datetime.min.time())
                contact_birthday = contact_birthday.replace(year=today.year)
                if today <= contact_birthday <= next_week:
                    upcoming_birthdays.append(contact)
                elif next_week < today and contact_birthday.year == today.year + 1:
                    upcoming_birthdays.append(contact)
        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Give me name and phone please."
        except KeyError:
            return "Give me name and phone please."

    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book):
    name, phone = args
    if name in book:
        book[name].add_phone(phone)
        return "Contact updated."
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."


@input_error
def change_contact(args, book):
    name, new_phone = args
    if name in book:
        record = book[name]
        record.phones = [new_phone]  
        return "Contact updated."
    else:
        return f"Contact with name {name} not found."


@input_error
def show_phone(args, book):
    name = args[0]
    if name in book:
        return f"Phone number for {name}: {', '.join(book[name].phones)}"
    else:
        return f"Contact with name {name} not found."


@input_error
def show_all(args, book):
    if book:
        result = "All contacts:\n"
        for name, record in book.items():
            phone_numbers = ', '.join(str(phone) for phone in record.phones)
            result += f"{name}: {phone_numbers}\n"
        return result
    else:
        return "No contacts saved."


@input_error
def add_birthday(args, book):
    name, birthday = args
    contact = book.find(name)
    if contact:
        contact.add_birthday(birthday)
        return f"Birthday added for {name}"
    else:
        record = Record(name)
        record.add_birthday(birthday)
        book.add_record(record)
        return f"New contact {name} created with birthday {birthday}"


@input_error
def show_birthday(args, book):
    name, *_ = args
    contact = book.find(name)
    if contact:
        return f"{contact.name}'s birthday is on {contact.birthday.value}"
    else:
        return f"No contact found with name {name}"


@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "Upcoming birthdays:\n" + "\n".join(
            [f"{contact.name}: {contact.birthday.value}" for contact in upcoming_birthdays]
        )
    
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook() 
    
def main():
    book = load_data()
    ui = WebInterface()
    ui.send_message("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            ui.send_message("Good bye!")
            break
        elif command == "hello":
            ui.send_message("How can I help you?")
        elif command == "add":
            ui.send_message(add_contact(args, book))
        elif command == "change":
            ui.send_message(change_contact(args, book))
        elif command == "phone":
            ui.send_message(show_phone(args, book))
        elif command == "all":
            ui.send_message(show_all(args, book))
        elif command == "add-birthday":
            ui.send_message(add_birthday(args, book))
        elif command == "show-birthday":
            ui.send_message(show_birthday(args, book))
        elif command == "birthdays":
            ui.send_message(birthdays(args, book))
        
    save_data(book)

if __name__ == "__main__":
    main()