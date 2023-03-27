"""Class Name

Author: Dmytro Tarasiuk
URL: https://github.com/RoyBebru/addressbook
Email: RoyBebru@gmail.com
License: MIT
"""

class Field:

    def __init__(self, value = "", title="", order=0):
        # Field title, such as "Phone", "E-mail", "Name", etc
        self.title = title
        # Field to sort
        self.order = order
        self._value = ""
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = self.normalize(value)

    def normalize(self, value):
        return value

    def __str__(self):
        return self.value

    def __eq__(self, value):
        return self.value.lower() == str(value).lower()

    def __ne__(self, value):
        return not self == value


if __name__ == "__main__":
    f1 = Field("data", "Comment", 90)
    f1.value = "Datum"
    f1.order = 85
    print(f1, f1.title, f1.order)

