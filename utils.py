import datetime
import uuid
import models
from sqlalchemy.orm import Session
from pytz import timezone



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


def get_account_information(account_id: uuid.UUID, current_user: dict, db: Session):
    accounts_info = db.query(models.Accounts)\
        .filter((models.Accounts.user_id == get_user_id(current_user)) and (models.Accounts.id == account_id))\
        .first()
    return accounts_info

def get_credit_account_information(account_id: uuid.UUID, current_user: dict, db: Session):
    credit_account_info = db.query(models.CreditAccount)\
        .filter((models.CreditAccount.user_id == get_user_id(current_user)) and (models.CreditAccount.id == account_id))\
        .first()
    return credit_account_info

def get_transactions_info_from_account_id_for_current_user(account_id: uuid.UUID, current_user: dict ,db: Session):
    return db.query(models.Transactions)\
        .filter(models.Transactions.account_id == account_id and 
                models.Transactions.id == get_user_id(current_user)
        )\
        .all()