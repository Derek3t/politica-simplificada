"""Gera o zip de entrega: backend, frontend, README e o PDF de documentação (README sem as menções a docs/).

Uso: python docs/gerar_zip.py [NomeDoZip] [--com-git]
O arquivo é criado na pasta acima do projeto, para não entrar dentro de si mesmo.
Ficam de fora ambiente virtual, caches, segredos, banco local e as ferramentas que geram o PDF.
"""

import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PDF = Path("docs/Documentacao_PoliticaSimplificada.pdf")

PASTAS_DA_ENTREGA = ("backend", "frontend")
ARQUIVOS_DA_RAIZ = (".gitignore",)

PASTAS_IGNORADAS = {"venv", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache", "dist", "instance"}
ARQUIVOS_IGNORADOS = {".env", ".DS_Store"}
SUFIXOS_IGNORADOS = (".db", ".db-wal", ".db-shm", ".sqlite3", ".pyc")


def deve_ignorar(caminho):
    partes = caminho.relative_to(RAIZ).parts
    if any(parte in PASTAS_IGNORADAS or parte.endswith(".egg-info") for parte in partes):
        return True
    return caminho.name in ARQUIVOS_IGNORADOS or caminho.name.endswith(SUFIXOS_IGNORADOS)


def readme_da_entrega():
    """README sem as menções a docs/, que não vai no zip: o PDF fica na raiz."""
    texto = (RAIZ / "README.md").read_text()
    texto = texto.replace(
        "A documentação técnica fica em `docs/`.", "A documentação técnica está no PDF da raiz do projeto."
    )
    texto = "\n".join(linha for linha in texto.splitlines() if not linha.startswith("docs/ "))
    return texto.split("\n## Documentação")[0].rstrip() + "\n"


def arquivos_da_entrega():
    for pasta in PASTAS_DA_ENTREGA:
        for caminho in sorted((RAIZ / pasta).rglob("*")):
            if caminho.is_file() and not deve_ignorar(caminho):
                yield caminho, caminho.relative_to(RAIZ)
    for nome in ARQUIVOS_DA_RAIZ:
        yield RAIZ / nome, Path(nome)
    yield RAIZ / PDF, Path(PDF.name)


def gerar(nome, com_git=False):
    destino = RAIZ.parent / f"{nome}.zip"
    entregues = list(arquivos_da_entrega())
    if com_git:
        entregues += [(c, c.relative_to(RAIZ)) for c in sorted((RAIZ / ".git").rglob("*")) if c.is_file()]
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zip_:
        zip_.writestr(f"{nome}/README.md", readme_da_entrega())
        for origem, relativo in entregues:
            zip_.write(origem, Path(nome) / relativo)
    return destino, len(entregues)


if __name__ == "__main__":
    argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
    nome = argumentos[0] if argumentos else "PoliticaSimplificada"
    destino, total = gerar(nome, com_git="--com-git" in sys.argv)
    print(f"{destino} ({total} arquivos, {destino.stat().st_size / 1_000_000:.1f} MB)")
