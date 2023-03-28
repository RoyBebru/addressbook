"""Class Comment

Author: Dmytro Tarasiuk
URL: https://github.com/RoyBebru/addressbook
Email: RoyBebru@gmail.com
License: MIT
"""


from field import Field


class Comment(Field):

    def __init__(self, comment=""):
        super().__init__(value=comment, title="Comment", order=95)
        if bool(comment):
            self.value = comment # to validate non empty comment

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, comment):
        # old_comment = self._value
        self._value = comment

if __name__ == "__main__":
    p1 = Comment("samjdmsna asjdj as djashgdj as")
    p2 = Comment("samjdmsna asjdj as djashgdj as")
    print(p2, p2.title, p2.order)
    if p1 != p2:
        print("NOT EQ")
    else:
        print("EQ")
