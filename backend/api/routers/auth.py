from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth_service import (
    auth_service, 
    UserLogin, 
    UserRegister, 
    UserResponse, 
    Token
)
from services.supabase_service import supabase_service
import logging

logger = logging.getLogger("auth_router")
router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """
    Register a new user account.
    """
    try:
        # Check if user exists
        existing_user = supabase_service.client.table("users") \
            .select("id") \
            .eq("email", user_data.email) \
            .execute()
        
        if existing_user.data:
            raise HTTPException(
                status_code=400, 
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = auth_service.hash_password(user_data.password)
        
        # Create user in database
        user = supabase_service.client.table("users").insert({
            "email": user_data.email,
            "password_hash": hashed_password,
            "full_name": user_data.full_name,
            "role": "analyst"
        }).execute()
        
        if not user.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create user"
            )
        
        user_obj = user.data[0]
        logger.info(f"New user registered: {user_data.email}")
        
        return UserResponse(
            id=user_obj["id"],
            email=user_obj["email"],
            full_name=user_obj["full_name"],
            role=user_obj["role"]
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Login with email and password.
    Returns access and refresh tokens.
    """
    try:
        # Get user from database
        user = supabase_service.client.table("users") \
            .select("id, email, password_hash") \
            .eq("email", credentials.email) \
            .execute()
        
        if not user.data:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        user_obj = user.data[0]
        
        # Verify password
        if not auth_service.verify_password(
            credentials.password, 
            user_obj["password_hash"]
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        # Create tokens
        tokens = auth_service.create_tokens(user_obj["id"], user_obj["email"])
        logger.info(f"User logged in: {credentials.email}")
        
        return tokens
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/refresh", response_model=Token)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Refresh access token using refresh token.
    """
    try:
        payload = auth_service.verify_token(credentials.credentials)
        
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )
        
        email = payload.get("sub")
        user_id = payload.get("user_id")
        
        if not email:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload"
            )
        
        # Create new tokens
        tokens = auth_service.create_tokens(user_id, email)
        logger.info(f"Token refreshed for: {email}")
        
        return tokens
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current user profile.
    """
    try:
        payload = auth_service.verify_token(credentials.credentials)
        
        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        
        email = payload.get("sub")
        user_id = payload.get("user_id")
        
        # Fetch user from database
        user = supabase_service.client.table("users") \
            .select("id, email, full_name, role") \
            .eq("id", user_id) \
            .execute()
        
        if not user.data:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        user_obj = user.data[0]
        return UserResponse(
            id=user_obj["id"],
            email=user_obj["email"],
            full_name=user_obj["full_name"],
            role=user_obj["role"]
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user")

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout (token invalidation handled client-side).
    """
    try:
        payload = auth_service.verify_token(credentials.credentials)
        if payload:
            email = payload.get("sub")
            logger.info(f"User logged out: {email}")
        
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")
