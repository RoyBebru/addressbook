"""Class Name

Author: Dmytro Tarasiuk
URL: https://github.com/RoyBebru/addressbook
Email: RoyBebru@gmail.com
License: MIT
"""

import re

from field import Field


class NameException(Exception):
    def __init__(self, *args, **kwargs):
        # Call parent constructor
        super(Exception, self).__init__(*args, **kwargs)


class Name(Field):
    # Common pattern for each object
    _c_pattern_name = (r"\b\w(?![0-9_])"
                       r"(?:(?<![0-9_])(?:\w|['-])(?![0-9_]))*"
                       r"(:?\w(?![0-9_]))?\b") # one word name pattern
    # Name consists of 1..3 words each can contain "'" or "-" in the middle
    _c_pattern_name = re.compile(_c_pattern_name
                        + r"(?:\s" + _c_pattern_name
                        + r"(?:\s" + _c_pattern_name + r")?"
                        + r")?", re.IGNORECASE) # up to 3 word name pattern

    def __init__(self, name):
        super().__init__(value=name, title="Name", order=10)
        if bool(name):
            self.name = name # to validate non empty name

    @property
    def name(self):
        return self.value

    @name.setter
    def name(self, name):
        name = self.normalize(name)
        error_message = self.verify(name)
        if bool(error_message):
            # Exception in the constructor does not create object
            raise NameException(error_message)
        # Name is proven and can be stored
        # old_name = self._value
        self.value = name

    def verify(self, name: str) -> bool:
        """Check name format"""
        m = Name._c_pattern_name.search(name)
        if not bool(m):
            return f"incorrect name '{name}'"
        if m.start() != 0:
            return f"extra symbol(s) '{name[:m.start()]}' in the start"
        if m.end() != len(name):
            return f"extra symbol(s) '{name[m.start():]}' in the end"
        # Name is proven
        return "" # name is verified

    def normalize(self, name) -> str:
        # Removing start/end spaces and change many spaces with one
        name = " ".join(str(name).split())
        return name

    def __eq__(self, name):
        """Case insensitive equal by words combination"""
        words2 = self.normalize(name)
        if len(words2) != len(self.name):
            return False
        words1 = self.name.lower().split(' ')
        words2 = words2.lower().split(' ')
        for word1 in words1:
            for word2 in words2:
                if word1 == word2:
                    break
            else:
                # No break was made: one word is not equal
                return False
        return True

    def __ne__(self, name):
        """Case insensitive inequal"""
        return not self == name

    def is_substr(self, name):
        words1 = self.name.lower().split(' ')
        words2 = self.normalize(name).lower().split(' ')
        for w1 in range(len(words1)):
            for w2 in range(len(words2)):
                if words2[w2] is None:
                    continue
                if words1[w1] == words2[w2]:
                    words1[w1] = None
                    words2[w2] = None
                    break
                elif words1[w1].find(words2[w2]) != -1:
                    words2[w2] = None
                    continue
                elif words2[w2].find(words1[w1]) != -1:
                    words1[w1] = None
                    break
        if len(tuple(x for x in filter(
                    lambda x: x is not None, words1))) == 0 or \
                len(tuple(x for x in filter(
                    lambda x: x is not None, words2))) == 0:
            return True
        return False

    def __hash__(self):
        return self.name.__hash__()

if __name__ == "__main__":
    p1 = Name("Вал'янець-Кал'янов Мар'ян Дем'янович")
    p2 = Name("М'ячін Тарас    Солов'янович")
    print(p2, p2.title, p2.order)
    if p1 != " Мар'ян   Дем'яновиЧ    Вал'янецЬ-Кал'янов ":
        print("NOT EQ")
    else:
        print("EQ")
    if p2.is_substr("  ___Солов'янович11111  wwwwwМ'ячін    vvvvvТарасvvv   "):
        print("~EQ~")
    else:
        print("NOT ~EQ~")