import datetime
import secrets
import uuid
import models
from sqlalchemy.orm import Session
from pytz import timezone
from fastapi import HTTPException, status
from templates import settings



def getCurrentTimeStamp():
    return datetime.datetime.now(timezone("Asia/Kolkata"))


def get_user_id(current_user: dict):
    return current_user.get("user_id")

def get_user_data(current_user: dict, db: Session):
    user_data  = db.query(models.User)\
                    .filter(models.User.id == get_user_id(current_user))\
                    .first()
    return user_data


def get_accounts_information(current_user: dict, db: Session):
    accounts_info = db.query(models.Accounts)\
        .filter(models.Accounts.user_id == get_user_id(current_user))\
        .all()
    return accounts_info


def get_account_information(account_id: uuid.UUID, db: Session):
    accounts_info = db.query(models.Accounts)\
        .filter(models.Accounts.id == account_id)\
        .first()
    return accounts_info

def get_credit_account_information(account_id: uuid.UUID, db: Session):
    credit_account_info = db.query(models.CreditAccount)\
        .filter(models.CreditAccount.credit_account_id == account_id)\
        .first()
    return credit_account_info

def get_transactions_info_from_account_id_for_current_user(account_id: uuid.UUID, current_user: dict ,db: Session):
    return db.query(models.Transactions)\
        .filter(models.Transactions.account_id == account_id and 
                models.Transactions.id == get_user_id(current_user)
        )\
        .all()

def get_transaction_info_from_current_user(db: Session, account_id: uuid.UUID, transaction_id: uuid.UUID, current_user: dict):
    transaction_info = db.query(models.Transactions)\
        .filter(models.Transactions.user_id == get_user_id(current_user) and 
                models.Transactions.account_id == account_id and
                models.Transactions.id == transaction_id
        )\
        .first()
    return transaction_info

def get_recurring_transactions_info(db: Session, account_id: uuid.UUID, transaction_id: uuid.UUID, current_user: dict):
    recurring_transaction_info = db.query(models.RecurringTransaction)\
                                .filter(models.RecurringTransaction.user_id == get_user_id(current_user) and
                                        models.RecurringTransaction.account_id == account_id and
                                        models.RecurringTransaction.recurring_transaction_id == transaction_id)\
                                .first()
    return recurring_transaction_info


def authenticate_username_and_password(username: str, password: str):
    correct_username = secrets.compare_digest(username, settings.USERNAME)
    correct_password = secrets.compare_digest(password, settings.API_PASSWORD)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Auth-Basic header is missing or invalid credentials"
        )