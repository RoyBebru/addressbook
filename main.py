#!/usr/bin/env python3
"""Main file

Author: Dmytro Tarasiuk
URL: https://github.com/RoyBebru/addressbook
Email: RoyBebru@gmail.com
License: MIT
"""

from addressbook import AddressBook, AddressBookException
from birthday import BirthdayException
from name import Name, NameException
from phone import Phone, PhoneException
from record import Record, RecordException

import atexit
import json
import os
from pathlib import Path
import re
import sys


"""CONSTANTS"""
path = Path(sys.argv[0])
SCRIPT_NAME = path.name
SCRIPT_DIR = path.parent.resolve()
ADDRESSBOOK_PATHFILE = SCRIPT_DIR / (path.stem + ".abo")
HISTFILE = SCRIPT_DIR / (path.stem + ".history")


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
        + "produces MATCH-SET"
        + os.linesep + "Command 'search' produces MATCH-SUBSET from MATCH-SET."
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
        + os.linesep + "Delete searched record(s) or field: "
        + "> delete [<field_name>[<num>]]"
        + os.linesep + "Change name field in searched record: "
        + "> change name Лабуда Зоряна Акакіївна"
        + os.linesep + "Change 1st phone field in searched record: "
        + "> change phone +38 (033) 222-11-33"
        + os.linesep + "Change 2nd phone field in searched record: "
        + "> change phone2 333-33-333"
        + os.linesep + "Add new record. This record will be serched: "
        + "> add Голілиць Рада Варфоломіївна"
        + os.linesep + "Add new field to the last searched record: "
        + "> add phone +48 551-051-555"
    )


@command_error_catcher
def cmd_add(cmd_args: str, box):
    if not bool(cmd_args):
        return "Argument required, use help for more information"
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
        value = ' '.join(args)
        name = Name(value)
        if isinstance(box.ab[name], Record):
            return f"Error: name '{' '.join(args)}' already exists" 
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

    # Checking for field index
    for ix in range(len(title)-1,-1,-1):
        if not title[ix].isdigit():
            if ix == len(title)-1:
                # No suffix number
                field_no = 1
            else:
                # File_no 0 is the same as 1
                field_no = int(title[ix+1:]) or 1
                title = title[:ix+1]
            break
    else:
        field_no = 1 # index is absent

    for field_title in Record.known_field_titles.keys():
        if title == field_title:
            # Field title is present: change field value 
            args.pop(0)
            value = " ".join(args)
            for name in box.ab_fit_to_fit:
                box.ab[name].change(title, value, field_no)
            break # field is found and changed
    else:
        if title != "Name":
            return "Unknown field name"
        args.pop(0)
        value = " ".join(args)
        if bool(value):
            for name in box.ab_fit_to_fit:
                box.ab[name] = value
        else:
            return "Change error: Name field parameter is required"
    box.ab.is_modified = True
    return


@command_error_catcher
def cmd_delete(cmd_args: str, box):
    args = cmd_args.split(' ') # [''] == ''.split(' ')
    title = args[0].capitalize()

    # Checking for field index
    for ix in range(len(title)-1,-1,-1):
        if not title[ix].isdigit():
            if ix == len(title)-1:
                # No suffix number
                field_no = 1
            else:
                # File_no 0 is the same as 1
                field_no = int(title[ix+1:]) or 1
                title = title[:ix+1]
            break
    else:
        field_no = 1 # index is absent

    for field_title in Record.known_field_titles.keys():
        if title == field_title:
            # Field title is present: delete this field within record(s)
            args.pop(0)
            value = " ".join(args)
            for name in box.ab_fit_to_fit:
                box.ab[name].delete(title, value, field_no)
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
    for (name, record_list_of_list) in ab.items():
        ab_as_tuple += ( ((name,) + tuple((pair[0], pair[1])
                        for pair in record_list_of_list)), )
    return ab_as_tuple


def input_or_default(prompt="", default=""):
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        return default


def main() -> None:
    # Function is used as convenient container for associated objects
    def box(): pass
    box.ab = AddressBook(load_addressbook())
    box.ab_fit = box.ab.keys()
    box.ab_fit_to_fit = box.ab_fit
    print("Use ? for more information")

    while True:

        for attempt in range(2):
            cmd_raw = input_or_default(
                f"({len(box.ab)}" # total records
                f"({len(box.ab_fit)}" # records in MATCH SET
                f"({len(box.ab_fit_to_fit)}" # records in MATCH SUBSET
                f"((C> ", "Ctrl+C")
            if cmd_raw == "Ctrl+C":
                # Is pressed Ctrl+C or Ctrl+D
                if not bool(attempt) and box.ab.is_modified:
                    print(os.linesep + "Addressbook was modified: use "
                          "'exit' or '.' to save changes and exit." +
                          os.linesep + "Or press Ctrl+C again to exit "
                          "without saving")
                    continue
                print("")
                return # exit without saving
            else:
                break

        (cmd, cmd_args) = parse(normalize(cmd_raw))

        handler = get_handler(cmd)

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
