from umk.framework import project


# @project.entry
# def entry():
#     p = project.Golang()
#     p.info.id = "go-example"
#     p.info.name = "Golang Example"
#     p.info.description = "Unimake project example (golang based)"
#     p.info.version = "v1.0.0"
#     p.info.contrib("Edward Sarkisyan", "edw.sarkisyan@gmail.com")
#     p.info.contrib("Some User", "some.user@mail.net")
#     return p


@project.entry
class Entry(project.Golang):
    def __init__(self):
        super().__init__()
        self.info.id = "go-example"
        self.info.name = "Golang Example"
        self.info.description = "Unimake project example (golang based)"
        self.info.version = "v1.0.0"
        self.info.contrib("Edward Sarkisyan", "edw.sarkisyan@gmail.com")
        self.info.contrib("Some User", "some.user@mail.net")

    def build(self):
        print(f"build override")


@project.action
def build(pro: Entry):
    pro.build()
    print(f"build action")
