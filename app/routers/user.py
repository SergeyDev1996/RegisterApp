from fastapi import APIRouter, HTTPException

from app.db import in_memory_db
from app.schemas.user import UserCreate
from app.utils import hash_password, generate_verification_code, send_verification_code_email

user_router = APIRouter()


@user_router.post("/user/signup")
async def create_user(user_create: UserCreate):
    # Check if the user already exists
    user_email = user_create.email
    user_exists = in_memory_db.get(user_email)
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    in_memory_db[user_email] = {}
    hashed_password = hash_password(user_create.password)
    user_verification_code = generate_verification_code()
    in_memory_db[user_email]["password"] = hashed_password
    in_memory_db[user_email]["verification_code"] = user_verification_code
    in_memory_db[user_email]["is_verified"] = False
    send_verification_code_email(user_email=user_email, verification_code=user_verification_code)
    return {
        "msg": "User created successfully. Please check your email to verify the user.", "user_email": user_email
    }
