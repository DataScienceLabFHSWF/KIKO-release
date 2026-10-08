# backend/app/schemas/app_config_schema.py
from typing import Literal
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

class AppConfigSchema(BaseModel):
    """AppConfigSchema defines the configuration settings for the application.
    It includes various parameters that control the behavior and features of the application.
    This model is used to manage application settings and can be extended as needed."""
    
    # Basic Configuration
    app_title: str = "Chat Assistant"
    chunk_size: int = 1200
    chunk_overlap: int = 200
    default_embedding_model: str = "nomic-embed-text:v1.5"
    default_llm_model: str = "llama3.3:70b"
    default_reasoning_model: str = "nemotron-3-super:120b"
    vector_store_base_path: str = "vector_store"
    batch_size: int = 100
    max_workers: int = 4
    be_cache_dir: str = "/backend/data/cache"
    fe_cache_dir: str = "/frontend/assets/cache"
    prompt_templates_dir: str = "/backend/app/core/prompts"
    pdf_dpi: int = 150
    debug_mode: bool = False
    default_folder_to_process: str = "/backend/data/Test/"

    # Course Generation Configuration
    course_generator_qa_count_min: int = 1
    course_generator_qa_count_default: int = 5
    course_generator_qa_count_max: int = 10
    course_generator_quiz_question_count_min: int = 1
    course_generator_quiz_question_count_default: int = 3
    course_generator_quiz_question_count_max: int = 4
    course_generator_quiz_option_count_min: int = 2
    course_generator_quiz_option_count_default: int = 3
    course_generator_quiz_option_count_max: int = 4
    course_generator_misconception_count_min: int = 1
    course_generator_misconception_count_default: int = 2
    course_generator_misconception_count_max: int = 4
    
    # State-of-the-Art VLM Configuration
    enable_vlm: bool = True
    preferred_vlm_model: str = "qwen2.5vl:7b"
    vlm_batch_size: int = 1
    vlm_max_tokens: int = 512
    vlm_temperature: float = 0.1
    extract_formulas: bool = False
    extract_forms: bool = False
    enable_form_filling: bool = False
    enable_highlighting: bool = True
    
    # Advanced OCR Configuration
    use_advanced_ocr: bool = False
    preferred_ocr_engine: str = "trocr"  # surya, trocr, tesseract_enhanced
    ocr_preprocessing: bool = True
    ocr_skew_correction: bool = True
    ocr_noise_reduction: bool = True
    ocr_language: str = "auto"
    
    # Multilingual Support
    enable_multilingual: bool = False
    language_detection: bool = True
    default_language: str = "deu"
    
    # Performance Configuration
    use_gpu_acceleration: bool = True
    precision: str = "float16"  # float16, float32, int8
    max_memory_usage_gb: int = 8
    enable_model_caching: bool = True
    
    # Document Processing
    extract_metadata: bool = True
    progressive_loading: bool = True
    progressive_chunk_size: int = 5
    enhanced_table_extraction: bool = True
    enable_document_classification: bool = True
    enable_layout_analysis: bool = True
    enable_confidence_scoring: bool = True
    
    # Resource Management
    memory_efficient_mode: bool = False
    cleanup_temp_files: bool = True
    max_document_size_mb: int = 100

class RuntimeEnvironmentResponse(BaseModel):
    """RuntimeEnvironmentResponse defines the details of the runtime environment in which the application is running.
    It includes information about the Python version and the platform (operating system) of the environment.
    This response is used to provide insights into the environment and can be helpful for debugging and support purposes."""
    
    python_version: str
    platform: str

class CudaInfoResponse(BaseModel):
    """CudaInfoResponse defines the details of CUDA support in the application environment.
    It includes information about whether CUDA is available, the version of CUDA, the device name, and the amount of memory available. 
    This response is used to provide insights into the GPU capabilities of the runtime environment."""
    
    enabled: bool
    version: str | None = None
    device: str | None = None
    memory_gb: int | float | None = None

class TorchModuleResponse(BaseModel):
    """TorchModuleResponse defines the availability and details of the PyTorch library in the application environment.
    It includes information about whether PyTorch is available, its version, and details about CUDA support if applicable. 
    This response is used to provide insights into the runtime environment and the capabilities of the underlying libraries."""
    
    is_available: bool
    cuda: CudaInfoResponse
    torch_version: str | None = None

