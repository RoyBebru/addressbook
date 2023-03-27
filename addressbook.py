#!/usr/bin/env python3
"""Address Book

Author: Dmytro Tarasiuk
URL: https://github.com/RoyBebru/addressbook
Email: RoyBebru@gmail.com
License: MIT
"""


import atexit
from collections import UserDict
import json
import os
from pathlib import Path
import re
import sys

from address import Address
from birthday import Birthday, BirthdayException
from comment import Comment
from name import Name, NameException
from phone import Phone, PhoneException


"""CONSTANTS"""
path = Path(sys.argv[0])
SCRIPT_NAME = path.name
SCRIPT_DIR = path.parent.resolve()
ADDRESSBOOK_PATHFILE = SCRIPT_DIR / (path.stem + ".ab")
HISTFILE = SCRIPT_DIR / (path.stem + ".history")


class RecordException(Exception):
    def __init__(self, *args, **kwargs):
        # Call parent constructor
        super(Exception, self).__init__(*args, **kwargs)


class Record:
    """Can contain any Field exclude Name"""
    known_field_titles = {"Phone": Phone
                         , "Birthday": Birthday
                         , "Address": Address
                         , "Comment": Comment
                         }

    def __init__(self, fields):
        self.fields = ()
        self.add(fields)

    def add(self, fields):
        for record_pair in fields:
            try:
                # Create field and add it to tuple
                # print(f"Create field {record_pair[0]}:{record_pair[1]}")
                self.fields += \
                    (Record.known_field_titles[record_pair[0]](record_pair[1]),)
            except KeyError:
                raise RecordException(f"no such field '{record_pair[0]}'")

    def delete(self, title="", value=""):
        if isinstance(title, str):
            if not bool(title):
                # Field title is absent: remove all field with value
                self.fields = tuple(field for field in self.fields
                                    if field != value)
                return
            if not bool(value):
                # Title is present but value is absent
                self.fields = tuple(field for field in self.fields
                                    if field.title != title)
                return
            self.fields = tuple(field for field in self.fields
                                if field.title != title or field != value)
            return

    def change(self, title: str, value: str):
        if isinstance(title, str):
            if not bool(title):
                raise RecordException("to change field title is required")
            if not bool(value):
                # Title is present but value is absent
                raise RecordException("to change a new parameter is required")
            for field in self.fields:
                if field.title == title:
                    field.value = value # changing field
            return

    def __str__(self):
        return str(self.as_tuple_of_tuples())

    def as_tuple_of_tuples(self):
        return tuple((field.title, str(field)) for field in self.fields)
    
    def report(self, indent=0) -> str:
        if len(self.fields) == 0:
            return ""
        fields = list(self.fields)
        fields.sort(key=lambda e: e.order)
        field_format = " " * indent + "%s: %s"
        return os.linesep + \
            os.linesep.join(
            field_format % (field.title, str(field))
            for field in fields)


class AddressBookException(Exception):
    def __init__(self, *args, **kwargs):
        # Call parent constructor
        super(Exception, self).__init__(*args, **kwargs)


