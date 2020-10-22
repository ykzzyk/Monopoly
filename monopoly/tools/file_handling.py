import pathlib
from kivy.lang import Builder


def import_dir(dir: pathlib.Path):
    for child in dir.iterdir():
        if child.is_dir():
            import_dir(child)
        elif child.is_file():
            if child.suffix == '.kv':
                Builder.load_file(str(child))
