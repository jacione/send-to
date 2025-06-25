import sys
from pathlib import Path

import src.utils as ut


INFO = {
    "name": Path(__file__).stem,
    "title": "New Directory",
}

def main(*filepaths):
    filepaths = [Path(f) for f in filepaths]
    parent = filepaths[0].parent
    if not all([f.parent == parent for f in filepaths]):
        raise ValueError('Files must be in the same directory')
    new_dir = parent

    while new_dir.exists():
        print('Directory already exists')
        new_dir = parent / ut.smart_input("New directory: ", default="new_directory")
    new_dir.mkdir()

    print(f"Moving selected files into {new_dir}...")
    for f in filepaths:
        print(f.name)
        f.rename(new_dir / f.name)


if __name__ == '__main__':
    ut.print_banner(INFO['title'])
    main(*sys.argv[1:])
    input("Press enter to close...")
