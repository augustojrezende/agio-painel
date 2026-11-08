#!/usr/bin/env python3
"""Exporta a série do ágio do projeto agio-stablecoin para o painel.

Lê dois arquivos que o comando `agio calcular` já grava e não altera nada
no projeto de origem (a versão congelada para a validação fica intacta):

    <origem>/dados/tratado/agio_diario.csv            ágio na janela da PTAX (10h-13h)
    <origem>/dados/tratado/agio_fechamento_diario.csv ágio no fechamento (00:00 UTC, 21h)

Grava `dados/agio.json` neste repositório, só com o ágio diário em %
(nenhum preço bruto das corretoras). Usa apenas a biblioteca padrão.

Uso:
    python3 scripts/exportar.py                  # só gera o JSON
    python3 scripts/exportar.py --publicar       # gera, faz commit e push se mudou
    python3 scripts/exportar.py --origem ~/Projetos/agio-stablecoin

Por padrão, a origem é a pasta `agio-stablecoin` ao lado desta.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEM_PADRAO = RAIZ.parent / "agio-stablecoin"
SAIDA = RAIZ / "dados" / "agio.json"
N_DIVERGENCIAS = 10   # dias com maior diferença entre as duas medidas
CASAS = 4             # casas decimais do ágio em %


def ler_serie(caminho: Path) -> dict[str, float]:
    """Lê `data,agio_pct` de um CSV do projeto; ignora linhas sem valor."""
    serie: dict[str, float] = {}
    with caminho.open(encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            valor = (linha.get("agio_pct") or "").strip()
            data = (linha.get("data") or "").strip()[:10]
            if not data or not valor:
                continue
            try:
                serie[data] = round(float(valor), CASAS)
            except ValueError:
                continue
    return serie


def montar(janela: dict[str, float], fechamento: dict[str, float]) -> dict:
    datas = sorted(set(janela) | set(fechamento))
    if not datas:
        raise ValueError("Nenhum dia com ágio nos arquivos de origem.")
    serie = [{"d": d, "j": janela.get(d), "f": fechamento.get(d)} for d in datas]

    ambos = [p for p in serie if p["j"] is not None and p["f"] is not None]
    ambos.sort(key=lambda p: abs(p["f"] - p["j"]), reverse=True)
    divergencias = [
        {"d": p["d"], "j": p["j"], "f": p["f"], "dif": round(p["f"] - p["j"], CASAS)}
        for p in ambos[:N_DIVERGENCIAS]
    ]

    return {
        "fonte": "https://github.com/augustojrezende/agio-stablecoin",
        "gerado_em": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ultima_data": datas[-1],
        "dias": len(datas),
        "serie": serie,
        "divergencias": divergencias,
    }


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(RAIZ), *args], capture_output=True, text=True)


def publicar(ultima_data: str) -> None:
    git("add", "dados/agio.json")
    if git("diff", "--cached", "--quiet").returncode == 0:
        print("Sem mudança no JSON; nada a publicar.")
        return
    msg = f"Atualiza a série até {ultima_data}"
    r = git("commit", "-m", msg)
    if r.returncode != 0:
        sys.exit(f"Falha no commit:\n{r.stderr}")
    r = git("push")
    if r.returncode != 0:
        sys.exit(f"Commit feito, mas o push falhou:\n{r.stderr}")
    print(f"Publicado: {msg}")


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--origem", type=Path, default=ORIGEM_PADRAO,
                   help="pasta do projeto agio-stablecoin")
    p.add_argument("--saida", type=Path, default=SAIDA)
    p.add_argument("--publicar", action="store_true", help="commit e push se o JSON mudou")
    a = p.parse_args(argv)

    tratado = a.origem.expanduser() / "dados" / "tratado"
    try:
        janela = ler_serie(tratado / "agio_diario.csv")
        fechamento = ler_serie(tratado / "agio_fechamento_diario.csv")
    except FileNotFoundError as e:
        sys.exit(f"Arquivo não encontrado: {e.filename}\nRode `agio calcular` no projeto de origem.")

    dados = montar(janela, fechamento)
    a.saida.parent.mkdir(parents=True, exist_ok=True)
    a.saida.write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")) + "\n",
                       encoding="utf-8")
    print(f"{a.saida.name}: {dados['dias']} dias, último {dados['ultima_data']}.")
    if a.publicar:
        publicar(dados["ultima_data"])


if __name__ == "__main__":
    main()
