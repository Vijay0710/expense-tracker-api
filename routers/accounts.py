from responses.JsonResponse import SuccessResponse
from responses.ResponseModels import AccountInfoResponseModel
from exceptions import network, accounts as exception_accounts, transactions
from sqlalchemy.exc import OperationalError
import datetime
from routers.auth import get_current_user
from responses import ResponseModels
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from database import SessionLocal, engine
import models
import sys
from typing import Optional
import uuid

from pydantic import BaseModel
from sqlalchemy import BigInteger

import utils
sys.path.append("../..")


router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    responses={
        404: {
            "description": "No Accounts Found"
        }
    }
)

class CreditAccountInformation(BaseModel):
    credit_card_limit: int
    credit_card_due_date: datetime.date
    credit_card_outstanding: float
    billing_cycle: str
    total_reward_points: str


class AccountInformation(BaseModel):
    account_type: models.AccountType
    bank_name: str
    account_number: int
    account_balance: float
    currency: models.CurrencyType
    credit_account_information: Optional[CreditAccountInformation] = None
    updated_at: Optional[str] = None

class UpdateCreditAccountInformation(BaseModel):
    credit_card_limit: Optional[str] = None
    credit_card_due_date: Optional[datetime.date] = None
    credit_card_outstanding: Optional[float] = None
    billing_cycle: Optional[datetime.date] = None
    total_reward_points: Optional[str] = None

class UpdateAccountInformation(BaseModel):
    id: uuid.UUID
    bank_name: Optional[str] = None
    account_number: int = None
    account_balance: Optional[float] = None
    account_type: Optional[models.AccountType] = None
    credit_account_information: Optional[UpdateCreditAccountInformation] = None
    currency: Optional[models.CurrencyType] = None

class AccountType(BaseModel):
    account_type: models.AccountType

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.post("/add")
async def create_account(account: AccountInformation, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        userId = current_user.get("user_id")

        user_data = db.query(models.User)\
            .filter(models.User.id == userId)\
            .first()

        if user_data:
            create_account_model = models.Accounts(
                id=uuid.uuid4(),
                **account.model_dump(exclude={"credit_account_information"}),
                user_id=userId
            )

            if (account.account_type.value == models.AccountType.CREDIT_ACCOUNT.value):
                credit_account = models.CreditAccount(
                    credit_account_id=create_account_model.id,
                    **account.credit_account_information.__dict__,
                    user_id=userId
                )
                db.add(credit_account)
            
            db.add(create_account_model)
            db.commit()
            return SuccessResponse(
                status_code = status.HTTP_201_CREATED,
                message={'detail': 'Account Added Successfully'}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User couldn't be found")

    except OperationalError:
        network.network_exception()


@router.post("/info", response_model=list[AccountInfoResponseModel])
async def get_accounts(accountTypeModel: Optional[AccountType] = None, db: Session = Depends(get_db), current_user:  dict = Depends(get_current_user)):
    try:
        userId = current_user.get("user_id")

        user_data = db.query(models.User)\
            .filter(models.User.id == userId)\
            .first()

        if user_data:
            accounts = db.query(models.Accounts)\
                .filter(models.Accounts.user_id == userId)\
            
            if accountTypeModel:
                accounts = accounts.filter(models.Accounts.account_type == accountTypeModel.account_type)
            
            return accounts.all()

        else:
            raise exception_accounts.not_found_exception()

    except OperationalError:
        network.network_exception()


@router.patch("/update")
async def update_account_information(account: UpdateAccountInformation, db: Session = Depends(get_db), current_user:  dict = Depends(get_current_user)):
    try:
        account_info = utils.get_account_information(account.id, db)
        credit_account_info = utils.get_credit_account_information(
            account_id=account_info.id,
            db=db
        )
        
        if account_info:
            updated_account_info = account.model_dump(exclude_unset=True, exclude={"credit_account_information"})
            # Shouldn't update the id(since it is a PK) so popping it from request body after getting account information
            updated_account_info.pop('id', None)
            updated_account_info["updated_at"] = utils.getCurrentTimeStamp()
                        
            for var, value in updated_account_info.items():
                setattr(account_info, var, value)

            if account.credit_account_information:
                updated_credit_account_info = account.credit_account_information.model_dump(exclude_unset=True)
                for var, value in updated_credit_account_info.items():
                    setattr(credit_account_info, var, value)
        
            db.commit()
            
            return SuccessResponse(
                status_code= status.HTTP_202_ACCEPTED,
                message={'detail': "Account Updated Successfully"}
            )
        else:
            raise exception_accounts.not_found_exception()

    except OperationalError:
        network.network_exception()

@router.delete("/delete", description="This operation will delete all the transactions associated with this account. Kindly use this with caution.")
async def delete_account_information(account_id: uuid.UUID, db: Session = Depends(get_db), current_user:  dict = Depends(get_current_user)):
    try:
        account_info = utils.get_account_information(account_id, db)

        if account_info:
            transactions_info = utils.get_transactions_info_from_account_id_for_current_user(
                account_id=account_id,
                current_user=current_user,
                db=db
            )

            credit_account_info = utils.get_credit_account_information(
                account_id=account_id,
                db=db
            )

            # Deleting all the assoicated account info from other tables before deleting from the primary table

            if credit_account_info:
                db.delete(credit_account_info)

            for transaction in transactions_info:
                if(transaction.is_recurring):
                    recurring__transaction_info = utils.get_recurring_transactions_info(
                        db=db,
                        account_id=account_id,
                        transaction_id=transaction.id,
                        current_user=current_user
                    )
                    if recurring__transaction_info:
                        db.delete(recurring__transaction_info)
                    else:
                        raise transactions.not_found_exception(
                            message="Something went wrong! Please try deleting this account later!"
                        )
                db.delete(transaction)
            
            db.delete(account_info)

            db.commit()

            return SuccessResponse(
                status_code = status.HTTP_202_ACCEPTED,
                message= {'detail': "Account and associated Transactions Deleted Successfully"}
            )
        else:
            raise exception_accounts.not_found_exception()

    except OperationalError:
        network.network_exception()