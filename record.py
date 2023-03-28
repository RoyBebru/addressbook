"""Record

Author: Dmytro Tarasiuk
URL: https://github.com/RoyBebru/addressbook
Email: RoyBebru@gmail.com
License: MIT
"""


import os

from address import Address
from birthday import Birthday
from comment import Comment
from phone import Phone


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

    def sort_fields(self):
        fields = list(self.fields)
        fields.sort(key=lambda e: e.order)
        return fields

    def add(self, fields):
        for record_pair in fields:
            try:
                # Create field
                new_field = Record.known_field_titles[record_pair[0]](record_pair[1])
            except KeyError:
                raise RecordException(f"no such field '{record_pair[0]}'")
            if new_field.is_unique:
                is_present = False
                for field in self.fields:
                    if field.title == new_field.title:
                        # Is already present such unique field: ignoring new_filed
                        del new_field
                        is_present = True
                        break
                if is_present: # is present field like new_field?
                    continue # do not create duplicate of unique field
            # Add new field to tuple
            self.fields += (new_field,)

    def change(self, title: str, value: str, field_no=1):
        if isinstance(title, str):
            if not bool(title):
                raise RecordException("to change field title is required")
            if not bool(value):
                # Title is present but value is absent
                raise RecordException("to change a new parameter is required")
            fields = list(self.fields)
            fields.sort(key=lambda e: e.order)
            for field in self.sort_fields():
                if field.title == title:
                    field_no -= 1
                    if field_no <= 0:
                        field.value = value # changing field
                        break
            return

    def delete(self, title="", value="", field_no=1):
        if isinstance(title, str):
            if not bool(title):
                # Field title is absent: remove all field with value,
                # field_no is ignored 
                self.fields = tuple(field for field in self.fields
                                    if field != value)
                return
            if not bool(value):
                # Title is present but value is absent: removing
                # one field with field_no (if such is present)
                fields = ()
                for field in self.sort_fields():
                    if field.title == title:
                        field_no -= 1
                        if field_no <= 0:
                            del field
                            continue # forget field
                    fields += (field,)
                self.fields = fields
                return
            # Title and value is present: delete field with value.
            # field_no is ignored.
            self.fields = tuple(field for field in self.fields
                                if field.title != title or field != value)
            return

    def __str__(self):
        return str(self.as_tuple_of_tuples())

    def as_tuple_of_tuples(self):
        return tuple((field.title, str(field)) for field in self.fields)

    def report(self, indent=0) -> str:
        if len(self.fields) == 0:
            return ""
        field_format = " " * indent + "%s: %s"
        return os.linesep + \
            os.linesep.join(
            field_format % (field.title, str(field))
            for field in self.sort_fields())
