import sys
sys.path.append("..")

from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict
import datetime
import models
import enum


class UserResponseModel(BaseModel):
    id: uuid.UUID
    full_name: str
    email_id: str
    phone_number: str

class TransactionResponseModel(BaseModel):
    id: uuid.UUID
    transaction_amount: int
    transaction_date: datetime.date
    transaction_description: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    transaction_currency_type: models.CurrencyType
    is_recurring: bool
    category: str