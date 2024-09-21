import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
import sys
sys.path.append("..")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String)
    email_id = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    address_id = Column(UUID(as_uuid=True), ForeignKey('address.id'), default=uuid.uuid4)

    address = relationship('Address', back_populates='user')


class Address(Base):
    __tablename__ = 'address'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address_1 = Column(String)
    address_2 = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    postal_code = Column(String)

    user_address = relationship('Users', back_populates='address')
