# backend/app/services/configuration_service.py

import logging, platform, sys, torch
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AppConfigurationModel
from app.schemas import AppConfigSchema, AdminEditableAppConfigSchema

logger = logging.getLogger(__name__)

try:
    logger.info("ℹ️ Importing the transformers advanced models.")
    from transformers import (
        Qwen2VLForConditionalGeneration,
        AutoProcessor,
        AutoTokenizer,
        LlavaNextProcessor,
        LlavaNextForConditionalGeneration,
        Pix2StructProcessor,
        Pix2StructForConditionalGeneration,
        TrOCRProcessor,
        VisionEncoderDecoderModel,
        AutoModel,
        AutoModelForCausalLM,
        AutoModelForImageClassification,
        AutoImageProcessor,
    )

    ADVANCED_MODELS_AVAILABLE = True
    logger.info("✅ Successfully installed the transformers advanced models.")
except ImportError:
    ADVANCED_MODELS_AVAILABLE = False
    logger.error("❌ Error while importing the transformers advanced models.")

try:
    logger.info("ℹ️ Importing the Surya OCR models.")
    from surya.ocr import run_ocr
    from surya.model.detection.segformer import (
        load_model as load_det_model,
        load_processor as load_det_processor,
    )
    from surya.model.recognition.model import load_model as load_rec_model
    from surya.model.recognition.processor import load_processor as load_rec_processor

    SURYA_AVAILABLE = True
    logger.info("✅ Successfully installed the Surya OCR models.")
except ImportError:
    SURYA_AVAILABLE = False
    logger.warning("ℹ️ Surya OCR is not available.")

try:
    logger.info("ℹ️ Importing cv2 and pytesseract.")
    import cv2 as cv
    import pytesseract

    CV2_AVAILABLE = True
    logger.info("✅ Successfully installed cv2 and pytesseract.")
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("ℹ️ cv2 or pytesseract is not available.")

EDITABLE_APP_CONFIG_FIELDS = set(AdminEditableAppConfigSchema.model_fields.keys())

def _clean_overrides(raw_config: dict | None) -> dict:
    if not isinstance(raw_config, dict):
        return {}

    return {
        key: value
        for key, value in raw_config.items()
        if key in EDITABLE_APP_CONFIG_FIELDS
    }

async def get_effective_app_config(
    db: AsyncSession | None = None,
) -> AppConfigSchema:
    """
    Return default config merged with admin-managed overrides.
    """

    default_config = AppConfigSchema()
    default_data = default_config.model_dump()

    if db is None:
        return default_config

    result = await db.execute(
        select(AppConfigurationModel)
        .where(
            AppConfigurationModel.config_id == 1
        )
    )

    row = result.scalar_one_or_none()

    if not row:
        return default_config

    overrides = _clean_overrides(row.config_json)

    return AppConfigSchema.model_validate(
        {
            **default_data,
            **overrides,
        }
)

async def update_app_config_for_admin(
    editable_config: AdminEditableAppConfigSchema,
    updated_by: int,
    db: AsyncSession,
) -> dict:
    """
    Persist admin-editable app configuration overrides.

    Stores only whitelisted editable fields.
    Returns the full effective AppConfigResponse shape.
    """

    try:
        overrides = editable_config.model_dump()

        result = await db.execute(
            select(AppConfigurationModel).where(
                AppConfigurationModel.config_id == 1
            )
        )
        row = result.scalar_one_or_none()

        if row is None:
            row = AppConfigurationModel(
                config_id=1,
                config_json=overrides,
                updated_by=updated_by,
            )
            db.add(row)
        else:
            row.config_json = overrides
            row.updated_by = updated_by

        await db.commit()

        return await get_app_config_and_libary_available(db=db)

    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception("❌ Failed to update application configuration")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error while updating app configuration: {exc}",
        ) from exc

async def get_app_config_and_libary_available(
    db: AsyncSession | None = None,
) -> dict:
    """
    Fetch runtime environment, feature flags, and effective app configuration.

    Name kept as-is to avoid breaking existing imports.
    """

    try:
        config = await get_effective_app_config(db=db)

        return {
            "environment": {
                "python_version": sys.version.split()[0],
                "platform": platform.platform(),
            },
            "modules": {
                "torch": {
                    "is_available": torch.cuda.is_available(),
                    "cuda": {
                        "enabled": torch.cuda.is_available(),
                        "version": (
                            torch.version.cuda
                            if torch.cuda.is_available()
                            else None
                        ),
                        "device": (
                            torch.cuda.get_device_name(0)
                            if torch.cuda.is_available()
                            else None
                        ),
                        "memory_gb": (
                            torch.cuda.get_device_properties(0).total_memory
                            // (1024**3)
                            if torch.cuda.is_available()
                            else None
                        ),
                    },
                    "torch_version": torch.__version__,
                }
            },
            "flags": {
                "is_advanced_models_available": ADVANCED_MODELS_AVAILABLE,
                "is_surya_available": SURYA_AVAILABLE,
                "is_cv2_available": CV2_AVAILABLE,
            },
            "app_config": config,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("❌ Error while fetching app configuration")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "❌ Error while fetching app configuration and "
                f"library availability: {exc}"
            ),
        ) from exc
