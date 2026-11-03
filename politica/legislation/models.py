from datetime import datetime, date
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from politica.ext.db import db

if TYPE_CHECKING:
    from politica.auth.models import Usuario


# === Agenda (Feed Diário) ===
class Agenda(db.Model):
    __tablename__ = "agenda"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    date: Mapped[date] = mapped_column(db.Date, nullable=False, unique=True, index=True)
    resumo: Mapped[Optional[str]] = mapped_column("Resumo", db.Text)
    usuario_ref: Mapped[int] = mapped_column("Usuario_REF", db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    # Relacionamentos
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="agendas")
    projetos_lei: Mapped[List["ProjetoLei"]] = relationship("ProjetoLei", back_populates="agenda", cascade="all, delete-orphan")
    dias_especiais: Mapped[List["DiaEspecial"]] = relationship("DiaEspecial", back_populates="agenda", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Agenda id={self.id} date='{self.date}'>"


# === Projetos de Lei ===
class ProjetoLei(db.Model):
    __tablename__ = "projetos_lei"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    vinculacao_id: Mapped[Optional[int]] = mapped_column(db.Integer)
    id_original: Mapped[Optional[str]] = mapped_column(db.String(100))
    codigo_pl: Mapped[str] = mapped_column("codigo_PL", db.String(50), nullable=False)
    titulo: Mapped[str] = mapped_column(db.String(255), nullable=False)
    resumo: Mapped[Optional[str]] = mapped_column("Resumo", db.Text)
    analise_impacto: Mapped[Optional[str]] = mapped_column(db.Text)
    comparacao_internacional: Mapped[Optional[str]] = mapped_column(db.Text)
    status: Mapped[str] = mapped_column(db.String(50), nullable=False, default="Em tramitação")
    data_votacao: Mapped[Optional[date]] = mapped_column(db.Date)
    agenda_ref: Mapped[int] = mapped_column("Agenda_REF", db.Integer, db.ForeignKey("agenda.id"), nullable=False)

    # Relacionamentos
    agenda: Mapped["Agenda"] = relationship("Agenda", back_populates="projetos_lei")
    historicos: Mapped[List["Historico"]] = relationship("Historico", back_populates="projeto", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ProjetoLei id={self.id} codigo_PL='{self.codigo_pl}'>"


# === Dias Especiais (Feriados e Datas Cívicas) ===
class DiaEspecial(db.Model):
    __tablename__ = "dias_especiais"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    vinculacao_id: Mapped[Optional[int]] = mapped_column(db.Integer)
    nome: Mapped[str] = mapped_column(db.String(150), nullable=False)
    tipo: Mapped[str] = mapped_column(db.String(50), nullable=False) # Ex: Feriado Nacional, Data Cívica
    agenda_ref: Mapped[int] = mapped_column("Agenda_REF", db.Integer, db.ForeignKey("agenda.id"), nullable=False)

    agenda: Mapped["Agenda"] = relationship("Agenda", back_populates="dias_especiais")

    def __repr__(self) -> str:
        return f"<DiaEspecial id={self.id} nome='{self.nome}'>"


# === Parlamentar ===
class Parlamentar(db.Model):
    __tablename__ = "parlamentar"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    id_original: Mapped[Optional[int]] = mapped_column(db.Integer)
    nome: Mapped[str] = mapped_column(db.String(150), nullable=False)
    partido: Mapped[str] = mapped_column(db.String(20), nullable=False)
    estado: Mapped[str] = mapped_column(db.String(2), nullable=False)
    foto_link: Mapped[Optional[str]] = mapped_column(db.String(500))

    # Relacionamentos
    historicos: Mapped[List["Historico"]] = relationship("Historico", back_populates="parlamentar", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Parlamentar id={self.id} nome='{self.nome} ({self.partido}/{self.estado})'>"


# === Histórico (Tabela Associativa N:N entre Parlamentar e ProjetoLei) ===
class Historico(db.Model):
    __tablename__ = "historico"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    parlamentar_id: Mapped[int] = mapped_column("parlamentar_id", db.Integer, db.ForeignKey("parlamentar.id"), nullable=False)
    projeto_id: Mapped[int] = mapped_column("projeto_id", db.Integer, db.ForeignKey("projetos_lei.id"), nullable=False)
    posicionamento: Mapped[str] = mapped_column(db.String(50), nullable=False) # Ex: Favorável, Controverso, Ausente

    # Relacionamentos N:N
    parlamentar: Mapped["Parlamentar"] = relationship("Parlamentar", back_populates="historicos")
    projeto: Mapped["ProjetoLei"] = relationship("ProjetoLei", back_populates="historicos")

    def __repr__(self) -> str:
        return f"<Historico id={self.id} parlamentar_id={self.parlamentar_id} projeto_id={self.projeto_id}>"