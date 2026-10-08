# backend/app/models/app_configurations_model.py

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.sql import func
from app.database import Base

class AppConfigurationModel(Base):
    """
    Singleton table for admin-managed application configuration overrides.

    Stores only editable override fields, not runtime/system information.
    """

    __tablename__ = "app_configurations"

    config_id = Column(Integer, primary_key=True, default=1)
    config_json = Column(JSON, nullable=False, default=dict)

    updated_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
