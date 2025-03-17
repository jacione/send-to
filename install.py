import os
import subprocess as sub
from pathlib import Path
import importlib
import argparse

import win32com.client as wcom
from win32com.shell import shellcon, shell as winshell
import tqdm


send_to = Path(winshell.SHGetFolderPath(0, getattr(shellcon, "CSIDL_SENDTO"), None, 0))
dist = Path(__file__).resolve().parent / "dist"

scripts = [
    "diff_to_gif",
    "img_to_pdf",
    "imgs_to_gif",
    "merge_pdfs",
]


def check_file_changed(name):
    script = Path(__file__).resolve().parent / f"src/{name}.py"
    record = Path(__file__).resolve().parent / f"data/{name}.txt"
    if not record.exists():
        record.write_text(script.read_text())
        return True
    elif record.read_text() != script.read_text():
        record.write_text(script.read_text())
        return True
    else:
        return False


def main(recompile=False):
    shell = wcom.Dispatch("WScript.Shell")
    for name in tqdm.tqdm(scripts):
        mod = importlib.import_module(f"src.{name}")
        if recompile and check_file_changed(name):
            sub.run(f"pyinstaller src/{mod.INFO['name']}.py --clean --onefile",
                    stdout=sub.DEVNULL, stderr=sub.DEVNULL
                    )
        shortcut = shell.CreateShortCut(f"{send_to.as_posix()}/{mod.INFO['title']}.lnk")
        shortcut.IconLocation = f"{dist.as_posix()}/{mod.INFO['name']}.exe"
        shortcut.Targetpath = f"{dist.as_posix()}/{mod.INFO['name']}.exe"
        shortcut.save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='install.py',
        description='Installs scripts so that they are accessible from the right-click "Send to... menu',
    )
    parser.add_argument("--recompile", action='store_true')
    args = parser.parse_args()
    main(args.recompile)
