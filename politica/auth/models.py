from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from politica.ext.db import db

if TYPE_CHECKING:
    from politica.legislation.models import Parlamentar


class UsuarioParlamentar(db.Model):
    __tablename__ = "usuario_parlamentar"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    parlamentar_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey("parlamentar.id"), nullable=False)

    # Relações bidirecionais apontando para as pontas
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="parlamentares_seguidos")
    parlamentar: Mapped["Parlamentar"] = relationship("Parlamentar", back_populates="seguidores")

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    google_id: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(db.String(150), nullable=False)
    access_token: Mapped[str] = mapped_column(db.Text, nullable=False)
    refresh_token: Mapped[str] = mapped_column(db.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=db.func.now())

    # Aqui é uma lista da CLASSE intermediária (porque guardamos dados da relação)
    parlamentares_seguidos: Mapped[List["UsuarioParlamentar"]] = relationship(
        "UsuarioParlamentar", 
        back_populates="usuario", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} email='{self.email}'>"