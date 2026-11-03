from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from politica.ext.db import db

if TYPE_CHECKING:
    from politica.legislation.models import Agenda


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    google_id: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(db.String(150), nullable=False)
    access_token: Mapped[str] = mapped_column(db.Text, nullable=False)
    refresh_token: Mapped[str] = mapped_column(db.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=db.func.now())

    # Relacionamento com a Agenda
    agendas: Mapped[List["Agenda"]] = relationship(
        "Agenda",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} email='{self.email}'>"