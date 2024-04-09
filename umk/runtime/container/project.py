import inspect

from umk import framework, core
from umk.framework.project import Project as BaseProject


class Project:
    def __init__(self):
        self.object: BaseProject = None
        self.actions: dict[str, framework.project.Action] = {}
        self.config = None

    def run(self, name: str):
        action = self.actions.get(name)
        if not action:
            # TODO Create error for this situation
            raise ValueError()
        sig = len(inspect.signature(action).parameters)
        if sig == 0:
            action()
        elif sig == 1:
            action(self.object)
        else:
            action(self.object, self.config)

    def action(self, func=None, *, name: str = ""):
        # Without 'name'
        if func is not None:
            self.actions[func.__name__] = func
            return func

        def decorator(fu):
            # With 'name'
            self.actions[name] = fu
            return fu

        return decorator

    def entry(self, factory):
        self.object = factory()

        # TODO Validate func result type and value

        def release():
            """
            Release project
            """
            self.object.release()
        self.actions["release"] = release

        return factory

    def implement(self):
        @core.overload
        def act(func): ...

        @core.overload
        def act(*, name: str = ""): ...

        def act(func=None, *, name: str = ""): return self.action(func, name=name)

        framework.project.action = act
        framework.project.get = lambda: self.object
        framework.project.run = lambda name: self.run(name)
        framework.project.entry = lambda factory: self.entry(factory)

