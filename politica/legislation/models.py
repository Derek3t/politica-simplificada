from datetime import date, time
from typing import List, Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from politica.extensions import db


class Agenda(db.Model):
    __tablename__ = "agenda"

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[date] = mapped_column(unique=True, index=True)
    resumo: Mapped[Optional[str]] = mapped_column(db.Text)

    projetos_lei: Mapped[List["ProjetoLei"]] = relationship(
        back_populates="agenda", cascade="all, delete-orphan", passive_deletes=True
    )
    dias_especiais: Mapped[List["DiaEspecial"]] = relationship(
        back_populates="agenda", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self):
        return f"<Agenda id={self.id} data='{self.data}'>"


class DiaEspecial(db.Model):
    __tablename__ = "dias_especiais"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(db.String(150))
    tipo: Mapped[str] = mapped_column(db.String(50))
    contexto_historico: Mapped[Optional[str]] = mapped_column(db.Text)
    importancia: Mapped[Optional[str]] = mapped_column(db.Text)
    impacto_legislativo: Mapped[Optional[str]] = mapped_column(db.Text)
    agenda_id: Mapped[int] = mapped_column(db.ForeignKey("agenda.id", ondelete="CASCADE"))

    agenda: Mapped["Agenda"] = relationship(back_populates="dias_especiais")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "data": self.agenda.data.isoformat(),
            "contexto_historico": self.contexto_historico,
            "importancia": self.importancia,
            "impacto_legislativo": self.impacto_legislativo,
        }


class ProjetoLei(db.Model):
    __tablename__ = "projetos_lei"
    __table_args__ = (UniqueConstraint("agenda_id", "id_original", name="uq_projeto_agenda_original"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    id_original: Mapped[Optional[str]] = mapped_column(db.String(100))
    tipo: Mapped[Optional[str]] = mapped_column(db.String(10))
    codigo_pl: Mapped[str] = mapped_column(db.String(50))
    titulo: Mapped[str] = mapped_column(db.Text)
    orgao: Mapped[Optional[str]] = mapped_column(db.String(150))
    horario: Mapped[Optional[time]]
    resumo: Mapped[Optional[str]] = mapped_column(db.Text)
    analise_impacto: Mapped[Optional[str]] = mapped_column(db.Text)
    comparacao_internacional: Mapped[Optional[str]] = mapped_column(db.Text)
    status: Mapped[str] = mapped_column(db.String(50), default="Em pauta")
    data_votacao: Mapped[Optional[date]]
    agenda_id: Mapped[int] = mapped_column(db.ForeignKey("agenda.id", ondelete="CASCADE"))

    agenda: Mapped["Agenda"] = relationship(back_populates="projetos_lei")
    historicos: Mapped[List["Historico"]] = relationship(
        back_populates="projeto", cascade="all, delete-orphan", passive_deletes=True
    )

    def to_dict(self, destacado=False):
        return {
            "id": self.id,
            "codigo_pl": self.codigo_pl,
            "titulo": self.titulo,
            "orgao": self.orgao,
            "horario": self.horario.strftime("%H:%M") if self.horario else None,
            "status": self.status,
            "data_votacao": self.data_votacao.isoformat() if self.data_votacao else None,
            "resumo": self.resumo,
            "analise_impacto": self.analise_impacto,
            "comparacao_internacional": self.comparacao_internacional,
            "destacado": destacado,
        }

    def __repr__(self):
        return f"<ProjetoLei id={self.id} codigo_pl='{self.codigo_pl}'>"


class Parlamentar(db.Model):
    __tablename__ = "parlamentar"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_original: Mapped[int] = mapped_column(unique=True)
    nome: Mapped[str] = mapped_column(db.String(150), index=True)
    partido: Mapped[str] = mapped_column(db.String(20))
    estado: Mapped[str] = mapped_column(db.String(2))
    foto_link: Mapped[Optional[str]] = mapped_column(db.String(500))

    historicos: Mapped[List["Historico"]] = relationship(
        back_populates="parlamentar", cascade="all, delete-orphan", passive_deletes=True
    )
    seguidores: Mapped[List["UsuarioParlamentar"]] = relationship(
        back_populates="parlamentar", cascade="all, delete-orphan", passive_deletes=True
    )

    def to_dict(self, seguido=False):
        return {
            "id": self.id,
            "nome": self.nome,
            "partido": self.partido,
            "estado": self.estado,
            "foto_link": self.foto_link,
            "seguido": seguido,
        }

    def __repr__(self):
        return f"<Parlamentar id={self.id} nome='{self.nome} ({self.partido}/{self.estado})'>"


class Historico(db.Model):
    __tablename__ = "historico"
    __table_args__ = (UniqueConstraint("parlamentar_id", "projeto_id", name="uq_historico_parlamentar_projeto"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    parlamentar_id: Mapped[int] = mapped_column(db.ForeignKey("parlamentar.id", ondelete="CASCADE"))
    projeto_id: Mapped[int] = mapped_column(db.ForeignKey("projetos_lei.id", ondelete="CASCADE"))
    posicionamento: Mapped[str] = mapped_column(db.String(50))

    parlamentar: Mapped["Parlamentar"] = relationship(back_populates="historicos")
    projeto: Mapped["ProjetoLei"] = relationship(back_populates="historicos")

    def __repr__(self):
        return f"<Historico id={self.id} parlamentar_id={self.parlamentar_id} projeto_id={self.projeto_id}>"
