#!venv\Scripts\python.exe
# busca_trabalhos.py
import sys
import os
from shutil import copy
from pathlib import Path
from datetime import datetime

from busca_trabalhos.job import Job
from busca_trabalhos.os_number import guess_os_number
from busca_trabalhos.config import carrega_config


HOJE = datetime.today().strftime("%d-%m-%Y")
AGORA = datetime.now().strftime("%H-%M-%S")

ARGUMENTOS = sys.argv[1:]


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
            _saida_arquivos = saida.joinpath(tipo)
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
        continua = input("Pressione qualquer tecla para continuar...\n> ")


def main() -> None:
    """Início do programa."""

    # Carrega arquivo de configurações.
    config = carrega_config()
    if not config:
        saida = input(
            "Sem arquivo de configuração. Pressione qualquer tecla para sair.\n > "
        )
        sys.exit()

    # Diretórios do programa.
    saida = Path(config["diretorios"]["saida"])
    layouts = Path(config["diretorios"]["layouts"]).joinpath(HOJE)
    provas = Path(config["diretorios"]["provas"]).joinpath(HOJE)

    # Cria a lista de trabalhos a serem feitos.
    jobs = [
        Job(Path(o))
        for o in ARGUMENTOS
        if (Path(o).suffix == ".pdf") and (guess_os_number(o) is not None)
    ]

    if not jobs:
        saida = input(
            "Sem trabalhos no momento. Pressione qualquer tecla para sair.\n> "
        )
        sys.exit()

    for job in jobs:
        print(f"Processando {job}...")
        if job.needs_layout:
            busca_arquivos(job, layouts, saida, "Layout")
        if job.needs_proof:
            busca_arquivos(job, provas, saida, "Prova Digital", sufixo=job.profile)


if __name__ == "__main__":
    main()
    saida = input("Programa terminado. Pressione qualquer tecla para sair.\n> ")
