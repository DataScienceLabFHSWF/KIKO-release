import sys, logging,torch, platform
from fastapi import HTTPException, status
from app.schemas import AppConfigSchema

logger = logging.getLogger(__name__)

# Check if the advanced models are available
try:
    print("ℹ️ Importing the transformers advanced models.")
    from transformers import (
        # VLM Models
        Qwen2VLForConditionalGeneration, AutoProcessor, AutoTokenizer,
        LlavaNextProcessor, LlavaNextForConditionalGeneration,
        Pix2StructProcessor, Pix2StructForConditionalGeneration,
        # OCR Models
        TrOCRProcessor, VisionEncoderDecoderModel,
        # General models
        AutoModel, AutoModelForCausalLM, AutoModelForImageClassification,
        AutoImageProcessor
    )

    ADVANCED_MODELS_AVAILABLE = True
    print("✅ Successfully installed the transformers advanced models.")
except ImportError as e:
    ADVANCED_MODELS_AVAILABLE = False
    print("❌ Error while installing the transformers advanced models.")

try:
    print("ℹ️ Importing the Surya OCR models.")
    # State-of-the-art OCR
    from surya.ocr import run_ocr
    from surya.model.detection.segformer import load_model as load_det_model, load_processor as load_det_processor
    from surya.model.recognition.model import load_model as load_rec_model
    from surya.model.recognition.processor import load_processor as load_rec_processor

    SURYA_AVAILABLE = True
    print("✅ Successfully installed the Surya OCR models.")
except ImportError:
    SURYA_AVAILABLE = False
    print("ℹ️ Installing the Surya OCR models failed. Some features may not be available.")

try:
    print("ℹ️ Importing the cv2 and pytesseract models.")
    import cv2 as cv
    import pytesseract

    CV2_AVAILABLE = True
    print("✅ Successfully installed the cv2 and pytesseract models.")
except ImportError:
    CV2_AVAILABLE = False
    print("ℹ️ Installing the cv2 and pytesseract models failed.")

logger = logging.getLogger(__name__)

async def get_app_config_and_libary_available() -> dict:
    """Fetch application configuration and library availability."""
    try:
        config = AppConfigSchema()
            
        if config is not None:
            
            configurations = {
                "environment": {
                    "python_version": sys.version.split()[0],
                    "platform": platform.platform(),
                },
                "modules": {
                    "torch": {
                        "is_available": torch.cuda.is_available(),
                        "cuda": {
                            "enabled": torch.cuda.is_available(),
                            "version": torch.version.cuda if torch.cuda.is_available() else None,
                            "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                            "memory_gb": torch.cuda.get_device_properties(0).total_memory // (1024**3) if torch.cuda.is_available() else None
                        },
                        "torch_version": torch.__version__,
                    },                   
                },
                "flags": {
                    "is_advanced_models_available": ADVANCED_MODELS_AVAILABLE,
                    "is_surya_available": SURYA_AVAILABLE,
                    "is_cv2_available": CV2_AVAILABLE
                },
                "app_config": config,
            }
            return configurations
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="❌ AppConfigSchema is not available."
            )       
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"❌ Error while fetching app configuration and library availability: {str(e)}"
            )
