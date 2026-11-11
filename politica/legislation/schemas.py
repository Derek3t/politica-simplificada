from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AgendaQuery(BaseModel):
    data: date
    apenas_seguidos: bool = False
    incluir_comissoes: bool = False


class ParlamentaresQuery(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    busca: str | None = Field(default=None, max_length=150)
    estado: str | None = Field(default=None, min_length=2, max_length=2)
    partido: str | None = Field(default=None, max_length=20)
    pagina: int = Field(default=1, ge=1)
    por_pagina: int = Field(default=20, ge=1, le=100)


class CalendarioQuery(BaseModel):
    mes: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")


class VotacoesQuery(BaseModel):
    periodo: Literal["hoje", "semana", "mes"] = "hoje"
    status: Literal["aprovado", "rejeitado", "andamento"] | None = None
    pagina: int = Field(default=1, ge=1)
    por_pagina: int = Field(default=20, ge=1, le=100)
