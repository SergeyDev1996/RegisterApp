import secrets
import string
import time
from typing import Dict, Optional

import jwt
from fastapi import HTTPException, Header
from sendgrid import Email, sendgrid, To, Mail
from starlette import status

from app.config import settings, pwd_context, jwt_settings


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def generate_verification_code(length=6):
    characters = string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def send_email(to_email: str, subject: str, content: str) -> None:
    """
    Sends an email using SendGrid.

    :param to_email: Recipient's email address
    :param subject: Subject of the email
    :param content: Plain-text or HTML content of the email
    """
    sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    from_email = Email(settings.FROM_EMAIL)
    to_email = To(to_email)
    subject = subject
    mail = Mail(from_email, to_email, subject, html_content=content)
    try:
        sg.client.mail.send.post(request_body=mail.get())
    except Exception as error:
        print(f"Error while sending email: {error}")


def send_verification_code_email(user_email: str, verification_code: str):
    content = f'Thank you for registering at our website. To confirm your account, please enter the following verification code:<br>' \
              f'<h2> {verification_code}</h2>'
    send_email(to_email=user_email, content=content, subject="Your verification code")


def generate_jwt_token(user_email: str, token_type: str) -> Dict[str, Optional[str]]:
    """
    Generate JWT tokens (access and refresh) based on the requested type.

    Args:
        user_id (int): The ID of the user.
        token_type (str): The type of tokens to generate.
                          "access" for access token only, "full" for both access and refresh tokens.

    Returns:
        Dict[str, Optional[str]]: Dictionary with "access_token" and optionally "refresh_token".
    """

    # Define payloads and expiration times for both tokens
    access_payload = {
        "email": user_email,
        "exp": time.time() + jwt_settings.ACCESS_TOKEN_EXPIRATION_TIME,
        "token_type": "access"
    }

    refresh_payload = {
        "email": user_email,
        "exp": time.time() + jwt_settings.REFRESH_TOKEN_EXPIRATION_TIME,
        "token_type": "refresh"
    }

    # Generate tokens
    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm=jwt_settings.ALGORITHM)
    refresh_token = None  # Default to None if only access token is requested

    # Generate refresh token if requested
    if token_type == "full":
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm=jwt_settings.ALGORITHM)

    # Return both tokens in a dictionary
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def verify_jwt_token(token: str, token_validation_type: str) -> Optional[dict]:
    """
    Verify the JWT token and return the decoded payload if valid.

    Args:
        token (str): The JWT token to validate.
        token_validation_type (str): Expected token type ("access" or "refresh").

    Returns:
        Optional[dict]: The decoded payload if the token is valid.

    Raises:
        HTTPException: If the token is invalid, expired, or missing the 'exp' field.
    """
    try:
        # Decode the token with secret key and algorithm
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[jwt_settings.ALGORITHM])

        # Check if 'exp' exists in the decoded token

        # Check if the token has expired
        if decoded_token["exp"] <= time.time():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")

        # Ensure token type matches expected token_validation_type
        if decoded_token.get("token_type") != token_validation_type:
            token_type_message = (
                "Please use refresh token for renewal" if token_validation_type == "refresh"
                else "Please use access token for authorization"
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=token_type_message)
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except KeyError as e:
        # Raise an error if 'exp' or other expected key is missing
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token is missing key: {str(e)}")
    except Exception as error:
        # Raise HTTPException with the actual exception message for unexpected errors
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))

# I am not using this function, but this is how you can use it for JWT authentication. Example:
# @user_router.get("/users/me", response_model=UserRead)  # Adjust the response model as needed
# async def get_user_info(token_data: dict = Depends(jwt_authentication("access")),
def jwt_authentication(token_validation_type: str):
    async def verify_jwt_dependency(authorization: str = Header(...)):
        # Expecting the header format: "Bearer <token>"
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization format. Expected 'Bearer <token>'"
            )
        # Extract token part from the "Bearer <token>" format
        token = authorization.split(" ")[1]
        return verify_jwt_token(token, token_validation_type)
    return verify_jwt_dependency


def send_reset_password_email(email: str, token: str):
    # Function to send email with SendGrid or any email service
    reset_link = f"{settings.FRONTEND_LINK}/reset-password?token={token}"
    # Code to send the email
    content = f'To reset your password, please paste the link below in your browser:<br>' \
              f'{reset_link}'
    send_email(content=content, subject="Your reset link", to_email=email)


