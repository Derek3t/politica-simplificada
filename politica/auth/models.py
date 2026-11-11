from datetime import datetime
from typing import List

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from politica.extensions import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(db.String(150))
    email: Mapped[str] = mapped_column(db.String(255), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(db.String(255))
    created_at: Mapped[datetime] = mapped_column(server_default=db.func.now())

    parlamentares_seguidos: Mapped[List["UsuarioParlamentar"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan", passive_deletes=True
    )

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "email": self.email}

    def __repr__(self):
        return f"<Usuario id={self.id} email='{self.email}'>"


class UsuarioParlamentar(db.Model):
    __tablename__ = "usuario_parlamentar"
    __table_args__ = (UniqueConstraint("usuario_id", "parlamentar_id", name="uq_usuario_parlamentar"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(db.ForeignKey("usuarios.id", ondelete="CASCADE"))
    parlamentar_id: Mapped[int] = mapped_column(db.ForeignKey("parlamentar.id", ondelete="CASCADE"))

    usuario: Mapped["Usuario"] = relationship(back_populates="parlamentares_seguidos")
    parlamentar: Mapped["Parlamentar"] = relationship(back_populates="seguidores")
