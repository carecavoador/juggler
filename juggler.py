# pylint: disable=E1101
# pylint: disable=C0103
"""Juggler Bot. Does the hard work for you!"""
import os
from pathlib import Path
from typing import NamedTuple
from shutil import copy
from datetime import date, datetime

from PyPDF2 import PdfFileReader

from job import Job
from osnumber import guess_os_number
from paper_sizes import A4_PAPER, A3_PAPER

# CONFIGS ---------------------------------------------------------------------
# Jobs directory.
JOBS_DIR = Path(r"C:\Projetos\Python\juggler\arquivos")

# Layouts input dir and files.
LAYOUTS_DIR = Path(r"C:\Projetos\Python\juggler\arquivos\layouts")
LAYOUTS_DONE_DIR = Path(LAYOUTS_DIR, "Baixados")
LAYOUT_FILES = [Path(LAYOUTS_DIR, layout) for layout in os.listdir(LAYOUTS_DIR)]

# Proofs input dir and files.
PROOFS_DIR = Path(r"C:\Projetos\Python\juggler\arquivos\digitais")
PROOFS_DONE_DIR = Path(PROOFS_DIR, "Baixados")
PROOF_FILES = [Path(PROOFS_DIR, digital) for digital in os.listdir(PROOFS_DIR)]

# Output dirs.
OUTPUT_DIR = Path(r"C:\Projetos\Python\juggler\saida")
A4_LAYOUTS_OUT = Path(OUTPUT_DIR, "A4")
A3_LAYOUTS_OUT = Path(OUTPUT_DIR, "A3")
ROLL_LAYOUTS_OUT = Path(OUTPUT_DIR, "Rolo")
PROOFS_OUT = Path(OUTPUT_DIR, "Provas Digitais")

# Formated current date and time.
TODAY = date.today().strftime("%d-%m-%Y")
NOW = datetime.now().strftime("_%H-%M-%S")
# -----------------------------------------------------------------------------


class LayoutSizes(NamedTuple):
    """Printouts separated by sizes."""

    a4: list
    a3: list
    roll: list


def separate_by_paper_size(printouts_list: list[Path]) -> LayoutSizes:
    """Reads a list of PDF files and returns a tuple of lists with the files
    separated by paper sizes."""

    # PDF files measurements are made in points at 72dpi. This constant is the
    # needed factor to get the sizes in milimeters.
    pdf_res_to_cm = 72.0 / 25.4

    a4_files = []
    a3_files = []
    roll_files = []

    for printout in printouts_list:
        with open(printout, "rb") as file:
            reader = PdfFileReader(file)
            page = reader.pages[0]
            width = round(float(page.mediabox.width) / pdf_res_to_cm)
            height = round(float(page.mediabox.height) / pdf_res_to_cm)

            # Goes into an A4 sheet.
            if (
                width <= A4_PAPER.width
                and height <= A4_PAPER.height
                or width <= A4_PAPER.height
                and height <= A4_PAPER.width
            ):
                a4_files.append(printout)

            # Goes into an A3 sheet.
            elif (
                width <= A3_PAPER.width
                and height <= A3_PAPER.height
                or width <= A3_PAPER.height
                and height <= A3_PAPER.width
            ):
                a3_files.append(printout)

            # Bigger than A3, must go into a Roll print.
            else:
                roll_files.append(printout)

    return LayoutSizes(a4=a4_files, a3=a3_files, roll=roll_files)


def prompt_user(prompt: str) -> bool:
    """Prompts user the given prompt and returns True or False."""

    ok = ["s", "sim"]
    not_ok = ["n", "nao", "não"]

    while True:
        print(prompt)
        choice = input("Sim ou Não?\n> ").lower()
        if choice in ok:
            return True
        elif choice in not_ok:
            return False
        else:
            print("Opção inválida.")


def retrieve_job_files(job_files: list[Path], output: Path, done_dir: Path) -> None:
    """Retrieves Job files to output destination and copies done files to done_dir."""

    if not done_dir.exists():
        os.mkdir(done_dir)

    if not output.exists():
        os.mkdir(output)

    for file in job_files:

        # Checks if file was already downloaded.
        file_done = done_dir.joinpath(file.name)
        if not file_done.exists():
            copy(file, done_dir)

        # If file was not already downloaded, copies it to done_dir.
        else:
            download_again = prompt_user(
                f"O arquivo {file_done.name} já foi baixado. Deseja Baixá-lo novamente?"
            )
            if download_again:
                file_done = done_dir.joinpath(file_done.stem + NOW + file_done.suffix)
                copy(file, file_done)
                print(f"Arquivo salvo como {file_done}.")
            else:
                continue

        # Checks if file is already in the output directory.
        downloaded_file = output.joinpath(file.name)
        if not downloaded_file.exists():
            copy(file, downloaded_file)
        else:
            ovewrite = prompt_user(
                f"O arquivo {downloaded_file} já existe. Deseja substituí-lo?"
            )
            if ovewrite:
                copy(file, downloaded_file)
                print(f"Arquivo {downloaded_file} substituído.")
            else:
                downloaded_file = downloaded_file.parent.joinpath(
                    downloaded_file.stem + NOW + downloaded_file.suffix
                )
                copy(file, downloaded_file)
                print(f"Arquivo salvo como {downloaded_file}.")

        # Delete file after all done.
        os.remove(file)


def work() -> None:
    """Program starts."""

    # Creates Jobs list.
    jobs_list = [
        Job(Path(JOBS_DIR, file))
        for file in [Path(f) for f in os.listdir(JOBS_DIR)]
        if guess_os_number(file.name) is not None
    ]

    jobs_layout_files = []
    jobs_proof_files = []

    # Looks for Jobs' files in Layouts directory and Proofs directory.
    for current_job in jobs_list:
        if current_job.needs_layout:
            jobs_layout_files.extend(
                [
                    layout
                    for layout in LAYOUT_FILES
                    if guess_os_number(layout.name)
                    == (current_job.os_number, current_job.os_version)
                ]
            )
        if current_job.needs_proof:
            jobs_proof_files.extend(
                [
                    proof
                    for proof in PROOF_FILES
                    if guess_os_number(proof.name)
                    == (current_job.os_number, current_job.os_version)
                ]
            )

    # Processes found Layouts files.
    if jobs_layout_files:
        a4_sheet, a3_sheet, roll_paper = separate_by_paper_size(jobs_layout_files)

        # Junta PDFs A4 e copia na pasta correspondente.
        if a4_sheet:
            retrieve_job_files(a4_sheet, A4_LAYOUTS_OUT, LAYOUTS_DONE_DIR)

        if a3_sheet:
            retrieve_job_files(a3_sheet, A3_LAYOUTS_OUT, LAYOUTS_DONE_DIR)

        if roll_paper:
            retrieve_job_files(roll_paper, ROLL_LAYOUTS_OUT, LAYOUTS_DONE_DIR)

    if jobs_proof_files:
        retrieve_job_files(jobs_proof_files, PROOFS_OUT, PROOFS_DONE_DIR)


if __name__ == "__main__":
    work()
