# pylint: disable=E1101
# pylint: disable=C0103
"""Juggler Bot. Does the hard work for you!"""
import os
from pathlib import Path
from typing import NamedTuple
from shutil import copy, move
from datetime import date, datetime

from PyPDF2 import PdfFileReader

from job import Job
from os_number import guess_os_number
from paper_sizes import PaperSheet, A4_PAPER, A3_PAPER, ROLL_PAPER
from juntapdf.juntapdf import merge_pdfs

# CONFIGS ---------------------------------------------------------------------
ROOT = Path(__file__).parent

# Jobs directory.
JOBS_DIR = Path(ROOT, r"arquivos")

# Layouts input dir and files.
LAYOUTS_DIR = Path(ROOT, r"arquivos\layouts")
LAYOUTS_DONE_DIR = Path(LAYOUTS_DIR, "Baixados")
LAYOUT_FILES = [Path(LAYOUTS_DIR, layout) for layout in os.listdir(LAYOUTS_DIR)]
LAYOUT_PAPER_SIZES = [A4_PAPER, A3_PAPER, ROLL_PAPER]

# Proofs input dir and files.
PROOFS_DIR = Path(ROOT, r"arquivos\digitais")
PROOFS_DONE_DIR = Path(PROOFS_DIR, "Baixados")
PROOF_FILES = [Path(PROOFS_DIR, digital) for digital in os.listdir(PROOFS_DIR)]

# Output dirs.
OUTPUT_DIR = Path(ROOT, r"arquivos\saida")
LAYOUTS_OUT = Path(OUTPUT_DIR, "Layouts")
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


def sort_by_size(
    printouts_list: list[Path], sizes: list[PaperSheet]
) -> list[tuple[PaperSheet, list[Path]]]:
    """Reads a list of PDF files and returns a tuple of lists with the files
    separated by paper sizes."""

    # PDF files measurements are made in points at 72dpi. This constant is the
    # needed factor to get the sizes in milimeters.
    pdf_res_to_mm = 72.0 / 25.4

    separated_layouts = []

    for printout in printouts_list:
        for paper_size in sizes:
            with open(printout, "rb") as file:
                reader = PdfFileReader(file)
                page = reader.pages[0]
                width = round(float(page.mediabox.width) / pdf_res_to_mm)
                height = round(float(page.mediabox.height) / pdf_res_to_mm)

                # Goes into an A4 sheet.
                if (width <= paper_size.width and height <= paper_size.height) or (
                    width <= paper_size.height and height <= paper_size.width
                ):
                    separated_layouts.append((paper_size, printout))
                    break

    return separated_layouts


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


def download_files(job: Job, source: list[Path], output: Path, done_dir: Path) -> None:
    """Retrieves Job files to output destination and copies done files to done_dir."""

    if not done_dir.exists():
        os.mkdir(done_dir)

    if not output.exists():
        os.mkdir(output)

    files_to_download = [
        file
        for file in source
        if guess_os_number(file.name) == (job.os_number, job.os_version)
    ]

    for file in files_to_download:

        # Checks if file was already downloaded.
        # If file was not already downloaded, copies it to done_dir.
        file_done = done_dir.joinpath(file.name)
        if not file_done.exists():
            copy(file, file_done)

        # If file WAS already downloaded than prompts user to download again.
        else:
            download_again = prompt_user(
                f"O arquivo {file_done.name} já foi baixado. Deseja Baixá-lo novamente?"
            )
            if download_again:
                file_done = done_dir.joinpath(file_done.stem + NOW + file_done.suffix)
                copy(file, file_done)
                print(f"Arquivo salvo como {file_done}.")
            else:
                files_to_download.pop(file)
                continue

        # Checks if file is not already in the output directory and copies it.
        downloaded_file = output.joinpath(file.name)
        if not downloaded_file.exists():
            copy(file, downloaded_file)

        # If file was already in the output directory prompts user to overwrite it.
        else:
            overwrite = prompt_user(
                f"O arquivo {downloaded_file} já existe. Deseja substituí-lo?"
            )
            if overwrite:
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

    return files_to_download


def work() -> None:
    """Program starts."""

    # Creates Jobs list.
    jobs_todo = [
        Job(Path(JOBS_DIR, file))
        for file in [Path(f) for f in os.listdir(JOBS_DIR)]
        if guess_os_number(file.name) is not None
    ]

    if not jobs_todo:
        print("Sem trabalhos no momento.")
        exit()

    # Looks for Jobs' files in Layouts directory and Proofs directory and downloads if any.
    for current_job in jobs_todo:
        if current_job.needs_layout:
            layout_files = download_files(
                current_job, LAYOUT_FILES, LAYOUTS_OUT, LAYOUTS_DONE_DIR
            )
            if layout_files:
                print(
                    f"{len(layout_files)} arquivos carregados com sucesso para {current_job}."
                )
            else:
                print(
                    f"Não foi possível localizar arquivos de print Layout para {current_job}."
                )

        if current_job.needs_proof:
            proof_files = download_files(
                current_job, PROOF_FILES, PROOFS_OUT, PROOFS_DONE_DIR
            )
            if proof_files:
                print(
                    f"{len(proof_files)} arquivos carregados com sucesso para {current_job}."
                )
            else:
                print(
                    f"Não foi possível localizar arquivos de print Layout para {current_job}."
                )

    # Organize layouts by size.
    pdf_layouts = [
        Path(LAYOUTS_OUT, layout)
        for layout in os.listdir(LAYOUTS_OUT)
        if Path(layout).suffix.lower() == ".pdf"
    ]

    layouts_by_size = sort_by_size(pdf_layouts, LAYOUT_PAPER_SIZES)

    for paper_size in LAYOUT_PAPER_SIZES:

        size_path = Path(LAYOUTS_OUT, paper_size.size)

        if not size_path.exists():
            os.mkdir(size_path)

        layouts = [
            layout[1] for layout in layouts_by_size if layout[0].size == paper_size.size
        ]
        merge_pdfs(layouts, LAYOUTS_OUT.joinpath(f"Layouts {paper_size.size}.pdf"))

        for layout in layouts:
            move(layout, size_path.joinpath(layout.name))


if __name__ == "__main__":
    work()
