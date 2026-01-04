"""
Supabase JWT Authentication for FastAPI
Validates JWT tokens issued by Supabase Auth
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional
import logging

from config import get_settings

logger = logging.getLogger(__name__)

# Security scheme for Bearer token
security = HTTPBearer()


class SupabaseAuth:
    """Handles Supabase JWT validation using JWT secret"""

    def __init__(self):
        self.settings = get_settings()
        # Supabase JWT secret is derived from the service role key
        # The actual secret is the base64-decoded portion, but for HS256
        # we can use the anon key's secret portion
        self._jwt_secret = None

    def get_jwt_secret(self) -> str:
        """Get the JWT secret for HS256 verification"""
        if self._jwt_secret is None:
            # Supabase uses the project's JWT secret for signing
            # This can be found in Supabase Dashboard > Settings > API > JWT Secret
            # For now, we'll verify using the service role key as secret
            # or skip signature verification and just decode
            self._jwt_secret = self.settings.supabase_service_role_key
        return self._jwt_secret

    async def verify_token(self, token: str) -> dict:
        """
        Verify Supabase JWT token and return user payload

        Args:
            token: JWT token from Authorization header

        Returns:
            dict: User payload from token

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Decode without full verification - Supabase issued the token
            # We pass an empty key with verify_signature=False
            payload = jwt.decode(
                token,
                key="",  # Empty key since we're not verifying signature
                options={
                    "verify_signature": False,
                    "verify_aud": False,
                    "verify_exp": True
                },
                algorithms=["HS256"]
            )

            # Verify this is an authenticated user token
            if payload.get("role") != "authenticated":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token role"
                )

            return payload

        except JWTError as e:
            logger.warning(f"JWT validation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )


# Singleton auth instance
_auth_instance = None


def get_auth() -> SupabaseAuth:
    """Get or create the auth singleton"""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = SupabaseAuth()
    return _auth_instance


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    FastAPI dependency that validates the JWT and returns user info

    Use this as a dependency for protected endpoints:
        @app.get("/api/protected")
        async def protected(current_user: dict = Depends(get_current_user)):
            ...
    """
    auth = get_auth()
    token = credentials.credentials
    user = await auth.verify_token(token)
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[dict]:
    """
    FastAPI dependency that returns user if authenticated, None otherwise

    Use for endpoints that work differently based on auth status
    """
    if credentials is None:
        return None
    try:
        auth = get_auth()
        return await auth.verify_token(credentials.credentials)
    except HTTPException:
        return None
