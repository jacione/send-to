import sys
from pathlib import Path

import src.utils as ut


INFO = {
    "name": Path(__file__).stem,
    "title": "Dump Contents",
}

def main(directory):
    directory = Path(directory)
    if not directory.is_dir():
        print("The given argument is not a directory.")
        return
    for f in directory.iterdir():
        print(f.name)
        f.rename(directory.parent / f.name)
    print(f"Unlinking directory '{directory.name}'")
    directory.rmdir()


if __name__ == '__main__':
    ut.print_banner(INFO['title'])
    main(sys.argv[1])
    input("Press enter to close...")
