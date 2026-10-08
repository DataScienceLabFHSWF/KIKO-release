# backend/app/api/routes/authentication.py

import logging
from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.hash import pbkdf2_sha256
from datetime import datetime, timezone
from app.core import get_email_settings
from app.schemas import (
    UserLoginRequest, UserLoginResponse, UserRegisterRequest, 
    UserRegisterResponse, COMMON_ERROR_RESPONSES, ForgotPasswordRequest,
    ResetPasswordRequest, GenericSuccessResponse, ChangePasswordRequest,
    ChangePasswordResponse, VerifyEmailRequest, ResendVerificationEmailRequest,
)
from app.database import get_db
from app.services import (
    get_user_profile_by_email, update_user_profile_by_email, create_access_token,
    check_for_duplicates, create_user, create_template_courses_for_instructor,
    find_user_by_email_or_none, create_password_reset_token, get_valid_password_reset_token,
    get_request_lang, get_user_based_token_id, datetime_to_token_timestamp, require_role, 
    create_email_verification_token, get_valid_email_verification_token,
)
from app.services.email import EmailService
from app.utils import default_avatar_for_role

logger = logging.getLogger(__name__)

router = APIRouter(responses=COMMON_ERROR_RESPONSES)

async def send_email_verification_message(
    *,
    user,
    request: Request,
    response_language: str,
    db: AsyncSession,
) -> None:
    settings = get_email_settings()

    raw_token = await create_email_verification_token(
        user_id=user.user_id,
        db=db,
        expires_minutes=settings.email_verification_token_expire_minutes,
        requested_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    verification_link = (
        f"{settings.frontend_public_url}/verify-email"
        f"?token={raw_token}"
    )

    if settings.app_env in {"development", "dev", "local"}:
        logger.info("ℹ️ Email verification link: %s", verification_link)
    else:
        logger.info(
            "ℹ️ Email verification link generated for user_id=%s. Link is not logged in %s.",
            user.user_id,
            settings.app_env,
        )

    await EmailService().send_template_email(
        to_email=user.email,
        to_name=user.full_name,
        template_key="email_verification",
        language=response_language,
        context={
            "user_name": user.full_name,
            "verification_link": verification_link,
            "expires_minutes": settings.email_verification_token_expire_minutes,
        },
    )

def build_welcome_role_content(role: str, language: str) -> dict:
    normalized_language = "de" if language.startswith("de") else "en"

    content = {
        "en": {
            "Learner": {
                "role_title": "Learner",
                "role_intro": (
                    "As a learner, you can explore course material, work through "
                    "learning modules, ask grounded questions, and use KIKO to "
                    "better understand complex knowledge resources."
                ),
                "primary_actions": [
                    "Open your dashboard",
                    "Explore available courses",
                    "Use the chat assistant to ask questions about learning material",
                    "Track your learning progress",
                ],
            },
            "Instructor": {
                "role_title": "Instructor",
                "role_intro": (
                    "As an instructor, you can create and manage courses, upload "
                    "documents, prepare learning content, and support learners with "
                    "AI-assisted knowledge workflows."
                ),
                "primary_actions": [
                    "Open your instructor dashboard",
                    "Create or review your courses",
                    "Upload course documents",
                    "Prepare learning material for learners",
                ],
            },
            "Admin": {
                "role_title": "Admin",
                "role_intro": (
                    "As an admin, you can manage platform configuration, review "
                    "system-level settings, and support the operation of KIKO."
                ),
                "primary_actions": [
                    "Open the admin dashboard",
                    "Review platform configuration",
                    "Manage users and system settings",
                    "Monitor platform workflows",
                ],
            },
        },
        "de": {
            "Learner": {
                "role_title": "Lernende Person",
                "role_intro": (
                    "Als lernende Person können Sie Kursmaterialien ansehen, "
                    "Lernmodule bearbeiten, nachvollziehbare Fragen stellen und "
                    "KIKO nutzen, um komplexe Wissensressourcen besser zu verstehen."
                ),
                "primary_actions": [
                    "Dashboard öffnen",
                    "Verfügbare Kurse ansehen",
                    "Chat-Assistent für Fragen zu Lernmaterialien nutzen",
                    "Lernfortschritt verfolgen",
                ],
            },
            "Instructor": {
                "role_title": "Lehrende Person",
                "role_intro": (
                    "Als lehrende Person können Sie Kurse erstellen und verwalten, "
                    "Dokumente hochladen, Lerninhalte vorbereiten und Lernende mit "
                    "KI-gestützten Wissensabläufen unterstützen."
                ),
                "primary_actions": [
                    "Instructor-Dashboard öffnen",
                    "Kurse erstellen oder prüfen",
                    "Kursdokumente hochladen",
                    "Lernmaterialien für Lernende vorbereiten",
                ],
            },
            "Admin": {
                "role_title": "Administrator",
                "role_intro": (
                    "Als Administrator können Sie Plattformkonfigurationen verwalten, "
                    "Systemeinstellungen prüfen und den Betrieb von KIKO unterstützen."
                ),
                "primary_actions": [
                    "Admin-Dashboard öffnen",
                    "Plattformkonfiguration prüfen",
                    "Benutzer und Systemeinstellungen verwalten",
                    "Plattformabläufe überwachen",
                ],
            },
        },
    }

    return content[normalized_language].get(
        role,
        content[normalized_language]["Learner"],
    )

async def send_welcome_email_message(
    *,
    user,
    response_language: str,
) -> None:
    settings = get_email_settings()

    if not settings.welcome_email_enabled:
        logger.info(
            "ℹ️ Welcome email disabled. Skipping welcome email for user_id=%s",
            user.user_id,
        )
        return

    content = build_welcome_role_content(user.role, response_language)

    dashboard_link = f"{settings.frontend_public_url}/dashboard"

    await EmailService().send_template_email(
        to_email=user.email,
        to_name=user.full_name,
        template_key="welcome",
        language=response_language,
        context={
            "user_name": user.full_name,
            "user_role": user.role,
            "role_title": content["role_title"],
            "role_intro": content["role_intro"],
            "primary_actions": content["primary_actions"],
            "dashboard_link": dashboard_link,
        },
    )

@router.post(
    "/authenticate", 
    response_model=UserLoginResponse,
    operation_id="authenticate_user"
)
async def login(
    login_form_data: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
) -> UserLoginResponse:
    """Authenticate user and return access token."""
    
    logger.info(f"ℹ️ Attempting to authenticate user: {login_form_data.email}")
    
    user = await get_user_profile_by_email(login_form_data.email, db)  
    
    if not user or not pbkdf2_sha256.verify(login_form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="❌ Invalid credentials. Please try again."
        )

    if not user.email_verified:
        logger.warning(
            "⚠️ Login blocked because email is not verified. user_id=%s email=%s",
            user.user_id,
            user.email,
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address before logging in.",
        )

    # Update last login time
    # user.last_login = datetime.now(timezone.utc)
    
    # Update user profile in the database
    db_user = await update_user_profile_by_email(user, db)
    
    # Create access token
    token = await create_access_token(
        {
            "sub": str(db_user.user_id),
            "email": db_user.email,
            "role": db_user.role,
            "pwd_changed_at": datetime_to_token_timestamp(db_user.password_changed_at),
        }
    )

    response = UserLoginResponse(access_token=token, token_type="bearer")

    logger.info(f"✅ User authenticated successfully: {response}.")
    
    return response

@router.post(
    "/register", 
    response_model=UserRegisterResponse, 
    status_code=status.HTTP_201_CREATED,
    operation_id="register_user"
)
async def register(
    register_form_data: UserRegisterRequest,
    request: Request,
    response_language: str = Depends(get_request_lang), 
    db: AsyncSession = Depends(get_db)
) -> UserRegisterResponse:
    """Register a new user and return their profile info (excluding password)."""

    logger.info(f"ℹ️ Attempting to register user: {register_form_data.email}")
    
    # normalize email
    email = register_form_data.email.lower().strip()
    # username = register_form_data.username.strip()

    # Check duplicates
    is_user_exist = await check_for_duplicates(email=email, db=db)
    
    if is_user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="❌ Email already registered."
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
        email_verified=False,
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
            logger.info(f"✅ Created template course clones for new instructor: {new_user.email}")
        except Exception as e:
            logger.exception(f"❌ Instructor registered, but default course provisioning failed {new_user.email}: {e}")
            default_course_report = {
                "courses_created": 0,
                "documents_created": 0,
                "document_failures": [{"reason": str(e)}],
            }

    try:
        await send_email_verification_message(
            user=new_user,
            request=request,
            response_language=response_language,
            db=db,
        )
        logger.info("✅ Verification email prepared for user_id=%s", new_user.user_id)
    except Exception:
        logger.exception(
            "❌ User registered, but verification email failed for user_id=%s",
            new_user.user_id,
        )

    response = UserRegisterResponse(
        message="success",
        user={
            "user_id": new_user.user_id,
            # "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role,
            "full_name": new_user.full_name,
            "avatar": new_user.avatar,
            # "bio": new_user.bio,
            "email_verified": new_user.email_verified,
        },
        default_course_report=default_course_report
    )
    
    logger.info(f"✅ User registered with email: {response.user.email}, ID: {response.user.user_id}")
    
    return response

@router.post(
    "/forgot-password",
    response_model=GenericSuccessResponse,
    operation_id="request_password_reset",
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db),
) -> GenericSuccessResponse:
    """
    Request a password reset link.

    Always returns success, even if the email does not exist.
    This prevents account/email enumeration.
    """

    email = payload.email.lower().strip()

    logger.info("ℹ️ Password reset requested for email: %s", email)

    user = await find_user_by_email_or_none(email, db)

    if user:
        settings = get_email_settings()

        raw_token = await create_password_reset_token(
            user_id=user.user_id,
            db=db,
            expires_minutes=settings.password_reset_token_expire_minutes,
            requested_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        reset_link = (
            f"{settings.frontend_public_url}/reset-password"
            f"?token={raw_token}"
        )

        logger.info(f"ℹ️ Reset password link: {reset_link}")

        try:
            await EmailService().send_template_email(
                to_email=user.email,
                to_name=user.full_name,
                template_key="password_reset",
                language=response_language,
                context={
                    "user_name": user.full_name,
                    "reset_link": reset_link,
                    "expires_minutes": settings.password_reset_token_expire_minutes,
                },
            )

            logger.info("✅ Password reset email prepared for: %s", user.email)

        except Exception:
            # Do not reveal email delivery failures to the user here,
            # because that could indirectly reveal whether the account exists.
            logger.exception(
                "❌ Failed to send password reset email for user_id=%s",
                user.user_id,
            )

    return GenericSuccessResponse(message="success")

@router.post(
    "/reset-password",
    response_model=GenericSuccessResponse,
    operation_id="reset_password",
)
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> GenericSuccessResponse:
    """
    Reset password using a one-time reset token.
    """

    reset_token = await get_valid_password_reset_token(
        raw_token=payload.token,
        db=db,
    )

    user = await get_user_based_token_id(db, reset_token.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="❌ Invalid or expired password reset link.",
        )

    user.password = pbkdf2_sha256.hash(payload.new_password)
    user.password_changed_at = datetime.now(timezone.utc)
    reset_token.used_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(user)

    logger.info("✅ Password reset completed for user_id=%s", user.user_id)

    return GenericSuccessResponse(message="success")

@router.post(
    "/change-password",
    response_model=ChangePasswordResponse,
    operation_id="change_password",
)
async def change_password(
    payload: ChangePasswordRequest,
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    db: AsyncSession = Depends(get_db),
) -> ChangePasswordResponse:
    """
    Change password for a logged-in user.

    Available for Learner, Instructor, and Admin.
    Requires current password.
    Returns a new access token because old tokens become invalid after
    password_changed_at is updated.
    """

    db_user = await get_user_profile_by_email(user["email"], db)

    if not pbkdf2_sha256.verify(payload.current_password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="❌ Current password is incorrect.",
        )

    if pbkdf2_sha256.verify(payload.new_password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="❌ New password must be different from the current password.",
        )

    db_user.password = pbkdf2_sha256.hash(payload.new_password)
    db_user.password_changed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(db_user)

    new_token = await create_access_token(
        {
            "sub": str(db_user.user_id),
            "email": db_user.email,
            "role": db_user.role,
            "pwd_changed_at": datetime_to_token_timestamp(
                db_user.password_changed_at
            ),
        }
    )

    logger.info("✅ Password changed for user_id=%s", db_user.user_id)

    return ChangePasswordResponse(
        message="success",
        access_token=new_token,
        token_type="bearer",
    )

@router.post(
    "/verify-email",
    response_model=GenericSuccessResponse,
    operation_id="verify_email",
)
async def verify_email(
    payload: VerifyEmailRequest,
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db),
) -> GenericSuccessResponse:
    token = await get_valid_email_verification_token(
        raw_token=payload.token,
        db=db,
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="❌ Invalid or expired email verification link.",
        )

    user = await get_user_based_token_id(db, token.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="❌ Invalid or expired email verification link.",
        )

    now = datetime.now(timezone.utc)
    should_send_welcome_email = False

    if not user.email_verified:
        user.email_verified = True
        user.email_verified_at = now
        should_send_welcome_email = user.welcome_email_sent_at is None

    token.used_at = now

    await db.commit()
    await db.refresh(user)

    logger.info("✅ Email verified successfully for user_id=%s", user.user_id)

    if should_send_welcome_email:
        try:
            await send_welcome_email_message(
                user=user,
                response_language=response_language,
            )

            user.welcome_email_sent_at = datetime.now(timezone.utc)
            await db.commit()

            logger.info("✅ Welcome email sent for user_id=%s", user.user_id)

        except Exception:
            logger.exception(
                "❌ Email verified, but welcome email failed for user_id=%s",
                user.user_id,
            )

    return GenericSuccessResponse(message="success")

@router.post(
    "/resend-verification-email",
    response_model=GenericSuccessResponse,
    operation_id="resend_verification_email",
)
async def resend_verification_email(
    payload: ResendVerificationEmailRequest,
    request: Request,
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db),
) -> GenericSuccessResponse:
    email = payload.email.lower().strip()

    logger.info("ℹ️ Verification email resend requested for email=%s", email)

    user = await find_user_by_email_or_none(email, db)

    if user and not user.email_verified:
        try:
            await send_email_verification_message(
                user=user,
                request=request,
                response_language=response_language,
                db=db,
            )
            logger.info("✅ Verification email resent for user_id=%s", user.user_id)
        except Exception:
            logger.exception(
                "❌ Failed to resend verification email for user_id=%s",
                user.user_id,
            )

    return GenericSuccessResponse(message="success")
