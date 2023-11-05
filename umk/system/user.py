import os
import pwd
import grp

from beartype import beartype


class Group:
    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        return self._id

    @beartype
    def __init__(self, name: str, id: int):
        self._name = name
        self._id = id


class User(Group):
    @property
    def group(self) -> Group:
        return self._group

    @beartype
    def __init__(self, name: str, id: int, group: Group):
        super().__init__(name, id)
        self._group = group


def user() -> User:
    u = pwd.getpwuid(os.getuid())
    g = grp.getgrgid(u.pw_gid)
    return User(
        name=u.pw_name,
        id=u.pw_uid,
        group=Group(name=g.gr_name, id=g.gr_gid)
    )
