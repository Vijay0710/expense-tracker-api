import sys
from typing import List, Optional

from pydantic import BaseModel

import responses.Response
sys.path.append("../..")

import models
from database import SessionLocal, engine
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from responses import Response
from routers.auth import decode_jwt_and_get_current_user
from exceptions import user, accounts as exception_account,transactions
import datetime
import uuid
import utils
from responses.Response import TransactionResponseModel
from sqlalchemy.exc import OperationalError
from exceptions import network


class Transaction(BaseModel):
    transaction_amount: int
    transaction_date: datetime.date
    transaction_description: Optional[str] = None
    transaction_currency_type: models.CurrencyType
    is_recurring: Optional[bool] = False
    account_id: uuid.UUID
    category: str

class UpdateTransaction(BaseModel):
    id: uuid.UUID
    transaction_amount: Optional[int] = None
    transaction_date: Optional[datetime.date] = None
    transaction_description: Optional[str] = None
    transaction_currency_type: Optional[models.CurrencyType] = None
    is_recurring: Optional[bool] = None
    account_id: uuid.UUID
    category: Optional[str] = None

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    responses={
        404: {
            "description": "No Transactions Found"
        }
    }
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


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

def get_transaction_info_from_current_user(db: Session, account_id: uuid.UUID, transaction_id: uuid.UUID, current_user: dict):
    transaction_info = db.query(models.Transactions)\
        .filter(models.Transactions.user_id == get_user_id(current_user) and 
                models.Transactions.account_id == account_id and
                models.Transactions.id == transaction_id
        )\
        .first()
    return transaction_info

def get_transactions_info_from_account_id_for_current_user(account_id: uuid.UUID, current_user: dict ,db: Session):
    return db.query(models.Transactions)\
        .filter(models.Transactions.account_id == account_id and 
                models.Transactions.id == get_user_id(current_user)
        )\
        .all()

@router.post("/", response_model=list[TransactionResponseModel])
async def get_transactions(account_id: uuid.UUID = None, db: Session = Depends(get_db), current_user: dict = Depends(decode_jwt_and_get_current_user)):
    try:
        user_data = get_user_data(current_user, db)

        if user_data: 
            if account_id:
                transactions = get_transactions_info_from_account_id_for_current_user(
                    account_id=account_id,
                    current_user=current_user,
                    db=db
                )
            else:
                transactions = db.query(models.Transactions)\
                    .filter(models.Transactions.user_id == user_data.id)\
                    .all()
            return transactions
        else:
            user.not_found_exception()
    
    except OperationalError:
        raise network.network_exception()
    

@router.post("/add")
async def add_transaction(transaction: Transaction, db: Session = Depends(get_db), current_user: dict = Depends(decode_jwt_and_get_current_user)):
    try:
        user_data  = get_user_data(current_user, db)

        accounts = get_accounts_information(current_user, db)
        
        is_valid_account = any(account.id == transaction.account_id for account in accounts)

        if is_valid_account:
            if user_data:
                transaction_model = models.Transactions(
                    id = uuid.uuid4(),
                    **transaction.__dict__,
                    user_id = get_user_id(current_user),
                )
                db.add(transaction_model)
            else:
                raise user.not_found_exception()
        else:
            raise exception_account.not_found_exception()
        
        db.commit()
        return {
            'status' : status.HTTP_201_CREATED,
            'detail' : 'Transaction Recorded Successfully'
        }
    except OperationalError:
        raise network.network_exception()

@router.patch("/update")
async def update_transaction(transaction: UpdateTransaction, db: Session = Depends(get_db), current_user: dict = Depends(decode_jwt_and_get_current_user)):
    try:
        user_data  = get_user_data(current_user, db)
        accounts = get_accounts_information(current_user, db)

        is_valid_account = any(account.id == transaction.account_id for account in accounts)
        
        if is_valid_account:
            is_valid_transaction = get_transaction_info_from_current_user(
                db,
                transaction.account_id,
                transaction.id,
                current_user
            )
            if user_data != None:
                if is_valid_transaction:
                    updated_transaction = transaction.model_dump(exclude_unset=True)
                    updated_transaction["updated_at"] = utils.getCurrentTimeStamp()

                    print(updated_transaction)
                    for var, value in updated_transaction.items():
                        setattr(is_valid_transaction, var, value)
                    
                    db.commit()
                    
                    return {
                        'status' : status.HTTP_202_ACCEPTED,
                        'detail' : "Transaction Updated Successfully"
                    }
                else:
                    raise transactions.not_found_exception()
            else:
                raise user.not_found_exception()
        else:
            raise exception_account.not_found_exception()
    
    except OperationalError:
        raise network.network_exception()

@router.delete("/delete")
async def delete_transaction(transaction_id: uuid.UUID, db: Session = Depends(get_db), current_user: dict = Depends(decode_jwt_and_get_current_user)):
    try:    
        user_data  = get_user_data(current_user, db)

        is_valid_transaction = db.query(models.Transactions)\
                                .filter(models.Transactions.id == transaction_id and 
                                        models.Transactions.user_id == get_user_id(user_data))\
                                .first()                
        if is_valid_transaction:
            db.delete(is_valid_transaction)
            db.commit()
            return {
                "status" : status.HTTP_204_NO_CONTENT,
                "detail" : "Transaction Deleted Successfully"
            }
        else:
            raise transactions.not_found_exception() 
    except OperationalError:
        raise network.network_exception()   