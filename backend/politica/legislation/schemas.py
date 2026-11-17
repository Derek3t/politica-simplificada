from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AgendaQuery(BaseModel):
    data: date
    apenas_seguidos: bool = False
    incluir_comissoes: bool = False
    uf: str | None = Field(default=None, pattern=r"^[A-Za-z]{2}$")


class ParlamentaresQuery(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    busca: str | None = Field(default=None, max_length=150)
    estado: str | None = Field(default=None, min_length=2, max_length=2)
    partido: str | None = Field(default=None, max_length=20)
    casa: Literal["Câmara", "Senado"] | None = None
    pagina: int = Field(default=1, ge=1)
    por_pagina: int = Field(default=20, ge=1, le=100)


class CalendarioQuery(BaseModel):
    mes: str = Field(pattern=r"^[1-9]\d{3}-(0[1-9]|1[0-2])$")
    uf: str | None = Field(default=None, pattern=r"^[A-Za-z]{2}$")


class VotacoesQuery(BaseModel):
    periodo: Literal["hoje", "semana", "mes"] = "hoje"
    status: Literal["aprovado", "rejeitado", "andamento"] | None = None
    casa: Literal["Câmara", "Senado"] | None = None
    pagina: int = Field(default=1, ge=1)
    por_pagina: int = Field(default=20, ge=1, le=100)


class BuscaQuery(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    q: str = Field(min_length=2, max_length=100)
