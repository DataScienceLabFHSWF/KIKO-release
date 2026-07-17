import logging
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.hash import pbkdf2_sha256
from datetime import datetime, timezone
from app.schemas import Token, UserLogin, RegisterRequest
from app.database import get_db
from app.services import (
    get_user_profile_by_email, update_user_profile_by_email, create_access_token,
    check_for_duplicates, create_user, create_template_courses_for_instructor
)
from app.utils import default_avatar_for_role

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/authenticate", response_model=Token)
async def login(
    login_form_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return access token."""
    print(f"ℹ️ Attempting to authenticate user: {login_form_data.email}")
    
    user = await get_user_profile_by_email(login_form_data.email, db)  
    
    if not user or not pbkdf2_sha256.verify(login_form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    
    # Update last login time
    user.last_login = datetime.now(timezone.utc)
    
    # Update user profile in the database
    db_user = await update_user_profile_by_email(user, db)
    
    # Create access token
    token = await create_access_token({
        "email": db_user.email,
        "role": db_user.role
    })
    
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    register_form_data: RegisterRequest, 
    db: AsyncSession = Depends(get_db)
):
    """Register a new user and return their profile info (excluding password)."""

    print(f"ℹ️ Attempting to register user: {register_form_data.email}")
    
    # normalize email
    email = register_form_data.email.lower().strip()
    # username = register_form_data.username.strip()

    # Check duplicates
    is_user_exist = await check_for_duplicates(email=email, db=db)
    
    if is_user_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="ℹ️ Email already registered."
        )
    
    # Hash password
    hashed_pwd = pbkdf2_sha256.hash(register_form_data.password)
    # date_of_birth = register_form_data.date_of_birth
    role = register_form_data.role
    full_name = register_form_data.full_name.strip()
    # bio = register_form_data.bio.strip()
    # Auto avatar based on role + full_name
    avatar_url = default_avatar_for_role(role, full_name)

    new_user = await create_user(
        # username=username,
        email=email,
        # date_of_birth=date_of_birth,
        password=hashed_pwd,
        role=role,
        full_name=full_name,
        avatar=avatar_url,
        # bio=bio,
        db=db
    )

    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="❌ User creation failed due to an internal error."
        )
    
    default_course_report = None
    
    # Create template course clones for new instructors (for their own editing)
    # These clones won't be visible to learners (only system user's courses are)
    if new_user.role == "Instructor":
        try:
            default_course_report = await create_template_courses_for_instructor(
                user_id=new_user.user_id,
                db=db,
            )
            print(f"✅ Created template course clones for new instructor: {new_user.email}")
        except Exception as e:
            print(f"⚠️ Instructor registered, but default course provisioning failed {new_user.email}: {e}")
            default_course_report = {
                "courses_created": 0,
                "documents_created": 0,
                "document_failures": [{"reason": str(e)}],
            }
    
    print(f"✅ User registered with email: {new_user.email}, ID: {new_user.user_id}")
    
    # Return safe user info (no password)
    return {
        "message": "success",
        "user": {
            "user_id": new_user.user_id,
            # "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role,
            "full_name": new_user.full_name,
            "avatar": new_user.avatar,
            # "bio": new_user.bio,
        },
        "default_course_report": default_course_report
    }
