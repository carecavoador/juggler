"""Classe para tratar de objetos Job e seus métodos."""
import re
from pathlib import Path


class Job:
    """Job object to store the job information and related files location."""

    def __init__(self, pdf_file: Path) -> None:
        self._pdf: pdf_file
        self.os_number, self.os_version = self.guess_os_number(pdf_file.name)
        self.needs_layout: bool = False
        self.needs_proof: bool = False
        self.files: list[Path] = []

    def __repr__(self) -> str:
        return f"OS {self.os_number} v{self.os_version}"

    def guess_os_number(self, filename: str) -> tuple[int, int]:
        """Tries to guess the OS Number and Version from a given string."""

        RE_OS = r"(\d{4,}).*[vV](\d+)"
        _os_number = re.search(RE_OS, filename)
        if _os_number:
            os_number = _os_number.group(1)
            os_version = _os_number.group(2)
            return (os_number, os_version)
        else:
            return (None, None)


def main():
    """Main function just for testing purposes."""
    files = [
        Path(r"E:\python\juggler\200_210.pdf"),
        Path(r"E:\python\juggler\OS_498677_3_V3.pdf"),
    ]
    jobs = [Job(f) for f in files if Job(f).os_number is not None]
    print(jobs)


if __name__ == "__main__":
    main()
