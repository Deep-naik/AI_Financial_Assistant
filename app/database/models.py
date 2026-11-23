
from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime, timezone

from app.database.connection import Base


class Dataset(Base):

    __tablename__ = "datasets"

    dataset_id = Column(
        String,
        primary_key=True,
        index=True
    )

    filename = Column(String, nullable=False)

    file_path = Column(String, nullable=False)

    processed_path = Column(String, nullable=False)

    total_rows = Column(Integer)

    total_columns = Column(Integer)

    upload_date = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    status = Column(
        String,
        default="processed"
    )
