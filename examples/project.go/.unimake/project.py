from umk import framework as kit
from umk.framework.adapters import go


@kit.project.entry
def entry():
    pro = kit.project.Golang()

    pro.info.id = "go-example"
    pro.info.name = "Golang Example"
    pro.info.description = "Unimake project example (golang based)"
    pro.info.version = "v1.0.0"
    pro.info.contrib("Edward Sarkisyan", "edw.sarkisyan@gmail.com")
    pro.info.contrib("Some User", "some.user@mail.net")

    build = pro.dependencies["build"]
    build.gomod(pro.layout.root, go.Go())
    build.apt_get("make", "git", sudo=True)

    return pro


@kit.project.action
def build():
    print(kit.config.boolean("with-docs"))
