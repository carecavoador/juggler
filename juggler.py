# pylint: disable=E1101
# pylint: disable=C0103
"""Juggler Bot. Does the hard work for you!"""
import os
import json

from pathlib import Path
from shutil import copy, move
from datetime import date, datetime

from PyPDF2 import PdfFileReader

from job import Job
from os_number import guess_os_number
from paper_sizes import PaperSheet, A4_PAPER, A3_PAPER, ROLL_PAPER
from juntapdf.juntapdf import merge_pdfs


# CONFIGS ---------------------------------------------------------------------
CONFIG = json.load(open("config.json", "r", encoding="utf-8"))

# Directories.
ROOT = Path(__file__).parent
CONFIG_DIRS = CONFIG["directories"]
# Jobs directory.
JOBS_DIR = Path(CONFIG_DIRS["jobs"])
# Layouts directories.
LAYOUTS_DIR = Path(CONFIG_DIRS["layouts-in"])
LAYOUTS_DONE_DIR = Path(LAYOUTS_DIR, "Baixados")
# Proofs directories.
PROOFS_DIR = Path(CONFIG_DIRS["proofs-in"])
PROOFS_DONE_DIR = Path(PROOFS_DIR, "Baixados")
# Output directories.
LAYOUTS_OUT = Path(CONFIG_DIRS["layouts-out"])
PROOFS_OUT = Path(CONFIG_DIRS["proofs-out"])

# Layout paper sizes.
LAYOUT_SIZES = CONFIG["layout-sizes"]

# Formated current date and time.
TODAY = date.today().strftime("%d-%m-%Y")
NOW = datetime.now().strftime("_%H-%M-%S")
# -----------------------------------------------------------------------------


def sort_by_size(
    printouts_list: list[Path], paper_sizes: dict
) -> list[tuple[str, list[Path]]]:
    """Reads a list of PDF files and returns a tuple of lists with the files
    separated by paper sizes."""

    # PDF files measurements are made in points at 72dpi. This constant is the
    # needed factor to get the sizes in milimeters.
    pdf_res_to_mm = 72.0 / 25.4

    separated_layouts = []

    for printout in printouts_list:
        for size in paper_sizes.keys():
            with open(printout, "rb") as file:
                reader = PdfFileReader(file)
                page = reader.pages[0]
                width = round(float(page.mediabox.width) / pdf_res_to_mm)
                height = round(float(page.mediabox.height) / pdf_res_to_mm)

                # Goes into an A4 sheet.
                if (
                    width <= paper_sizes[size]["width"]
                    and height <= paper_sizes[size]["height"]
                ) or (
                    width <= paper_sizes[size]["height"]
                    and height <= paper_sizes[size]["width"]
                ):
                    separated_layouts.append((size, printout))
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


def download_files(files_to_download: list[Path], output: Path, done_dir: Path) -> None:
    """Retrieves Job files to output destination and copies done files to done_dir."""

    if not done_dir.exists():
        os.mkdir(done_dir)

    if not output.exists():
        os.mkdir(output)

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
                files_to_download.pop(files_to_download.index(file))
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
            job_layout_files = [
                Path(LAYOUTS_DIR, file)
                for file in os.listdir(LAYOUTS_DIR)
                if guess_os_number(file)
                == (current_job.os_number, current_job.os_version)
            ]
            if job_layout_files:
                layouts_downloaded = download_files(
                    job_layout_files, LAYOUTS_OUT, LAYOUTS_DONE_DIR
                )
                print(
                    f"{len(layouts_downloaded)} arquivos de Print Layout carregados com sucesso para {current_job}."
                )
            else:
                print(
                    f"Não foi possível localizar arquivos de Print Layout para {current_job}."
                )

        if current_job.needs_proof:
            job_proof_files = [
                Path(PROOFS_DIR, file)
                for file in os.listdir(PROOFS_DIR)
                if guess_os_number(file)
                == (current_job.os_number, current_job.os_version)
            ]
            if job_proof_files:
                proofs_downloaded = download_files(
                    job_proof_files, PROOFS_OUT, PROOFS_DONE_DIR
                )
                print(
                    f"{len(proofs_downloaded)} arquivos de Prova Digital carregados com sucesso para {current_job}."
                )
            else:
                print(
                    f"Não foi possível localizar arquivos de Prova Digital para {current_job}."
                )

    # Organize layouts by size.
    pdf_layouts = [
        Path(LAYOUTS_OUT, layout)
        for layout in os.listdir(LAYOUTS_OUT)
        if Path(layout).suffix.lower() == ".pdf"
    ]

    if pdf_layouts:

        layouts_by_size = sort_by_size(pdf_layouts, LAYOUT_SIZES)

        for size in LAYOUT_SIZES.keys():

            size_path = Path(LAYOUTS_OUT, size)

            if not size_path.exists():
                os.mkdir(size_path)

            layouts = [layout[1] for layout in layouts_by_size if layout[0] == size]

            if layouts:
                merge_pdfs(layouts, LAYOUTS_OUT.joinpath(f"Layouts {size}.pdf"))

            for layout in layouts:
                move(layout, size_path.joinpath(layout.name))


if __name__ == "__main__":
    work()
