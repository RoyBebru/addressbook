"""Class Address

Author: Dmytro Tarasiuk
URL: https://github.com/RoyBebru/addressbook
Email: RoyBebru@gmail.com
License: MIT
"""


from field import Field


class Address(Field):

    def __init__(self, address=""):
        super().__init__(value=address, title="Address", order=50)
        if bool(address):
            self.value = address # to validate non empty address

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, address):
        address = self.normalize(address)
        # old_address = self._value
        self._value = address

    def normalize(self, address) -> str:
        # Removing start/end spaces and change many spaces with one
        address = " ".join(str(address).split())
        return address

if __name__ == "__main__":
    p1 = Address("samjdmsna asjdj as djashgdj                 as")
    p2 = Address("samjdmsna          asjdj as djashgdj as")
    print(p2, p2.title, p2.order)
    if p1 != p2:
        print("NOT EQ")
    else:
        print("EQ")
