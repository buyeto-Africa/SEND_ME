from pydantic import BaseModel, EmailStr
from typing import Optional

class SignupRequest(BaseModel):
    email: EmailStr  # Using EmailStr for email validation
    password: str
    phone_number: Optional[str] = None
    tenant_id: int

class SignupResponse(BaseModel):
    msg: str