class AddressBook(UserDict):

    def __init__(self, records=()):
        """ Instead tuple() can be used list[] or vice versa: 
        ab = AddressBook(
            ("Mykola", (("Phone", "111-22-33"), ("Phone", "111-44-55"), ...)))
        )
        ab = AddressBook((
            ("Mykola": (("Phone", "111-22-33"), ("Phone", "111-44-55"), ...))),
            ("Oleksa": (("Phone", "333-22-33"), ("Phone", "333-44-55"), ...))),
        ))
        """
        super().__init__({})
        self[None] = records # call __setitem__()
        self.is_modified = False

    def __getitem__(self, key):
        """
         key    | Return
        --------+-------------------------------------
        1) None | ( ("Name1", ("Phone", "111222333"), ...), 
                |   ("Name2", ("Phone", "111222333"), ...), ... 
                | )
        3) Name | Record data[key] 
        6) str  | for each in keys() is_substr(key) return (Name1, Name2, ...)
        """
        if key is None:
            return tuple((str(name), record.as_tuple_of_tuples())
                         for (name, record) in self.data.items())
        elif isinstance(key, Name):
            return self.data[key]
        elif isinstance(key, str):
            return tuple(name for name in filter(
                lambda n: n.is_substr(key), self.keys()))
        raise AddressBookException(f"unsopported key {key}")

    def __setitem__(self, key, value):
        """
         key    | value              | Action
        --------+--------------------+-------------------------------------
        1) None | ("Name", ("Phone", "111222333"), ...)
                |                    | self.data[Name(value["Name"])]
                |                    |     = Record(value)
        2) None | ( ("Name", ("Phone", "111222333"), ...), 
                |   ("Name", ("Phone", "111222333"), ...), ... 
                | )                  | many times (1)
        3) Name | ("Name", ("Phone", "111222333"), ...)
                |                    | self.data[Name] = Record(value)
        4) Name | Record             | self.data[Name] = Record
        5) Name | str_new_name       | change Name
        6) str  | ("Name", ("Phone", "111222333"), ...)
                |                    | self.data[Name(key)] = Record(value)
        7) str  | Record             | self.data[Name(key)] = Record
        """
        if key is None:
            if len(value) == 0:
                self.data.clear()
                self.is_modified = True
                return
            if isinstance(value, tuple) or isinstance(value, list):
                if isinstance(value[0], str):
                    self.data[Name(value[0])] = Record(value[1:])   # (1)
                    self.is_modified = True
                    return
                for item in value:                                  # (2)
                    if not isinstance(item[0], str):
                        raise AddressBookException(
                            f"absent required name as "
                            f"the first item in {item}")
                    self.data[Name(item[0])] = Record(item[1:])
                    self.is_modified = True
                return
            raise AddressBookException(f"not supported value {value}")
        elif isinstance(key, Name):
            if isinstance(value, tuple) or isinstance(value, list): # (3)  
                self.data[key] = Record(value)
            elif isinstance(value, Record):                         # (4)
                self.data[key] = value
            elif isinstance(value, str):                            # (5)
                record = self.data[key]
                self.data.pop(key)
                key.name = value
                self.data[key] = record
            else:
                raise AddressBookException(f"not supported value {value}")
        elif isinstance(key, str):
            if isinstance(value, tuple) or isinstance(value, list): # (6)
                self.data[Name(key)] = Record(value)
            elif isinstance(value, Record):                         # (7)
                self.data[Name(key)] = value
            else:
                raise AddressBookException(f"not supported value {value}")
        else:
            raise AddressBookException(f"not supported key {key}")

        self.is_modified = True
        return

    def __str__(self):
        return str(self[None])

    def keys(self):
        return tuple(super().keys())

    def report(self, names = None, index=1):
        if names is None:
            names = list(self.data.keys())
        elif isinstance(names, Name):
            names = (names,)
        if isinstance(names, tuple) or isinstance(names, list):
            index -= 1
            indent = len(str(len(names)))
            name_format = f"#%-{indent}d %s: %s"
            indent += len("# ")
            return (os.linesep * 2).join(
                name_format % (index := index + 1, name.title, str(name))
                + self.data[name].report(indent)
                for name in names)
        return ""

    def _sample_to_regex(self, sample):
        """Converts:
        Matches any zero or more characters: '*' -> '.*'
        Matches any one character: '?' -> '.?'
        Matches exactly one character that is a member of
            the string string: '[string]' -> '[string]'
        Removes the special meaning of the character
            that follows it: '\' -> '\'
        """
        sample = re.sub(r"(?<!\\)\*", r".*", sample)
        sample = re.sub(r"(?<!\\)\?", r".?", sample)
        sample = re.sub(r"(?<!\\)\+", r"\+", sample)
        sample = re.sub(r"(?<!\\)\(", r"\(", sample)
        sample = re.sub(r"(?<!\\)\)", r"\)", sample)
        sample = re.sub(r"(?<!\\)\|", r"\|", sample)
        return sample

    def iter_by_sample(self, sample: str, names=None):
        if names is None:
            names = list(self.data.keys())
        elif isinstance(names, Name):
            names = (names,)
        if isinstance(names, tuple) or isinstance(names, list):
            try:
                rex = re.compile(self._sample_to_regex(sample),
                                re.IGNORECASE|re.MULTILINE)
            except re.error:
                raise AddressBookException("error sample in metasymbols")
            index = 1
            for name in names:
                if rex.search(self.report([name], index=index)):
                    yield name
                index += 1

    def JSON_helper(self):
        ab = {}
        for (name, record) in self.data.items():
            rec_list = list(record.as_tuple_of_tuples())
            rec_list.sort(reverse=True, key=lambda it: it[0])
            ab[str(name)] = dict(rec_list)
        return ab

