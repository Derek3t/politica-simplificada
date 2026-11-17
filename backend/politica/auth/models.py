from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from politica.extensions import db

if TYPE_CHECKING:
    from politica.legislation.models import Parlamentar


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(db.String(150))
    email: Mapped[str] = mapped_column(db.String(255), unique=True, index=True)
    senha_hash: Mapped[str | None] = mapped_column(db.String(255))
    google_id: Mapped[str | None] = mapped_column(db.String(64), unique=True, index=True)
    google_refresh_token: Mapped[str | None] = mapped_column(db.Text)
    created_at: Mapped[datetime] = mapped_column(server_default=db.func.now())

    parlamentares_seguidos: Mapped[list["UsuarioParlamentar"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan", passive_deletes=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "google_calendar": self.google_refresh_token is not None,
        }

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
