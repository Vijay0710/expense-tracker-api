from responses.Response import AccountInfoResponseModel
from exceptions import network, accounts as exception_accounts
from sqlalchemy.exc import OperationalError
import datetime
from routers.auth import get_current_user
from responses import Response
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
    account_limit: int
    account_due_date: datetime.date
    account_current_outstanding: str
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


class UpdateAccountInformation(BaseModel):
    id: uuid.UUID
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    account_balance: Optional[float] = None
    account_type: Optional[models.AccountType] = None
    currency: Optional[models.CurrencyType] = None


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
            create_account_model = models.Accounts()

            create_account_model.id = uuid.uuid4()
            create_account_model.account_number = account.account_number
            create_account_model.account_type = account.account_type
            create_account_model.account_balance = account.account_balance
            create_account_model.bank_name = account.bank_name
            create_account_model.currency = account.currency
            create_account_model.user_id = user_data.id

            if (account.account_type.value == 5):
                credit_account = models.CreditAccount()
                credit_account.credit_account_id = create_account_model.id
                credit_account.credit_card_limit = account.credit_account_information.account_limit
                credit_account.credit_card_due_date = account.credit_account_information.account_due_date
                credit_account.billing_cycle = account.credit_account_information.billing_cycle
                credit_account.total_reward_points = account.credit_account_information.total_reward_points
                credit_account.credit_card_outstanding = account.credit_account_information.account_current_outstanding
                credit_account.user_id = userId
                db.add(credit_account)

        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User couldn't be found")

        db.add(create_account_model)
        db.commit()

        return {
            'status': status.HTTP_201_CREATED,
            'detail': 'Account Added Successfully'
        }

    except OperationalError:
        network.network_exception()


@router.post("/info", response_model=list[AccountInfoResponseModel])
async def get_accounts(db: Session = Depends(get_db), current_user:  dict = Depends(get_current_user)):
    try:
        userId = current_user.get("user_id")

        user_data = db.query(models.User)\
            .filter(models.User.id == userId)\
            .first()

        if user_data:
            accounts = db.query(models.Accounts)\
                .filter(models.Accounts.user_id == userId)\
                .all()
            return accounts

        else:
            raise exception_accounts.not_found_exception()

    except OperationalError:
        network.network_exception()


@router.patch("/update")
async def update_account_information(account: UpdateAccountInformation, db: Session = Depends(get_db), current_user:  dict = Depends(get_current_user)):
    try:
        account_info = utils.get_account_information(
            account.id, current_user, db)
        print(account_info)
        if account_info:
            updated_account_info = account.model_dump(exclude_unset=True)
            # Shouldn't update the id(since it is a PK) so popping it from request body after getting account information
            updated_account_info.pop('id', None)
            updated_account_info["updated_at"] = utils.getCurrentTimeStamp()
            for var, value in updated_account_info.items():
                setattr(account_info, var, value)
            db.commit()
            return {
                'status': status.HTTP_202_ACCEPTED,
                'detail': "Account Updated Successfully"
            }
        else:
            raise exception_accounts.not_found_exception()

    except OperationalError:
        network.network_exception()
