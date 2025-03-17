import sys
from pathlib import Path

import img2pdf

import src.utils as ut


INFO = {
    "name": Path(__file__).stem,
    "title": "Image(s) to PDF",
}


def main(image_files):
    ut.print_banner(INFO["title"])
    print("Images:")
    for img in image_files:
        print(f"\t{img}")
        parent = img.parent.as_posix()
        name = img.stem
        with open(f"{parent}/{name}.pdf", "wb") as f:
            f.write(img2pdf.convert(f"{img.as_posix()}"))


if __name__ == "__main__":
    main([Path(img) for img in sys.argv[1:]])
    input("Press enter to close...")
