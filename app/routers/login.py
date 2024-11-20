from uuid import uuid4

from fastapi import APIRouter, HTTPException
from starlette import status

from app.db import in_memory_db, reset_tokens
from app.schemas.login import VerificationRequest, LoginRequest, AuthToken, PasswordResetRequest, PasswordResetToken, \
    PasswordResetConfirm
from app.schemas.user import UserEmail
from app.utils import generate_verification_code, send_verification_code_email, verify_password, generate_jwt_token, \
    verify_jwt_token, send_reset_password_email, hash_password

login_router = APIRouter()


@login_router.post("/login/verify")
async def verify_user(request: VerificationRequest):
    # Fetch user from the in-memory store
    user = in_memory_db.get(request.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user["is_verified"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your user has been already verified"
        )
    # Check if the code matches and is still valid
    if user.get("verification_code") == request.verification_code:        # Clear the verification code upon successful verification
        user["is_verified"] = True
        return {
            "status": "success", "message": "Email successfully verified."
        }
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code"
    )


@login_router.post("/login/token/access")
async def login_user(request: LoginRequest):
    # Retrieve the user data from in-memory store
    user = in_memory_db.get(request.email)

    # Check if user exists and is verified
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User with this email does not exist. Please signup first"
        )
    if not user["is_verified"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your user first"
        )
    # Verify password
    password_is_correct = verify_password(plain_password=request.password, hashed_password=user["password"])
    if not password_is_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong password"
        )
    # Generate a JWT token (or any other token) for a successful login
    # For demonstration purposes, we’ll return a placeholder token
    tokens = generate_jwt_token(user_email=request.email, token_type="full") # Replace with actual token generation logic
    return tokens


@login_router.post("/login/token/refresh")
async def refresh_token(token: AuthToken):
    # Validate the refresh token
    payload = verify_jwt_token(token=token.token, token_validation_type="refresh")
    user_email = payload.get("email")
    if user_email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    # Generate a new access token
    new_access_token = generate_jwt_token(user_email=user_email, token_type="access")
    return {
        "access_token": new_access_token, "token_type": "bearer"
    }


@login_router.post("/login/password_reset/request")
async def request_password_reset(data: PasswordResetRequest):
    user = in_memory_db.get(data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email is not registered on our "
                                                                            "website")
    reset_token = str(uuid4())
    reset_tokens[reset_token] = data.email
    # Send the reset token via email
    send_reset_password_email(email=data.email, token=reset_token)
    return {
        "message": "Password reset email sent."
    }


@login_router.post("/login/resend_verification_code", status_code=status.HTTP_200_OK)
async def resend_token(email: UserEmail):
    user = in_memory_db.get(email.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email does not exists. Please signup first."
        )
    if user["is_verified"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your user has been already verified"
        )
    verification_code = generate_verification_code()
    in_memory_db[email.email]["verification_code"] = verification_code
    send_verification_code_email(user_email=email.email, verification_code=verification_code)
    return {
        "message": "Login link has been resent successfully"
    }


@login_router.post("/login/password_reset/confirm")
async def confirm_password_reset(data: PasswordResetConfirm):
    # Verify the token exists and get the email
    if data.token not in reset_tokens:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    email = reset_tokens[data.token]
    # Hash the new password
    hashed_password = hash_password(data.password)
    # Save hashed password to user data (in real applications, update the user in DB)
    # delete the token after use
    in_memory_db[email]["password"] = hashed_password
    del reset_tokens[data.token]
    return {
        "message": "Password reset successful."
    }
