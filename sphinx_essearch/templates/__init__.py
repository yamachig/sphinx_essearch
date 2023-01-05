from pathlib import Path


def get_dir():
    return str(Path(__file__).parent.resolve())
