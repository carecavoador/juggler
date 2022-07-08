# busca_trabalhos.py
import sys
import os
from shutil import copy
from pathlib import Path
from datetime import datetime

from job import Job
from os_number import guess_os_number


ARGUMENTOS = sys.argv[1:]

DESKTOP = Path().home().joinpath("Desktop")
LAYOUTS = Path("/home/careca/Python/juggler/arquivos/layout")
PROVAS = Path("/home/careca/Python/juggler/arquivos/prova")

HOJE = datetime.today().strftime("%d-%m-%Y")
AGORA = datetime.now().strftime("%H-%M-%S")


def busca_arquivos(
    job: Job, entrada: Path, saida: Path, tipo: str, sufixo: str = ""
) -> None:
    """Tenta localizar arquivos relativos ao Job no local especificado, depois
    tenta baixar os respectivos arquivos do FTP."""

    _arquivos = [
        Path(entrada, a)
        for a in os.listdir(entrada)
        if (guess_os_number(a) == (job.os_number, job.os_version))
        and Path(entrada, a).is_file()
    ]
    if _arquivos:
        for _arquivo in _arquivos:
            _saida_arquivos = saida.joinpath(tipo) / AGORA
            _novo_arquivo = _saida_arquivos.joinpath(
                "".join([str(job), "_", tipo, sufixo, _arquivo.suffix])
            )
            if not _saida_arquivos.exists():
                os.mkdir(_saida_arquivos)
            copy(_arquivo, _novo_arquivo)

            _baixados = entrada.joinpath("Baixados")
            _arquivo_baixado = _baixados.joinpath(_arquivo.name)
            if not _baixados.exists():
                os.mkdir(_baixados)
            if not _arquivo_baixado.exists():
                copy(_arquivo, _arquivo_baixado)
                os.remove(_arquivo)

            else:
                _novo_arquivo_baixado = _baixados.joinpath(
                    _arquivo.stem + "_" + AGORA + _arquivo.suffix
                )
                copy(_arquivo, _novo_arquivo_baixado)
                os.remove(_arquivo)

    else:
        print(f"Não foi possível localizar arquivos de {tipo} para {job}.")


def main() -> None:
    """Início do programa."""

    # Cria a lista de trabalhos a serem feitos.
    jobs = [
        Job(Path(o))
        for o in ARGUMENTOS
        if (Path(o).suffix == ".pdf") and (guess_os_number(o) is not None)
    ]

    if not jobs:
        print("Sem trabalhos no momento.")
        sys.exit()

    for job in jobs:
        if job.needs_layout:
            busca_arquivos(job, LAYOUTS, DESKTOP, "Layout")
        if job.needs_proof:
            busca_arquivos(job, PROVAS, DESKTOP, "Prova Digital", sufixo=job.profile)


if __name__ == "__main__":
    main()
