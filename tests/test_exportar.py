"""Testes do exportador, com CSVs sintéticos (sem rede, sem o projeto de origem)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import exportar  # noqa: E402


def _csv(caminho: Path, linhas: list[tuple[str, str]]) -> None:
    caminho.write_text("data,agio,agio_pct,n_fontes\n" +
                       "".join(f"{d},0,{v},2\n" for d, v in linhas), encoding="utf-8")


def _origem(tmp_path: Path) -> Path:
    tratado = tmp_path / "agio-stablecoin" / "dados" / "tratado"
    tratado.mkdir(parents=True)
    _csv(tratado / "agio_diario.csv",
         [("2025-04-08", "0.30"), ("2025-04-09", "-0.04"), ("2025-04-10", "0.25")])
    _csv(tratado / "agio_fechamento_diario.csv",
         [("2025-04-08", "0.35"), ("2025-04-09", "-3.51"), ("2025-04-11", "0.20")])
    return tmp_path / "agio-stablecoin"


def test_json_tem_as_duas_medidas_e_uniao_das_datas(tmp_path):
    saida = tmp_path / "agio.json"
    exportar.main(["--origem", str(_origem(tmp_path)), "--saida", str(saida)])
    d = json.loads(saida.read_text(encoding="utf-8"))
    assert [p["d"] for p in d["serie"]] == ["2025-04-08", "2025-04-09", "2025-04-10", "2025-04-11"]
    assert d["serie"][2] == {"d": "2025-04-10", "j": 0.25, "f": None}
    assert d["ultima_data"] == "2025-04-11" and d["dias"] == 4


def test_maior_divergencia_vem_primeiro(tmp_path):
    saida = tmp_path / "agio.json"
    exportar.main(["--origem", str(_origem(tmp_path)), "--saida", str(saida)])
    div = json.loads(saida.read_text(encoding="utf-8"))["divergencias"]
    assert div[0]["d"] == "2025-04-09"
    assert div[0]["dif"] == -3.47
    assert len(div) == 2  # só dias com as duas medidas


def test_nao_publica_precos_brutos(tmp_path):
    saida = tmp_path / "agio.json"
    exportar.main(["--origem", str(_origem(tmp_path)), "--saida", str(saida)])
    d = json.loads(saida.read_text(encoding="utf-8"))
    chaves = {k for p in d["serie"] for k in p}
    assert chaves == {"d", "j", "f"}


def test_ignora_linhas_vazias(tmp_path):
    caminho = tmp_path / "x.csv"
    caminho.write_text("data,agio_pct\n2025-01-02,\n2025-01-03,abc\n2025-01-06,0.1\n", encoding="utf-8")
    assert exportar.ler_serie(caminho) == {"2025-01-06": 0.1}


def test_origem_ausente_avisa(tmp_path):
    import pytest
    with pytest.raises(SystemExit) as e:
        exportar.main(["--origem", str(tmp_path / "nada"), "--saida", str(tmp_path / "a.json")])
    assert "agio calcular" in str(e.value)
