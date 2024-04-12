import os

if not os.environ.get('_UMK_COMPLETE', None):
    from rich.table import Table
    from umk import core


    class PropertiesPrinter:
        def print(self, *entries: core.Properties, name=True, description=True, value=True, splitter=" ", equal="="):
            for properties in entries:
                table = Table(show_header=True, show_edge=True, show_lines=True)
                if name:
                    table.add_column("Name", justify="left", style="", no_wrap=True)
                if description:
                    table.add_column("Description", justify="left", style="italic", no_wrap=True)
                if value:
                    table.add_column("Value", justify="left", style="", no_wrap=True)
                for item in properties:
                    if isinstance(item.value, list):
                        val = splitter.join(item.value)
                    elif isinstance(item.value, dict):
                        val = "\n".join([f"{k}{equal}{v}" for k, v in item.value.items()])
                    else:
                        val = str(item.value)
                    row = []
                    if name:
                        row.append(item.name)
                    if description:
                        row.append(item.description or "<empty>")
                    if value:
                        row.append(val)
                    table.add_row(*row)
                core.globals.console.print(table)
