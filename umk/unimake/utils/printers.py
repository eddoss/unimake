from rich.table import Table

from umk import core


class PropertiesPrinter:
    def print(self, *entries: core.Properties, name=True, description=True, splitter=" ", equal="="):
        for properties in entries:
            table = Table(show_header=True, show_edge=True, show_lines=True)
            if name:
                table.add_column("Name", justify="left", style="", no_wrap=True)
            if description:
                table.add_column("Description", justify="left", style="", no_wrap=True)
            table.add_column("Value", justify="left", style="", no_wrap=True)
            for item in properties:
                if isinstance(item.value, list):
                    value = splitter.join(item.value)
                elif isinstance(item.value, dict):
                    value = "\n".join([f"{k}{equal}{v}" for k, v in item.value.items()])
                else:
                    value = str(item.value)
                if not name and not description:
                    row = (value, )
                elif not name:
                    row = (item.description, value)
                elif not description:
                    row = (item.name, value)
                else:
                    row = (item.name, item.description, value)
                table.add_row(*row)
            core.globals.console.print(table)
