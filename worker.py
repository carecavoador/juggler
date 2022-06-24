import re


def guess_os_number(filename: str, pattern: str) -> tuple[int, int]:
    """Tries to guess the OS Number and Version from a given string."""

    _os_number = re.search(pattern, filename)
    if _os_number:
        os_number = _os_number.group(1)
        os_version = _os_number.group(2)
        return (os_number, os_version)
    else:
        return (None, None)
