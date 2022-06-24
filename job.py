"""Classe para tratar de objetos Job e seus métodos."""
from pathlib import Path
from osnumber import guess_os_number


class Job:
    """Job object to store the job information and related files location."""

    def __init__(self, pdf_file: Path) -> None:
        self._pdf: pdf_file
        self.os_number, self.os_version = guess_os_number(pdf_file.name)
        self.profile: str = ""
        self.needs_layout: bool = False
        self.needs_proof: bool = False

    def __repr__(self) -> str:
        return f"OS {self.os_number} v{self.os_version}"


def main():
    """Main function just for testing purposes."""
    files = [
        Path(r"E:\python\juggler\200_210.pdf"),
        Path(r"E:\python\juggler\OS_498677_3_V3.pdf"),
    ]
    jobs = [Job(file) for file in files if guess_os_number(file.name) is not None]
    print(jobs)


if __name__ == "__main__":
    main()
