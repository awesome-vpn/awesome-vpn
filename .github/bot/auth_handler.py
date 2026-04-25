#!/usr/bin/env python3
"""Authentication Handler for GitHub Bot"""

import os
import json
import time
import logging
from datetime import datetime, timedelta

try:
    import jwt
except ImportError:
    jwt = None

from .otp_manager import OTPManager, RateLimiter, BackupCodeManager

logger = logging.getLogger(__name__)


class AuthHandler:
    """Handles OTP verification and JWT token generation"""
    
    def __init__(self, otp_secret=None, jwt_secret=None):
        """
        Initialize authentication handler
        
        Args:
            otp_secret: OTP secret from GitHub Secrets
            jwt_secret: JWT secret for token generation
        """
        if jwt is None:
            raise ImportError("PyJWT is required. Install: pip install PyJWT")
        
        self.otp_secret = otp_secret or os.getenv("BOT_OTP_SECRET")
        self.jwt_secret = jwt_secret or os.getenv("JWT_SECRET")
        
        if not self.otp_secret:
            raise ValueError("BOT_OTP_SECRET not configured")
        
        if not self.jwt_secret:
            raise ValueError("JWT_SECRET not configured")
        
        self.otp_manager = OTPManager(self.otp_secret)
        self.rate_limiter = RateLimiter(max_attempts=5, window_seconds=300)
        self.backup_manager = BackupCodeManager()
    
    def verify_otp(self, code, user_id="bot-user"):
        """
        Verify OTP code with rate limiting
        
        Args:
            code: 6-digit OTP code
            user_id: User identifier for rate limiting
        
        Returns:
            dict: {success: bool, message: str, token: str or None}
        """
        # Check rate limiting
        if not self.rate_limiter.is_allowed(user_id):
            retry_after = self.rate_limiter.get_retry_after(user_id)
            return {
                "success": False,
                "message": f"Too many attempts. Try again in {retry_after} seconds.",
                "token": None,
                "retry_after": retry_after
            }
        
        # Try regular OTP first
        if self.otp_manager.verify(code):
            token = self.generate_token(user_id)
            return {
                "success": True,
                "message": "OTP verified successfully",
                "token": token,
                "retry_after": 0
            }
        
        # Try backup code
        if self.backup_manager.use_backup_code(str(code)):
            logger.warning(f"Backup code used by {user_id}. Remaining: {self.backup_manager.remaining_codes()}")
            token = self.generate_token(user_id)
            return {
                "success": True,
                "message": f"Backup code verified. {self.backup_manager.remaining_codes()} codes remaining.",
                "token": token,
                "retry_after": 0
            }
        
        return {
            "success": False,
            "message": "Invalid OTP code",
            "token": None,
            "retry_after": self.rate_limiter.get_retry_after(user_id)
        }
    
    def generate_token(self, user_id, expires_in_hours=1):
        """
        Generate JWT token for authenticated session
        
        Args:
            user_id: User identifier
            expires_in_hours: Token expiration time
        
        Returns:
            str: JWT token
        """
        payload = {
            "user_id": user_id,
            "issued_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=expires_in_hours)).isoformat(),
            "type": "bot_auth"
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
        return token
    
    def verify_token(self, token):
        """
        Verify JWT token
        
        Args:
            token: JWT token
        
        Returns:
            dict: {valid: bool, payload: dict or None}
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return {"valid": True, "payload": payload}
        except jwt.ExpiredSignatureError:
            return {"valid": False, "payload": None, "error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"valid": False, "payload": None, "error": "Invalid token"}
    
    def get_otp_info(self):
        """Get OTP information"""
        return {
            "current_code": self.otp_manager.get_current_code(),
            "expires_in_seconds": self.otp_manager.get_time_remaining(),
            "backup_codes_remaining": self.backup_manager.remaining_codes()
        }


class OperationAuthorizer:
    """Authorizes specific operations based on token and role"""
    
    # Operation to required role mapping
    OPERATION_ROLES = {
        "crawl": "user",
        "commit": "maintainer",
        "create_pr": "maintainer",
        "create_release": "admin",
        "workflow_trigger": "maintainer"
    }
    
    USER_ROLES = {
        "bot-user": "maintainer",
        "admin": "admin"
    }
    
    def __init__(self, token):
        """
        Initialize authorizer with token
        
        Args:
            token: JWT token from authentication
        """
        self.token = token
        self.auth_handler = AuthHandler()
        
        result = self.auth_handler.verify_token(token)
        if not result["valid"]:
            raise ValueError(f"Invalid token: {result.get('error')}")
        
        self.payload = result["payload"]
    
    def can_perform(self, operation):
        """
        Check if user can perform operation
        
        Args:
            operation: Operation name
        
        Returns:
            bool: True if authorized, False otherwise
        """
        user_id = self.payload.get("user_id")
        user_role = self.USER_ROLES.get(user_id, "user")
        required_role = self.OPERATION_ROLES.get(operation, "user")
        
        # Role hierarchy: admin > maintainer > user
        role_levels = {"user": 1, "maintainer": 2, "admin": 3}
        
        return role_levels.get(user_role, 0) >= role_levels.get(required_role, 0)


if __name__ == "__main__":
    # Demo
    print("=== Auth Handler Demo ===\n")
    print("Note: Requires BOT_OTP_SECRET and JWT_SECRET environment variables")
