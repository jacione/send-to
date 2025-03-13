import re
import unicodedata as ud
from pathlib import Path

import src.utils as ut


class Entry:
    """
    Representation of a single entry in a table of contents.
    """
    def __init__(self, section, title, page):
        self.title = title
        self.page = int(page)

        if section.lower().startswith('appendix '):
            self.appendix = True
            section = section[9:]  # Strip the 'Appendix' off of the section string
            section = section.split(".")
            # Many appendices are lettered rather than numbered.
            if ut.check_numeric(section[0]):
                pass
            for i, s in enumerate(section):
                if ut.check_numeric(s):
                    section[i] = int(s)
                else:
                    section[i] = ut.letter_to_number(s)
        else:
            self.appendix = False
            section = ut.strip_nonnumeric(section, True, True)
            section = [int(x) for x in section.split(".")]

        while len(section) < 3:
            section.append(0)
        self.chapter = section[0]
        self.section = section[1]
        self.subsection = section[2]

    def __str__(self):
        if self.appendix:
            # TODO: Handle appendices.
            return f"[UNHANDLED APPENDIX]"
        elif self.subsection:
            return f"{self.chapter}.{self.section}.{self.subsection} - {self.title} (page {self.page})"
        elif self.section:
            return f"{self.chapter}.{self.section} - {self.title} (page {self.page})"
        else:
            return f"Ch. {self.chapter} - {self.title} (page {self.page})"


class Appendix(Entry):
    def __init__(self):
        pass


def split_line(line):
    """
    Split the section and page numbers off of a line from a table of contents. Appendices are treated uniquely
    """
    section, _, title = line.partition(" ")
    if title == "":
        return "", line, ""
    if not ut.check_numeric(section):
        section = None
        title = line
    title, _, page = title.rpartition(" ")
    return section, title, page


def clean_buffer(buffer):
    """
    Remove trailing non-numerical characters from the buffer.
    """
    buffer = f"{buffer[0]} {buffer[1]} {buffer[2]}"
    return split_line(ut.strip_nonnumeric(buffer))


def identify_toc(document, verbose=False):
    """
    Takes in a pypdf.PdfReader object and scans the text to find the table of contents.
    :param document:
    :return:
    """
    print("Scanning for table of contents...")
    toc_text = []
    toc_found = False
    for i, page in enumerate(document.pages):
        # List of all lines of text on this page
        all_lines = page.extract_text().splitlines()

        # Sublist of all lines that end with a number
        cond_lines = [line for line in all_lines if bool(re.match(r"^.*\D\d", line))]

        # If more than 75% of the lines end with a number, then it's probably a TOC page
        if len(cond_lines) > 0.75 * len(all_lines):
            ut.vprint(f"ToC on page {i}!", verbose)
            if not toc_found and len(all_lines) < 10:
                # If the FIRST page that matches the pattern has fewer than 10 lines of text, it's probably just a
                # weird frontmatter page, and we should move on. (if it's not the first match, then it could be the
                # last few lines of the TOC)
                continue
            toc_text += all_lines
            toc_found = True
        # If the pattern no longer matches, then the TOC has ended. No need to scan the entire document, especially
        # since the pattern could also match with an index, references (depending on how they're formatted), and large
        # block equations
        elif toc_found:
            break
    else:
        print("No table of contents found!")

    return toc_text


def add_bookmarks_to_pdf(document, contents, save_as, verbose=False):
    print("Adding bookmarks to PDF...")
    chapter_level = [
        entry for entry in contents
        if not any([entry.section, entry.subsection, entry.appendix])
    ]
    section_level = [
        [
            entry for entry in contents
            if all([entry.chapter == chapter.chapter, entry.section, not any([entry.subsection, entry.appendix])])
        ]
        for chapter in chapter_level
    ]
    subsection_level = [
        [
            [
                entry for entry in contents
                if all([entry.chapter == chapter.chapter, entry.section == section.section, entry.subsection, not entry.appendix])
            ]
            for section in section_level[i]
            if section.chapter == chapter.chapter
        ]
        for i, chapter in enumerate(chapter_level)
    ]

    writer = ut.pdf_writer()
    writer.append(document, import_outline=False)
    try:
        for i, chapter in enumerate(chapter_level):
            ut.vprint(chapter, verbose)
            chapter_mark = writer.add_outline_item(str(chapter), chapter.page)
            for j, section in enumerate(section_level[i]):
                ut.vprint(section, verbose)
                section_mark = writer.add_outline_item(str(section), section.page, chapter_mark)
                for subsection in subsection_level[i][j]:
                    ut.vprint(subsection, verbose)
                    writer.add_outline_item(str(subsection), subsection.page, section_mark)
        writer.write(save_as)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        writer.close()


def toc_to_txt(doc_file):
    document = ut.read_pdf(doc_file)
    contents = identify_toc(document)
    text = ""
    for line in contents:
        text += f"{line}\n"
    text = ud.normalize("NFKD", text)
    toc_file = Path(f"{doc_file.parent}/{doc_file.stem}.txt")
    toc_file.write_text(text)


def toc_from_txt(doc_file, toc_file, verbose=False):
    print("Parsing table of contents...")

    doc = ut.read_pdf(doc_file)
    firstpage = 0
    chapter = 0
    section = 0
    subsection = 0

    for i, line in enumerate(toc_file.readlines()):
        heading, title, page = split_line(line)
        if title == "firstpage" and firstpage == 0:
            firstpage = page
            continue
        if title == "\n":
            chapter += 1
            section = 0
            subsection = 0
            continue
        if heading is None:
            continue
        h_split = heading.split('.')
        if len(h_split) == 1:
            pass
        # TODO UNFINISHED



if __name__ == "__main__":
    wd = Path("C:/Users/jacio/Documents/School/Textbooks/")
    p1 = wd / "Gordon Hobbs - A Formal Theory of Commonsense Psychology.pdf"
    p2 = wd / "Clyne Campbell - Testing of the Plastic Deformation of Metals.pdf"
    p3 = wd / "Asaro - Mechanics of Solids and Materials.pdf"
    p4 = wd / "Moore Davis Coplan - Building Scientific Apparatus.pdf"
    write_bookmarks(p4, verbose=True)
