import sys
sys.path.append("..")

import uuid
from pydantic import BaseModel


class UserResponseModel(BaseModel):
    id: uuid.UUID
    full_name: str
    email_id: str
    phone_number: str