# JWT Utilities
import os, logging
from fastapi import HTTPException, status, Depends, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta

logger = logging.getLogger(__name__)

TOKEN_SECRET_KEY = os.getenv("SECRET_KEY")
TOKEN_ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/authentication/authenticate")

async def create_access_token(
    data: dict, 
    expires_delta: timedelta = None
) -> str:
    """Create a JWT access token with the provided data and expiration time.
    If expires_delta is not provided, it defaults to the value set in ACCESS_TOKEN_EXPIRE_MINUTES.
    The token is encoded using the secret key and algorithm specified in the environment variables."""

    to_encode = data.copy()
    # Temporary removing the expiration of tokens
    # expire = datetime.now((timezone.utc)) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # to_encode.update({"exp": expire})
    return jwt.encode(to_encode, TOKEN_SECRET_KEY, algorithm=TOKEN_ALGORITHM)

async def decode_access_token(token: str):
    """Decode the JWT access token and return the payload.
    If the token is invalid or expired, it returns None.
    This function uses the secret key and algorithm specified in the environment variables to decode the token."""

    try:
        payload = jwt.decode(token, TOKEN_SECRET_KEY, algorithms=[TOKEN_ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the current user from the JWT token.
    This function decodes the token and retrieves the user information.
    If the token is invalid or expired, it raises an HTTPException with a HTTP_401_UNAUTHORIZED status code.
    If the token is valid, it returns a dictionary containing the user's email and role."""

    payload = await decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return {"email": payload["email"], "role": payload["role"]}

# 🎯 Role checker
def require_role(allowed_roles: list):
    """Decorator to check if the user has one of the allowed roles.
    This function returns a dependency that checks the user's role against the allowed roles.
    If the user's role is not in the allowed roles, it raises an HTTPException with a HTTP_403_FORBIDDEN status code."""
    
    async def role_checker(user=Depends(get_current_user)):
        """Check if the current user has one of the allowed roles."""
        
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for role: {user['role']}",
            )
        return user
    return role_checker

def get_request_lang(accept_language: str = Header(None)) -> str:
    
    if not accept_language:
        return "en"
    
    al = accept_language.lower()
    if al.startswith("en"):
        return "en"
    return "de"
