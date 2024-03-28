from umk.framework import project
from umk.framework.adapters import go
from umk.framework import dependencies as dep


@project.entry
def entry():
    p = project.Golang()
    p.info.id = "go-example"
    p.info.name = "Golang Example"
    p.info.description = "Unimake project example (golang based)"
    p.info.version = "v1.0.0"
    p.info.contrib("Edward Sarkisyan", "edw.sarkisyan@gmail.com")
    p.info.contrib("Some User", "some.user@mail.net")
    p.dependencies["build"] = [
        dep.apt("make", "git"),
        dep.gomod(p.layout.root, go.Go())
    ]
    return p


# @project.entry
# class Entry(project.Golang):
#     def __init__(self):
#         super().__init__()
#         self.info.id = "go-example"
#         self.info.name = "Golang Example"
#         self.info.description = "Unimake project example (golang based)"
#         self.info.version = "v1.0.0"
#         self.info.contrib("Edward Sarkisyan", "edw.sarkisyan@gmail.com")
#         self.info.contrib("Some User", "some.user@mail.net")
#         self.dependencies["build"] = [
#             dep.apt("make", "git")
#         ]


@project.action
def build(pro: project.Golang):
    for dependencies in pro.dependencies.values():
        for dependency in dependencies:
            dependency.resolve()
