import sys
sys.path.append("..")

from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict
from models import AccountType, CurrencyType
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
    transaction_currency_type: CurrencyType
    is_recurring: bool
    category: str

class AccountInfoResponseModel(BaseModel):
    id: uuid.UUID
    account_type: AccountType
    bank_name: str
    account_number: str
    account_balance: float
    currency: CurrencyType
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

class CreditAccountResponseModel(BaseModel):
    id: uuid.UUID
    bank_name: str
    credit_card_limit: str
    credit_card_due_date: datetime.date
    billing_cycle: str
    credit_card_outstanding: float
    account_number: str
    card_type: str
    total_reward_points: str
