import sys
from typing import List, Optional

from pydantic import BaseModel

from requests.transaction_requests_models import Transaction, UpdateTransaction
sys.path.append("../..")

import models
from database import SessionLocal, engine
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from responses.JsonResponse import SuccessResponse
from routers.auth import decode_jwt_and_get_current_user
from exceptions import user, accounts as exception_account,transactions
import uuid
import utils
from responses.ResponseModels import TransactionResponseModel
from sqlalchemy.exc import OperationalError
from exceptions import network

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    responses={
        404: {
            "description": "No Transactions Found"
        },
        201: {
            "description": "Transaction Recorded and Added successfully"
        },
        204: {
            "description": "Transaction deleted successfully"
        }
    }
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.post("/", response_model=list[TransactionResponseModel])
async def get_transactions(account_id: uuid.UUID = None, db: Session = Depends(get_db), current_user: dict = Depends(decode_jwt_and_get_current_user)):
    try:
        user_data = utils.get_user_data(current_user, db)

        if user_data: 
            if account_id:
                transactions = utils.get_transactions_info_from_account_id_for_current_user(
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
        user_data  = utils.get_user_data(current_user, db)

        accounts = utils.get_accounts_information(current_user, db)
        
        is_valid_account = any(account.id == transaction.account_id for account in accounts)

        if is_valid_account:
            if user_data:
                transaction_model = models.Transactions(
                    id = uuid.uuid4(),
                    **transaction.model_dump(exclude={"recurring_transaction"}),
                    user_id = utils.get_user_id(current_user),
                )
                db.add(transaction_model)

                if transaction.is_recurring:
                    if transaction.recurring_transaction:
                        recurring_transaction_model = models.RecurringTransaction(
                            recurring_transaction_id = transaction_model.id,
                            **transaction.recurring_transaction.model_dump(exclude_unset=True),
                            account_id = transaction_model.account_id
                        )
                        db.add(recurring_transaction_model)
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You haven't specified any recurring transaction details. Please try again"
                        )
                db.commit()
                
                return SuccessResponse(
                    status_code = status.HTTP_201_CREATED,
                    message = {'detail' : 'Transaction Recorded Successfully'}
                )
            else:
                raise user.not_found_exception()
        else:
            raise exception_account.not_found_exception()
    except OperationalError:
        raise network.network_exception()

@router.patch("/update")
async def update_transaction(transaction: UpdateTransaction, db: Session = Depends(get_db), current_user: dict = Depends(decode_jwt_and_get_current_user)):
    try:
        user_data  = utils.get_user_data(current_user, db)
        accounts = utils.get_accounts_information(current_user, db)

        is_valid_account = any(account.id == transaction.account_id for account in accounts)
        
        if is_valid_account:
            is_valid_transaction = utils.get_transaction_info_from_current_user(
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
                    
                    return SuccessResponse(
                        status_code = status.HTTP_202_ACCEPTED,
                        message = {'detail' : 'Transaction Updated Successfully'}
                    )
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
        user_data  = utils.get_user_data(current_user, db)

        is_valid_transaction = db.query(models.Transactions)\
                                .filter(models.Transactions.id == transaction_id and 
                                        models.Transactions.user_id == utils.get_user_id(user_data))\
                                .first()                
        if is_valid_transaction:
            db.delete(is_valid_transaction)
            db.commit()
            return SuccessResponse(
                status_code= status.HTTP_204_NO_CONTENT,
                message= {"detail" : "Transaction Deleted Successfully"}
            )
        else:
            raise transactions.not_found_exception() 
    except OperationalError:
        raise network.network_exception()   