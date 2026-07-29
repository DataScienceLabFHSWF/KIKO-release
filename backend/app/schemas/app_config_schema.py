from pydantic import BaseModel

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
