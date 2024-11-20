from pydantic import BaseModel
from pydantic import EmailStr

from app.schemas.user import PasswordValidatorMixin


class VerificationRequest(BaseModel):
    email: EmailStr
    verification_code: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthToken(BaseModel):
    token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetToken(BaseModel):
    token: str
    email: EmailStr


class PasswordResetConfirm(PasswordValidatorMixin):
    token: str
