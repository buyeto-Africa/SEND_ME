# models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, nullable=True)
    password = Column(String, nullable=False)
    tenant_id = Column(Integer, nullable=False)
    role = Column(String, default="customer", nullable=False)  # Added role field
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships can be added when you implement order models
    # orders = relationship("Order", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"