class ModulesResponse(BaseModel):
    """ModulesResponse defines the availability and details of key modules and libraries used in the application.
    It includes information about the availability of PyTorch and its CUDA support, as well as the versions of these libraries. 
    This response is used to provide insights into the runtime environment and the capabilities of the underlying libraries."""
    
    torch: TorchModuleResponse

class FeatureFlagsResponse(BaseModel):
    """FeatureFlagsResponse defines the availability of certain features and integrations in the application.
    It includes flags for advanced models, specific integrations like Surya and CV2, and can
    be extended to include additional feature flags as needed."""
    
    is_advanced_models_available: bool
    is_surya_available: bool
    is_cv2_available: bool

class AppConfigResponse(BaseModel):
    """AppConfigResponse defines the response schema for application configuration API.
    It includes the runtime environment details, available modules and their status, 
    feature flags indicating the availability of certain features, and the application configuration settings."""
    
    environment: RuntimeEnvironmentResponse
    modules: ModulesResponse
    flags: FeatureFlagsResponse
    app_config: AppConfigSchema

class AdminEditableAppConfigSchema(BaseModel):
    """
    Admin-editable application configuration.

    Only expose safe operational fields.
    Do not expose paths, cache folders, memory limits, debug mode,
    or other infrastructure-sensitive settings.
    """

    model_config = ConfigDict(extra="forbid")

    default_embedding_model: str
    default_llm_model: str
    default_reasoning_model: str

    course_generator_qa_count_min: int
    course_generator_qa_count_default: int
    course_generator_qa_count_max: int

    course_generator_quiz_question_count_min: int
    course_generator_quiz_question_count_default: int
    course_generator_quiz_question_count_max: int

    course_generator_quiz_option_count_min: int
    course_generator_quiz_option_count_default: int
    course_generator_quiz_option_count_max: int

    course_generator_misconception_count_min: int
    course_generator_misconception_count_default: int
    course_generator_misconception_count_max: int

    enable_vlm: bool
    preferred_vlm_model: str

    use_advanced_ocr: bool
    preferred_ocr_engine: str
    ocr_preprocessing: bool
    ocr_skew_correction: bool
    ocr_noise_reduction: bool
    ocr_language: str

    enable_multilingual: bool
    language_detection: bool
    default_language: str

    @field_validator(
        "default_embedding_model",
        "default_llm_model",
        "default_reasoning_model",
        "preferred_vlm_model",
        "preferred_ocr_engine",
        "ocr_language",
        "default_language",
    )
    @classmethod
    def non_empty_string(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty.")
        return value

    @model_validator(mode="after")
    def validate_ranges(self):
        self._validate_range(
            label="Q&A pairs",
            minimum=self.course_generator_qa_count_min,
            default=self.course_generator_qa_count_default,
            maximum=self.course_generator_qa_count_max,
        )

        self._validate_range(
            label="Quiz questions",
            minimum=self.course_generator_quiz_question_count_min,
            default=self.course_generator_quiz_question_count_default,
            maximum=self.course_generator_quiz_question_count_max,
        )

        self._validate_range(
            label="Quiz options",
            minimum=self.course_generator_quiz_option_count_min,
            default=self.course_generator_quiz_option_count_default,
            maximum=self.course_generator_quiz_option_count_max,
        )

        self._validate_range(
            label="Misconceptions",
            minimum=self.course_generator_misconception_count_min,
            default=self.course_generator_misconception_count_default,
            maximum=self.course_generator_misconception_count_max,
        )

        if self.enable_vlm and not self.preferred_vlm_model:
            raise ValueError("Preferred VLM model is required when VLM is enabled.")

        if self.use_advanced_ocr and not self.preferred_ocr_engine:
            raise ValueError(
                "Preferred OCR engine is required when advanced OCR is enabled."
            )

        return self

    @staticmethod
    def _validate_range(
        label: str,
        minimum: int,
        default: int,
        maximum: int,
    ) -> None:
        if minimum < 1:
            raise ValueError(f"{label}: minimum must be at least 1.")

        if minimum > maximum:
            raise ValueError(f"{label}: minimum cannot be greater than maximum.")

        if default < minimum or default > maximum:
            raise ValueError(
                f"{label}: default must be between minimum and maximum."
            )

class AppConfigUpdateRequest(BaseModel):
    app_config: AdminEditableAppConfigSchema

class AppConfigUpdateResponse(AppConfigResponse):
    message: Literal["success"] = "success"
