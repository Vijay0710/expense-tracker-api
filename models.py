import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Boolean, Column, Date, String, ForeignKey, BigInteger, DateTime, Enum, Double
import utils
from enum import Enum as pyEnum
import sys
sys.path.append("..")


class AccountType(pyEnum):
    SAVINGS_ACCOUNT = "SAVINGS_ACCOUNT"
    CHECKING_ACCOUNT = "CHECKING_ACCOUNT"
    BUSINESS_ACCOUNT = "BUSINESS_ACCOUNT"
    JOINT_ACCOUNT = "JOINT_ACCOUNT"
    CREDIT_ACCOUNT = "CREDIT_ACCOUNT"


class CurrencyType(pyEnum):
    INR = "INR"
    USD = "USD"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    full_name = Column(String)
    email_id = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    phone_number = Column(String, unique=True, index=True)
    address_id = Column(UUID(as_uuid=True), ForeignKey('address.id'), default=None)

    user_address_fk = relationship('Address', back_populates='address_user_fk', foreign_keys="[Address.user_id]")
    transactions = relationship('Transactions', back_populates='user_transaction_fk')
    accounts = relationship('Accounts', back_populates='user_account_fk')
    credit_account_fk = relationship('CreditAccount',back_populates='user_credit_account_fk')


class Address(Base):
    __tablename__ = 'address'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address_1 = Column(String)
    address_2 = Column(String, default=None)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    postal_code = Column(String)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    address_user_fk = relationship('User', back_populates='user_address_fk', foreign_keys="[Address.user_id]")


class Transactions(Base):
    __tablename__ = 'transactions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    transaction_amount = Column(BigInteger)
    transaction_date = Column(Date)
    category = Column(String, default="Other")
    transaction_description = Column(String, default=None, nullable=True)
    created_at = Column(DateTime, default=utils.getCurrentTimeStamp())
    updated_at = Column(DateTime, default=None, nullable=True)
    transaction_currency_type = Column(Enum(CurrencyType), default="INR")
    is_recurring = Column(Boolean, default=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'))

    user_transaction_fk = relationship('User', back_populates='transactions')
    transaction_account_fk = relationship('Accounts',back_populates='account_transaction_fk')


class Accounts(Base):
    __tablename__ = 'accounts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    account_type = Column(Enum(AccountType), nullable=False)
    bank_name = Column(String, nullable=False)
    account_number = Column(BigInteger, nullable=False)
    account_balance = Column(Double, default=0)
    currency = Column(Enum(CurrencyType), default=CurrencyType.INR)
    created_at = Column(DateTime, default=utils.getCurrentTimeStamp())
    updated_at = Column(DateTime, default=None, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    account_transaction_fk = relationship('Transactions', back_populates='transaction_account_fk')
    user_account_fk = relationship('User', back_populates='accounts')
    credit_account_fk = relationship('CreditAccount', back_populates='account_credit_account_fk')
    

class CreditAccount(Base):
    __tablename__ = 'credit_account'

    credit_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'),primary_key= True, default=None)
    credit_card_limit = Column(String, nullable=False)
    credit_card_due_date = Column(Date, nullable=False)
    credit_card_outstanding = Column(BigInteger, nullable=False, default=0)
    billing_cycle = Column(String, nullable=False)
    total_reward_points = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True),ForeignKey('users.id'),nullable=False)
    
    account_credit_account_fk = relationship('Accounts', back_populates='credit_account_fk')
    user_credit_account_fk = relationship('User',back_populates='credit_account_fk')


    


