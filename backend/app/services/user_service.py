# backend/app/services/user_service.py

import logging
from sqlalchemy import select
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import UserModel, RoleModel, UserRoleModel
from app.schemas import UserProfileUpdateRequest
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

async def get_user_profile_by_email(
    email: str, 
    db: AsyncSession
) -> UserModel:
    """
    Retrieve user profile by email from the database.
    Raises HTTPException if user not found.
    """

    try:
        normalized_email = email.lower().strip()
        
        result = await db.execute(
            select(UserModel)
            .where(UserModel.email == normalized_email)
        )
        
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")
        
        return user
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"❌ Database error while fetching user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error: {str(e)}"
        )

async def update_user_profile_by_email(
    user: UserModel, 
    db: AsyncSession
) -> UserModel:
    """
    Update user profile in the database.
    Raises HTTPException if user not found.
    """

    try:
        db_user = await get_user_profile_by_email(user.email, db)
        
        # Update fields
        # db_user.email = user.email
        # db_user.full_name = user.full_name
        # db_user.username = user.username
        # db_user.date_of_birth = user.date_of_birth
        # db_user.avatar = user.avatar
        # db_user.bio = user.bio
        # db_user.role = user.role
        # db_user.password = user.password
        # db_user.joined = user.joined
        db_user.last_login = datetime.now(timezone.utc)
        
        await db.commit()
        
        await db.refresh(db_user)  # refresh object from DB after commit
        
        return db_user
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during profile update: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during profile update: {str(e)}"
        )

async def check_for_duplicates(
    email:str,
    db: AsyncSession
) -> UserModel:
    """
    Check for duplicate users by email or username.
    """

    try:
        result = await db.execute(
            select(UserModel)
            .where(UserModel.email == email)
        )

        user = result.scalar_one_or_none()
        return user
    except SQLAlchemyError as e:
        logger.error(f"❌ Database error during duplicate check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error during duplicate check: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error during duplicate check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during duplicate check: {str(e)}"
        )

async def create_user(
    # username: str, 
    email: str, 
    # date_of_birth, 
    password: str, 
    role: str, 
    full_name: str, 
    avatar: str, 
    # bio: str, 
    db: AsyncSession,
    email_verified: bool = False,
) -> UserModel:
    """
    Create a new user in the database.
    Raises HTTPException if user with email or username already exists.
    """
    
    try:
        logger.info(f"ℹ️ Creating user service: {email}")
        
        # Validate role exists
        role_row = (await db.execute(select(RoleModel).where(RoleModel.name == role))).scalar_one_or_none()
        
        if not role_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid role.")
        
        new_user = UserModel(
            # username=username,
            email=email,
            # date_of_birth=date_of_birth,
            password=password,
            role=role,
            full_name=full_name,
            avatar=avatar,
            # bio=bio,
            email_verified=email_verified,
            email_verified_at=datetime.now(timezone.utc) if email_verified else None,
        )

        db.add(new_user)
        await db.flush()  # to get new_user.user_id
        
        # Link role in UserRoleModel for your existing RBAC
        db.add(UserRoleModel(user_id=new_user.user_id, role_id=role_row.role_id))

        await db.commit()
        await db.refresh(new_user)  # refresh to get DB-generated fields like user_id
        
        logger.info(f"✅ User created with ID: {new_user.user_id}")
        return new_user
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during user creation: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during user creation: {str(e)}"
        )

async def get_system_user_id(db: AsyncSession) -> int | None:
    """
    Retrieve the system user ID.
    Returns None if system user doesn't exist or on database error.
    """
    try:
        result = await db.execute(
            select(UserModel.user_id).where(UserModel.email == "system@fh-swf.de")
        )
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"❌ Database error fetching system user: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error fetching system user: {e}")
        return None

async def update_current_user_profile(
    email: str,
    payload: UserProfileUpdateRequest,
    db: AsyncSession,
) -> UserModel:
    try:
        normalized_email = email.lower().strip()

        result = await db.execute(
            select(UserModel)
            .where(UserModel.email == normalized_email)
        )

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="❌ User not found.",
            )

        update_data = payload.model_dump(exclude_unset=True)

        if "full_name" in update_data and update_data["full_name"] is not None:
            user.full_name = update_data["full_name"].strip()

        if "avatar" in update_data:
            user.avatar = update_data["avatar"]

        await db.commit()
        await db.refresh(user)

        return user

    except HTTPException:
        raise

    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception("❌ Database error while updating user profile")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Database error while updating user profile.",
        ) from exc

async def find_user_by_email_or_none(
    email: str,
    db: AsyncSession,
) -> UserModel | None:
    """
    Safe lookup for flows like forgot-password.

    Do not raise 404 if the user does not exist, because that can reveal
    whether an email address is registered.
    """

    try:
        normalized_email = email.lower().strip()

        result = await db.execute(
            select(UserModel).where(UserModel.email == normalized_email)
        )

        return result.scalar_one_or_none()

    except SQLAlchemyError as exc:
        logger.exception("❌ Database error during safe user lookup")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Database error during user lookup.",
        ) from exc
