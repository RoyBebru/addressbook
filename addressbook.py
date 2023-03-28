"""AddressBook

Author: Dmytro Tarasiuk
URL: https://github.com/RoyBebru/addressbook
Email: RoyBebru@gmail.com
License: MIT
"""


from collections import UserDict
import os
import re

from name import Name
from record import Record


class AddressBookException(Exception):
    def __init__(self, *args, **kwargs):
        # Call parent constructor
        super(Exception, self).__init__(*args, **kwargs)


class AddressBook(UserDict):

    def __init__(self, records=()):
        """ Instead tuple() in records can be used list[] or vice versa: 
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
            ab[str(name)] = rec_list
        return ab
