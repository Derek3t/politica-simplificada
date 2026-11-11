from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AgendaQuery(BaseModel):
    data: date
    apenas_seguidos: bool = False
    incluir_comissoes: bool = False


class ParlamentaresQuery(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    busca: Optional[str] = Field(default=None, max_length=150)
    estado: Optional[str] = Field(default=None, min_length=2, max_length=2)
    partido: Optional[str] = Field(default=None, max_length=20)
    pagina: int = Field(default=1, ge=1)
    por_pagina: int = Field(default=20, ge=1, le=100)
