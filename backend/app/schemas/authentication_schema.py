from pydantic import BaseModel

class Token(BaseModel):
    """Token Schema for user authentication.
    This Schema is used to represent the access token returned upon successful user authentication.
    It includes the access token string and the token type."""
    
    access_token: str
    token_type: str
