"""Class Phone

Author: Dmytro Tarasiuk
URL: https://github.com/RoyBebru/addressbook
Email: RoyBebru@gmail.com
License: MIT
"""


import re

from field import Field


class PhoneException(Exception):
    def __init__(self, *args, **kwargs):
        # Call parent constructor
        super(Exception, self).__init__(*args, **kwargs)


class Phone(Field):
    # Common pattern for each object
    pattern_phone_number = re.compile(
            r"(?:\+\d{1,3})?\s*(?:\(\d{2,5}\)|\d{2,5})?"
            r"\s*\d{1,3}(?:\s*-)?\s*\d{1,3}(?:\s*-)?\s*\d{1,3}")

    def __init__(self, phone=""):
        super().__init__(value=phone, title="Phone", order=30)
        if bool(phone):
            self.value = phone # to validate non epmpty phone number

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, phone):
        phone = self.normalize(phone)
        error_message = self.verify(phone)
        if bool(error_message):
            # Exception in the constructor does not create object
            raise PhoneException(error_message)
        # Phone number is proven and can be stored
        self._value = phone

    def verify(self, phone: str) -> bool:
        """Check phone format"""
        m = Phone.pattern_phone_number.search(phone)
        if not bool(m):
            return f"incorrect number '{phone}'"
        if m.start() != 0:
            return f"extra symbol(s) '{phone[:m.start()]}' in the start"
        if m.end() != len(phone):
            return f"extra symbol(s) '{phone[m.end():]}' in the end"
        if sum(map(lambda x: bool(x.isdigit()), phone)) < 5:
            return f"number '{phone}' is very short to be correct"
        # Phone number is proven
        return ""

    def normalize(self, phone) -> str:
        # Removing start/end spaces and change many spaces with one
        phone = " ".join(str(phone).split())
        phone = phone.replace(" - ", "-").replace(" -", "-").replace("- ", "-")
        return phone

    def _get_digits_from_str(self, text: str) -> str:
        return "".join(filter(str.isdigit, text))

    def __eq__(self, phone):
        if self._get_digits_from_str(str(self)) \
                == self._get_digits_from_str(str(phone)):
            return True
        return False

    def __ne__(self, phone):
        return not self == phone


if __name__ == "__main__":
    p1 = Phone("777-77-77")
    print(p1, p1.title, p1.order)
    p2 = Phone("(777) 7-777")
    if p1 != p2:
        print("NOT EQ")
    else:
        print("EQ")
    p1.value = "999-99-00"
    print(p1)