def command_error_catcher(cmd_hundler):
    def decor(cmd_args, box):
        try:
            return cmd_hundler(cmd_args, box)
        except AddressBookException as e:
            return f"AddressBook Error: {e.args[0]}"
        except RecordException as e:
            return f"Record Error: {e.args[0]}"
        except NameException as e:
            return f"Name Error: {e.args[0]}"
        except PhoneException as e:
            return f"Phone Error: {e.args[0]}"
        except BirthdayException as e:
            return f"Birthday Error: {e.args[0]}"
    return decor

# @command_error_catcher
def cmd_help(*__):
    return ("Application uses MATCH-SET and MATCH-SUBSET. Command 'show' "
        + "produced MATCH-SET"
        + os.linesep + "Command 'search' produced MATCH-SUBSET from MATCH-SET."
        + "Commands 'add', 'change',"
        + os.linesep + "and 'delete' work with MATCH-SET. Commands have synonyms and "
        + "short forms including"
        + os.linesep + "ukrainian."
        + os.linesep + "Matches all records in address book: > all"
        + os.linesep + "Matches records with the relevant phone number: "
        + "> show 111-22-33"
        + os.linesep + "Matches records with the relevant person name: "
        + "> show Кас'ян Дем'янович Непийпиво-В'юнець"
        + os.linesep + "Show matching records: > show"
        + os.linesep + "Search in matching records by template with "
        + "metasymbols '*'/'?': > search #2"
        + os.linesep + "Delete searched record(s) or field: > delete [<field_name>]"
        + os.linesep + "Change name field in searched record: "
        + "> change name Лабуда Зоряна Акакіївна"
        + os.linesep + "Change 1st phone field in searched record: "
        + "> change phone +38 (033) 222-11-33"
        + os.linesep + "Change 2nd phone field in searched record: "
        + "> change phone 2 333-33-333"
        + os.linesep + "Add new record. This record will be serched: "
        + "> add Голілиць Рада Варфоломіївна"
        + os.linesep + "Add new field to the last searched record: "
        + "> add phone +48 551-051-555"
    )

@command_error_catcher
def cmd_add(cmd_args: str, box):
    if not bool(cmd_args):
        return "argument required, use help for more information"
    args = cmd_args.split(' ')
    title = args[0].capitalize()
    for field_title in Record.known_field_titles.keys():
        if title == field_title:
            args.pop(0)
            for name in box.ab_fit_to_fit:
                # Add new field
                box.ab[name].add( ((title, ' '.join(args)),) )
            break
    else:
        if title == "Name":
            args.pop(0) # omit option title "Name"
        # Create new record
        name = Name(' '.join(args))
        box.ab[name] = ()
        box.ab_fit += (name,)
        box.ab_fit_to_fit = (name,)
    box.ab.is_modified = True
    return None

