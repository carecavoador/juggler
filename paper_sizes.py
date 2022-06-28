"""Paper class and paper sizes objects."""
from typing import NamedTuple


class PaperSheet(NamedTuple):
    """Paper sheet sizes."""

    size: str
    width: int
    height: int

    def __repr__(self) -> str:
        return self.size

    def __str__(self) -> str:
        return self.size


# Paper sizes.
A4_PAPER = PaperSheet(size="A4", width=210, height=297)
A3_PAPER = PaperSheet(size="A3", width=297, height=420)
ROLL_PAPER = PaperSheet(size="Rolo", width=914, height=600)


# def separate_by_paper_size(
#     printouts_list: list[Path], sizes: list[PaperSheet]
# ) -> list[tuple(PaperSheet, list[Path])]:
#     """Reads a list of PDF files and returns a tuple of lists with the files
#     separated by paper sizes."""

#     # PDF files measurements are made in points at 72dpi. This constant is the
#     # needed factor to get the sizes in milimeters.
#     pdf_res_to_cm = 72.0 / 25.4

#     a4_files = []
#     a3_files = []
#     roll_files = []

#     for printout in printouts_list:
#         with open(printout, "rb") as file:
#             reader = PdfFileReader(file)
#             page = reader.pages[0]
#             width = round(float(page.mediabox.width) / pdf_res_to_cm)
#             height = round(float(page.mediabox.height) / pdf_res_to_cm)

#             # Goes into an A4 sheet.
#             if (
#                 width <= A4_PAPER.width
#                 and height <= A4_PAPER.height
#                 or width <= A4_PAPER.height
#                 and height <= A4_PAPER.width
#             ):
#                 a4_files.append(printout)

#             # Goes into an A3 sheet.
#             elif (
#                 width <= A3_PAPER.width
#                 and height <= A3_PAPER.height
#                 or width <= A3_PAPER.height
#                 and height <= A3_PAPER.width
#             ):
#                 a3_files.append(printout)

#             # Bigger than A3, must go into a Roll print.
#             else:
#                 roll_files.append(printout)

#     return LayoutSizes(a4=a4_files, a3=a3_files, roll=roll_files)
