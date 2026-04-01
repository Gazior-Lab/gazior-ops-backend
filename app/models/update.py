from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

#### `Update` (Announcement)
# Team updates mapped to the frontend "Recent Updates" / Megaphone feed.
# - `id`: UUID (Primary Key)
# - `workspace_id`: UUID (Foreign Key -> Workspace.id)
# - `author_id`: UUID (Foreign Key -> User.id)
# - `title`: String
# - `content`: Text (Markdown)
# - `tag`: String (e.g., 'Launch', 'System', 'Performance')
# - `department`: String (Nullable)
# - `created_at`: DateTime
# - `updated_at`: DateTime

class Update(Base):
    __tablename__ = "updates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(String(5000), nullable=False)  # Markdown content

    tag: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'Launch', 'System', 'Performance'
    department: Mapped[str] = mapped_column(String(100), nullable=True)

    # Server default timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)