# @command_error_catcher
def cmd_all(cmd_args: str, box):
    box.ab_fit = box.ab.keys()
    box.ab_fit_to_fit = box.ab_fit
    return None

@command_error_catcher
def cmd_change(cmd_args: str, box):
    args = cmd_args.split(' ') # [''] == ''.split(' ')
    title = args[0].capitalize()
    for field_title in Record.known_field_titles.keys():
        if title == field_title:
            # Field title is present: change field value 
            args.pop(0)
            value = " ".join(args)
            for name in box.ab_fit_to_fit:
                box.ab[name].change(title, value)
            break # field is found and changed
    else:
        if title != "Name":
            return "Change Error: unknown field name"
        args.pop(0)
        value = " ".join(args)
        if bool(value):
            for name in box.ab_fit_to_fit:
                box.ab[name] = value
        else:
            return "Change Error: Name field parameter is required"
    box.ab.is_modified = True
    return

@command_error_catcher
def cmd_delete(cmd_args: str, box):
    args = cmd_args.split(' ') # [''] == ''.split(' ')
    title = args[0].capitalize()
    for field_title in Record.known_field_titles.keys():
        if title == field_title:
            # Field title is present: delete this field within record(s)
            args.pop(0)
            value = " ".join(args)
            for name in box.ab_fit_to_fit:
                box.ab[name].delete(title, value)
            break # field is found and deleted
    else:
        if title == "Name" or not bool(title):
            args.pop(0) # omit option title "Name"

        if len(args) == 0:
            # Delete all record(s) in ab_fit
            box.ab_fit = tuple(name for name in box.ab_fit
                            if name not in box.ab_fit_to_fit)
            for name in box.ab_fit_to_fit:
                box.ab.pop(name)
        else:
            value = " ".join(args)
            # Delete record(s) with Name == value
            box.ab_fit = tuple(name for name in box.ab_fit
                            if name not in box.ab_fit_to_fit \
                                or not name.is_substr(value))
            for name in box.ab_fit_to_fit:
                if name.is_substr(value):
                    box.ab.pop(name)
        box.ab_fit_to_fit = box.ab_fit
    box.ab.is_modified = True
    return

@command_error_catcher
def cmd_exit(*args):
    # dump_addressbook(args[1])
    return None

def report_fit_to_fit(box):
    report = ""
    for name in box.ab_fit_to_fit:
        if bool(report):
            report += os.linesep * 2
        report += box.ab.report(name, index=box.ab_fit.index(name)+1)
    return report

@command_error_catcher
def cmd_search(cmd_args: str, box):
    box.ab_fit_to_fit = tuple(name for name in box.ab.iter_by_sample(
            cmd_args, names=box.ab_fit))
    return report_fit_to_fit(box)

@command_error_catcher
def cmd_show(cmd_args: str, box):
    if not bool(cmd_args):
        return report_fit_to_fit(box) 
    try:
        box.ab_fit = ()
        ph = Phone(cmd_args)
        for name in box.ab.keys():
            for field in box.ab[name].fields:
                if isinstance(field, Phone) and field == ph:
                    box.ab_fit += (name,)
                    break
    except PhoneException:
        box.ab_fit = box.ab[cmd_args]
    box.ab_fit_to_fit = box.ab_fit
    return box.ab.report(box.ab_fit)

def cmd_unknown(*args):
    return "Unknown command: use help command for more information"

def normalize(cmd: str) -> str:
    # Change many spaces with one and remove prefix/suffix space(s)
    return " ".join(cmd.split())

def parse(norm_cmd: str) -> tuple:
    i = norm_cmd.find(' ')
    if i == -1:
        return (norm_cmd, '')
    return (norm_cmd[:i], norm_cmd[i+1:])

