import os
import pwd
import grp

from umk import core


class Group(core.Model):
    id: None | int = core.Field(
        default=None,
        description="Group ID."
    )
    name: None | str = core.Field(
        default=None,
        description="Group name."
    )


class User(Group):
    group: Group = core.Field(
        default_factory=Group,
        description="User group info."
    )


def user() -> User:
    u = pwd.getpwuid(os.getuid())
    g = grp.getgrgid(u.pw_gid)
    return User(
        name=u.pw_name,
        id=u.pw_uid,
        group=Group(name=g.gr_name, id=g.gr_gid)
    )
