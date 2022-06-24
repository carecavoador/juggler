from pathlib import Path
from job import Job


class Worker:
    """Worker object gets a Job list to do."""

    def __init__(self, jobs: list[Job], source_dir: Path, output_dir: Path):
        self.jobs = jobs
        self.source_dir = source_dir
        self.output_dir = output_dir
