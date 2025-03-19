import subprocess as sub
from pathlib import Path
import importlib
import winsound

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
    try:
        if record.read_text() != script.read_text():
            record.write_text(script.read_text())
            return True
        else:
            return False
    except FileNotFoundError:
        return True


def make_shortcut(title):
    return Path(f"{send_to.as_posix()}/{title}.lnk").exists()


def update_record(name):
    script = Path(__file__).resolve().parent / f"src/{name}.py"
    record = Path(__file__).resolve().parent / f"data/{name}.txt"
    record.write_text(script.read_text())


def main():
    shell = wcom.Dispatch("WScript.Shell")
    recompile = check_file_changed("utils")
    for name in tqdm.tqdm(scripts):
        mod = importlib.import_module(f"src.{name}")
        if recompile or check_file_changed(name):
            sub.run(f"pyinstaller src/{name}.py --clean --onefile",
                    stdout=sub.DEVNULL, stderr=sub.DEVNULL
                    )
            update_record(name)
        if make_shortcut(mod.INFO['title']):
            shortcut = shell.CreateShortCut(f"{send_to.as_posix()}/{mod.INFO['title']}.lnk")
            shortcut.IconLocation = f"{dist.as_posix()}/{mod.INFO['name']}.exe"
            shortcut.Targetpath = f"{dist.as_posix()}/{mod.INFO['name']}.exe"
            shortcut.save()
    update_record("utils")


if __name__ == "__main__":
    main()
    winsound.MessageBeep()
