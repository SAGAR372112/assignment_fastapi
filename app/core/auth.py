from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from .config import Settings

class AuthManager:
    "Handle authentication and JWT tokens"
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None):
        "Create JWT access token"
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.settings.secret_key, algorithm=self.settings.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        "Verify JWT token"
        try:
            payload = jwt.decode(token, self.settings.secret_key, algorithms=[self.settings.algorithm])
            return payload
        except JWTError:
            raise Exception("Token validation failed")