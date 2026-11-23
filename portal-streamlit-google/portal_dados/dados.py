"""Geração e filtragem de registros totalmente fictícios."""

from __future__ import annotations

from datetime import date, timedelta
from random import Random

import pandas as pd


VISITAS = ["V0", "V1", "V2", "V3", "V4"]
STATUS = ["Realizado", "Aguardando", "Não realizado", "Verificar"]
GRUPOS = ["Proven", "TeleProven", "Controle"]
CENTROS = [
    "Centro Norte",
    "Centro Sul",
    "Centro Leste",
    "Centro Oeste",
    "Centro Central",
    "Centro Interior",
]


def gerar_dados_ficticios(quantidade: int = 620) -> pd.DataFrame:
    """Cria dados demonstrativos reprodutíveis, sem pacientes ou organizações reais."""
    rng = Random(20261117)
    inicio = date(2025, 1, 1)
    registros = []

    for indice in range(1, quantidade + 1):
        visita = rng.choice(VISITAS)
        status = rng.choices(STATUS, weights=[62, 19, 11, 8], k=1)[0]
        registros.append(
            {
                "Registro": f"DEMO-{indice:05d}",
                "Centro": rng.choice(CENTROS),
                "Grupo": rng.choice(GRUPOS),
                "Visita": visita,
                "Status": status,
                "Data prevista": inicio + timedelta(days=rng.randrange(650)),
                "Completude (%)": rng.randint(75, 100)
                if status == "Realizado"
                else rng.randint(10, 74),
            }
        )

    return pd.DataFrame.from_records(registros)


def filtrar_dados(
    dados: pd.DataFrame,
    centros: list[str],
    grupos: list[str],
    visitas: list[str],
    status: list[str],
    data_inicio: date,
    data_fim: date,
    busca: str = "",
) -> pd.DataFrame:
    """Aplica filtros combinados. Seleção vazia significa nenhum resultado."""
    mascara = (
        dados["v_1"].isin(centros)
        # & dados["Grupo"].isin(grupos)
        # & dados["Visita"].isin(visitas)
        # & dados["Status"].isin(status)
        & dados["v_2"].between(data_inicio, data_fim)
    )

    if busca.strip():
        mascara &= dados["Registro"].str.contains(
            busca.strip(), regex=False, case=False, na=False
        )

    return dados.loc[mascara].copy()


def resumo_por_centro(dados: pd.DataFrame) -> pd.DataFrame:
    """Calcula volume e taxa de visitas realizadas por centro."""
    if dados.empty:
        return pd.DataFrame(
            columns=["Centro", "Registros", "Realizados", "Taxa de realização (%)"]
        )

    resumo = (
        dados.assign(Realizado=dados["Status"].eq("Realizado"))
        .groupby("Centro", as_index=False)
        .agg(Registros=("Registro", "size"), Realizados=("Realizado", "sum"))
    )
    resumo["Taxa de realização (%)"] = (
        resumo["Realizados"] / resumo["Registros"] * 100
    ).round(1)
    return resumo.sort_values("Registros", ascending=False).reset_index(drop=True)