HANDLERS = {
    cmd_add: re.compile(r"^(?:ad|add|"
                        r"дод|дода|додай|додат|додати)$",
                        re.IGNORECASE),
    cmd_all: re.compile(r"^(?:"+r"al|all|"
                        r"в|вс|вс[іе])$",
                        re.IGNORECASE),
    cmd_change: re.compile(r"^(?:c|ch|cha|chan|chang|change|"
                           r"з|зм|змі|змін|зміна|зміни|змінит|змінити)$",
                           re.IGNORECASE),
    cmd_delete: re.compile(r"^(?:d|de|del|dele|delet|delete|"
                           r"вид|вида|видал|видали|видалит|видалити)$",
                           re.IGNORECASE),
    cmd_exit: re.compile(r"^(?:\.|e|ex|exi|exit|"
                         r"q|qu|qui|quit|"
                         r"b|by|bye|"
                         r"вий|вий[тд]|вий[дт]и|вих|вихі|вихід)$",
                         re.IGNORECASE),
    cmd_help: re.compile(r"^(?:\?|h|he|hel|help|"
                         r"доп|допо|допом|допомо|допомож|допоможи|допомог|допомога)$",
                         re.IGNORECASE),
    cmd_search: re.compile(r"^(?:se|se[ea]|sear|searc|search|"
                           r"ш|шу|шук|шука|шукай|шукат|шукати)$",
                           re.IGNORECASE), 
    cmd_show: re.compile(r"^(?:sh|sho|show|"
                         r"п|по|пок|пока|пока[зж]|покажи|показа|показат|показати|"
                         r"ди|див|диви|дивис|дивися|дивит|дивити|дивитис|дивитис[яь])$",
                         re.IGNORECASE),
}

def get_handler(cmd: str):
    for (func, regex) in HANDLERS.items():
        if regex.search(cmd):
            return func
    return cmd_unknown

def dump_addressbook(box):
    if not box.ab.is_modified:
        return
    try:
        with open(ADDRESSBOOK_PATHFILE, "w") as fh:
            fh.write(json.dumps(box.ab.JSON_helper(), 
                                indent=2,
                                ensure_ascii=False))
    except PermissionError:
        return
    box.ab.is_modified = False
    return

def load_addressbook():
    try:
        with open(ADDRESSBOOK_PATHFILE, "r") as fh:
            ab = json.loads(fh.read())
    except FileNotFoundError:
        return ()
    except PermissionError:
        return ()
    
    ab_as_tuple = ()
    for (name, record) in ab.items():
        ab_as_tuple += ( ((name,) + tuple((title, value)
                        for (title, value) in record.items())), )
    return ab_as_tuple


def main() -> None:
    # Function is used as convenient container for associated objects
    def box(): pass
    box.ab = AddressBook(load_addressbook())
    box.ab_fit = box.ab.keys()
    box.ab_fit_to_fit = box.ab_fit
    print("Use ? for more information")
    while True:

        for attempt in range(2):
            try:
                cmd_raw = input("(_((_(((> ")
                break
            except (KeyboardInterrupt, EOFError):
                # Is pressed Ctrl+C or Ctrl+D
                if not bool(attempt) and box.ab.is_modified:
                    print(os.linesep + "Addressbook was modified: use 'exit' or '.' "
                          "to save changes and exit." +
                          os.linesep + "Or press Ctrl+C again to exit "
                          "without saving")
                    continue
                print("")
                return # exit without saving

        (cmd, cmd_args) = parse(normalize(cmd_raw))
        handler = get_handler(cmd)
        # print(f"Call {handler.__name__}")
        result_text = handler(cmd_args, box)
        if bool(result_text):
            print(result_text)
        if handler is cmd_exit:
            dump_addressbook(box)                
            break


def turn_on_edit_in_input():
    try:
        import readline
        try:
            readline.read_history_file(HISTFILE)
        except FileNotFoundError:
            pass
        # Default history len is -1 (infinite), which may grow unruly
        readline.set_history_length(1000)
        atexit.register(readline.write_history_file, HISTFILE)
    except ModuleNotFoundError:
        pass


if __name__ == "__main__":

    turn_on_edit_in_input()
    main()
