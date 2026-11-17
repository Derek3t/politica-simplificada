"""Gera o zip de entrega sem ambiente virtual, caches, segredos e banco local.

Uso: python docs/gerar_zip.py [NomeDoZip] [--sem-git]
O arquivo é criado na pasta acima do projeto, para não entrar dentro de si mesmo.
"""

import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

PASTAS_IGNORADAS = {
    "venv",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "instance",
    ".idea",
    ".vscode",
}
ARQUIVOS_IGNORADOS = {".env", ".DS_Store", "documentacao.html"}
SUFIXOS_IGNORADOS = (".db", ".sqlite3", ".pyc", ".egg-info")


def deve_ignorar(caminho, incluir_git):
    partes = caminho.relative_to(RAIZ).parts
    if ".git" in partes and not incluir_git:
        return True
    if ".git" in partes:
        return False
    if any(parte in PASTAS_IGNORADAS or parte.endswith(".egg-info") for parte in partes):
        return True
    return caminho.name in ARQUIVOS_IGNORADOS or caminho.name.endswith(SUFIXOS_IGNORADOS)


def gerar(nome, incluir_git):
    destino = RAIZ.parent / f"{nome}.zip"
    arquivos = sorted(c for c in RAIZ.rglob("*") if c.is_file() and not deve_ignorar(c, incluir_git))
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zip_:
        for arquivo in arquivos:
            zip_.write(arquivo, Path(nome) / arquivo.relative_to(RAIZ))
    return destino, len(arquivos)


if __name__ == "__main__":
    argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
    nome = argumentos[0] if argumentos else "PoliticaSimplificada"
    destino, total = gerar(nome, incluir_git="--sem-git" not in sys.argv)
    print(f"{destino} ({total} arquivos, {destino.stat().st_size / 1_000_000:.1f} MB)")
