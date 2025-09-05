from datetime import datetime
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

# Define a SQLAlchemy ORM model to represent the "usage_logs" table
class UsageLog(Base):
    # Name of the database table
    __tablename__ = "usage_logs"

    # Primary key column (auto-incremented integer)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Timestamp when the log entry was created
    # Defaults to the current UTC datetime
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    # Label for the user who made the request (e.g. "alice")
    # Indexed for fast lookups by user
    user_label: Mapped[str] = mapped_column(String(100), index=True)

    # Model name that was called (e.g. "gpt-5-mini")
    # Indexed for fast aggregation queries by model
    model: Mapped[str] = mapped_column(String(100), index=True)

    # Number of input tokens consumed in this request
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)

    # Number of output tokens generated in this request
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)