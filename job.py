# pylint: disable=E1101
"""Classe para tratar de objetos Job e seus métodos."""
from re import search
from pathlib import Path
from PyPDF2 import PdfReader

<<<<<<< HEAD
from os_number import guess_os_number
=======

def guess_os_number(filename: str) -> tuple[int, int]:
    """Tries to guess the OS Number and Version from a given string."""

    os_pattern = r"(\d{4,}).*[vV](\d+)"  # regex to match OS Number and Version
    _os_number = re.search(os_pattern, filename)
    if _os_number:
        os_number = _os_number.group(1)
        os_version = _os_number.group(2)
        return (os_number, os_version)
>>>>>>> 67738f645dca50b1bdcab6335ecc21b6b1af951e


class Job:
    """Job object to store the job information and related files location."""

    def __init__(self, pdf_file: Path) -> None:
        self._pdf: pdf_file
        self.os_number, self.os_version = guess_os_number(pdf_file.name)
        self.profile: str = ""
        self.needs_layout: bool = False
        self.needs_proof: bool = False
        self.layout_files: list = []
        self.proof_files: list = []
        self.read_job_data_from_pdf(pdf_file)

    def __repr__(self) -> str:
        return f"OS {self.os_number} v{self.os_version}"

    def __str__(self) -> str:
        return f"OS_{self.os_number}_v{self.os_version}"

    def read_job_data_from_pdf(self, _pdf: Path) -> None:
        """Reads a PDF file and extract it's text to look for the job
        information."""

        with open(_pdf, "rb") as f:
            reader = PdfReader(f)
            page_one = reader.pages[0]
            text = page_one.extract_text().split("\n")

        for line in text:
            if line == text[14]:
                self.profile = "_Perfil_"
                self.profile += search("(.+)Fechamento:", line).groups(1)[0]
            elif line.startswith("Print Layout"):
                self.needs_layout = True
            elif line.startswith("Prova Digital"):
                self.needs_proof = True
