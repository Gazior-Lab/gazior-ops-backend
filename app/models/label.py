from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base



class Label(Base):
    __tablename__ = "labels"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    color: Mapped[str] = mapped_column(String(7), nullable=False)  # Hex code (e.g., #FF5733)