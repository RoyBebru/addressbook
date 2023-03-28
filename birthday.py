"""Class Birthday

Author: Dmytro Tarasiuk
URL: https://github.com/RoyBebru/addressbook
Email: RoyBebru@gmail.com
License: MIT
"""


from datetime import date, datetime

from field import Field


class BirthdayException(Exception):
    def __init__(self, *args, **kwargs):
        # Call parent constructor
        super(Exception, self).__init__(*args, **kwargs)


class Birthday(Field):
    # Common pattern for each object
    def __init__(self, birthday=""):
        super().__init__(value=birthday, title="Birthday", order=80, is_unique=True)
        if bool(birthday):
            self.value = birthday # to validate non epmpty birthday

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, birthday):
        birthday = self.verify(birthday)
        if len(birthday) > 10:
            raise BirthdayException(birthday)
        # old_birthday = self._value
        self._value = birthday

    def verify(self, birthday):
        """Return len(text)>10 if error or date in text format like '11.03.2011'"""
        if isinstance(birthday, date) or isinstance(birthday, datetime):
            return birthday.strftime(r"%d.%m.%Y")
        elif not isinstance(birthday, str):
            return f"bad value form '{birthday}'"
        birthday = ''.join(birthday.split()) # remove all spaces
        if birthday == "":
            return "" # empty birthday is valid
        try:
            birthday = datetime.strptime(birthday, r"%d.%m.%Y")
        except ValueError:
            try:
                birthday = datetime.strptime(birthday, r"%d.%m.%y")
            except ValueError:
                return f"wrong value '{birthday}'"
        return birthday.strftime(r"%d.%m.%Y")

    def __eq__(self, birthday):
        birthday = self.verify(birthday)
        return self.value == birthday

    def __ne__(self, birthday):
        return not self == birthday


if __name__ == "__main__":
    p1 = Birthday("10.11.12")
    print(p1, p1.title, p1.order)
    p2 = Birthday("10.11.2012")
    print(p2, p2.title, p2.order)
    if p1 != p2:
        print("NOT EQ")
    else:
        print("EQ")
