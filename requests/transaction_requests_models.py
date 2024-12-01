import datetime
from typing import Optional
import uuid
from pydantic import BaseModel

import models


class RecurringTransaction(BaseModel):
    recurring_amount: float
    recurring_transaction_category: models.TransactionCategory
    frequency: int
    start_date: datetime.date
    end_date: datetime.date
    description: Optional[str] = None
    created_at: datetime.date
    updated_at: Optional[datetime.date] = None
    user_id: uuid.UUID

class Transaction(BaseModel):
    transaction_amount: int
    transaction_date: datetime.date
    transaction_description: Optional[str] = None
    transaction_currency_type: models.CurrencyType
    is_recurring: Optional[bool] = False
    recurring_transaction: Optional[RecurringTransaction] = None
    account_id: uuid.UUID
    category: Optional[str] = None

class UpdateTransaction(BaseModel):
    id: uuid.UUID
    transaction_amount: Optional[int] = None
    transaction_date: Optional[datetime.date] = None
    transaction_description: Optional[str] = None
    transaction_currency_type: Optional[models.CurrencyType] = None
    is_recurring: Optional[bool] = None
    account_id: uuid.UUID
    category: Optional[str] = None