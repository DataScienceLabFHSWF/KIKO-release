import torch, numpy as np, cv2 as cv, pytesseract, logging
import shutil
from PIL import Image
from transformers import (        
        # OCR Models
        TrOCRProcessor, VisionEncoderDecoderModel,
        # General models
        AutoModelForImageClassification, AutoImageProcessor
)
from app.utils import get_device_and_dtype

logger = logging.getLogger(__name__)

# If Tesseract binary is in PATH, tell pytesseract where it is so we avoid
# runtime errors inside containers or environments where PATH is different.
tess_path = shutil.which("tesseract")
if tess_path:
    pytesseract.pytesseract.tesseract_cmd = tess_path
    print(f"ℹ️ Tesseract OCR found at: {tess_path}")
else:
    print("❌ Tesseract OCR binary not found in PATH. OCR functionality may be limited.")

class OCRManager:
    """Advanced OCR manager using state-of-the-art open-source models."""
    
    def __init__(self, config):
        print("ℹ️ OCRManager: Initializing OCRManager with advanced preprocessing and classification capabilities.")
        self.config = config
        self.ocr_engines = {}
        self.document_classifiers = {}
        self.preprocessing_pipeline = None
        self.language_detector = None
        
        # Initialize advanced preprocessing
        if self.config.get("app_config").ocr_preprocessing:
            self.initialize_advanced_preprocessing()
            
    def initialize_advanced_preprocessing(self):
        """Initialize advanced image preprocessing pipeline."""

        if not self.config.get("flags").get("is_cv2_available"):
            print("❌ OCRManager: OpenCV is not available, cannot initialize advanced preprocessing.")
            return False
        
        print("ℹ️ OCRManager: Initializing advanced preprocessing pipeline for OCR.")

        try:
            def advanced_preprocess(image):
                """Advanced preprocessing pipeline for better OCR results."""
                print("ℹ️ OCRManager: Starting advanced preprocessing...")
                if isinstance(image, Image.Image):
                    image = np.asarray(image)
                
                # Convert to grayscale if needed
                if len(image.shape) == 3:
                    gray = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
                else:
                    gray = image.copy()
                
                # Noise reduction
                if self.config.get("app_config").ocr_noise_reduction:
                    denoised = cv.fastNlMeansDenoising(gray)
                else:
                    denoised = gray
                
                # Adaptive histogram equalization
                clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                enhanced = clahe.apply(denoised)
                
                # Skew correction
                if self.config.get("app_config").ocr_skew_correction:
                    corrected = self._correct_skew(enhanced)
                else:
                    corrected = enhanced
                
                # Adaptive thresholding
                binary = cv.adaptiveThreshold(
                    corrected, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv.THRESH_BINARY, 11, 2
                )
                
                # Morphological cleanup
                kernel = np.ones((1,1), np.uint8)
                cleaned = cv.morphologyEx(binary, cv.MORPH_OPEN, kernel)
                print("✅ Advanced preprocessing completed successfully.")                
                return cleaned
            
            self.preprocessing_pipeline = advanced_preprocess 
            print("✅ Advanced preprocessing pipeline initialized successfully.")
            return True
        except Exception as e:
            print(f"❌ Error initializing advanced preprocessing: {str(e)}")
            return False
    
    def _correct_skew(self, image):
        """Correct document skew using Hough Line Transform."""

        try:
            print("ℹ️ Starting skew correction...")
            # Edge detection
            edges = cv.Canny(image, 50, 150, apertureSize=3)
            
            # Hough Line Transform
            lines = cv.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                # Calculate average angle
                angles = []
                for line in lines[0:20]:  # Use first 20 lines
                    rho, theta = line[0]
                    angle = theta * 180 / np.pi
                    if angle < 45:
                        angles.append(angle)
                    elif angle > 135:
                        angles.append(angle - 180)
                
                if angles:
                    median_angle = np.median(angles)
                    if abs(median_angle) > 0.5:  # Only correct significant skew
                        # Rotate image
                        (h, w) = image.shape[:2]
                        center = (w // 2, h // 2)
                        M = cv.getRotationMatrix2D(center, median_angle, 1.0)
                        rotated = cv.warpAffine(image, M, (w, h), 
                                               flags=cv.INTER_CUBIC, 
                                               borderMode=cv.BORDER_REPLICATE)
                        print(f"✅ Skew corrected by {median_angle:.2f} degrees.")
                        return rotated
                else:
                    print("ℹ️ No significant skew detected, returning original image.")
                    return image
            else:
                print("ℹ️ No significant skew detected, returning original image.")
            return image
        except Exception as e:
            print(f"❌ Error correcting skew, returning original image. {str(e)}")
            return image
    
    async def get_advanced_document_classifier(self):
        """Get advanced document type classifier."""
        
        print("ℹ️ Initializing advanced document classifier...")
        if 'document_classifier' in self.document_classifiers:
            print("ℹ️ Using cached document classifier.")
            return self.document_classifiers['document_classifier']
        
        if not self.config.get("app_config").enable_document_classification:
            print("ℹ️ Document classification is disabled, using basic classifier.")
            return self._get_basic_classifier()
        
        try:
            if self.config.get("flags").get("is_advanced_models_available"):
                # Try to load document layout analysis model
                try:
                    print("ℹ️ Loading advanced document classifier using transformers...")
                    
                    device, dtype = get_device_and_dtype()
                    
                    # Document Image Transformer (DiT) model
                    model_name = "microsoft/dit-base-finetuned-rvlcdip"
                    
                    processor = AutoImageProcessor.from_pretrained(
                        model_name,
                        trust_remote_code=True,
                        use_fast=True
                    )

                    model = AutoModelForImageClassification.from_pretrained(
                        model_name,
                        device_map=None,
                        trust_remote_code=True
                    ).to(device)
                    
                    def classify_document(image):
                        """Classify document type using transformer model."""
                        print("ℹ️ Classifying document type using advanced model...")
                        inputs = processor(images=image, return_tensors="pt")
                        device = next(model.parameters()).device  # Get model device
                        for k in inputs:
                            if isinstance(inputs[k], torch.Tensor):
                                inputs[k] = inputs[k].to(device)
                        with torch.no_grad():
                            outputs = model(**inputs)
                            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                            predicted_class_idx = predictions.argmax().item()
                        
                        # Map to our document types
                        class_mapping = {
                            0: "scientific", 1: "form", 2: "general", 3: "table",
                            4: "general", 5: "general", 6: "general", 7: "general",
                            8: "general", 9: "general", 10: "general", 11: "general",
                            12: "scientific", 13: "general", 14: "general", 15: "general"
                        }
                        print(f"✅ Document classified as: {class_mapping.get(predicted_class_idx, 'general')}")
                        return class_mapping.get(predicted_class_idx, "general")
                    
                    self.document_classifiers['document_classifier'] = classify_document
                    print("✅ Advanced document classifier loaded successfully.")
                    return classify_document
                except Exception as e:
                    print(f"❌ Error loading advanced document classifier: {str(e)}")
                    return self._get_opencv_classifier()
            else:
                print("ℹ️ Advanced models not available, using OpenCV classifier.")
                return self._get_opencv_classifier()
        except Exception as e:
            print(f"❌ Error initializing document classifier: {str(e)}. ℹ️ Using basic document classifier as fallback.")                
            return self._get_basic_classifier()
    
    def _get_opencv_classifier(self):
        """Enhanced OpenCV-based document classifier."""
        print("ℹ️ Initializing OpenCV-based document classifier...")
        
        if not self.config.get("flags").get('is_cv2_available'):
            print("❌ OpenCV is not available, cannot initialize advanced preprocessing.")     
            return self._get_basic_classifier()
            
        def classify_document_opencv(image):
            try:
                print("ℹ️ Classifying document type using OpenCV...")
                if isinstance(image, Image.Image):
                    image = np.asarray(image)
                
                gray = cv.cvtColor(image, cv.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
                
                # Feature extraction
                features = {}
                
                # Line density analysis
                horizontal_kernel = cv.getStructuringElement(cv.MORPH_RECT, (25, 1))
                vertical_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, 25))
                
                _, thresh = cv.threshold(gray, 150, 255, cv.THRESH_BINARY_INV)
                horizontal_lines = cv.morphologyEx(thresh, cv.MORPH_OPEN, horizontal_kernel)
                vertical_lines = cv.morphologyEx(thresh, cv.MORPH_OPEN, vertical_kernel)
                
                features['horizontal_density'] = cv.countNonZero(horizontal_lines) / (gray.shape[0] * gray.shape[1])
                features['vertical_density'] = cv.countNonZero(vertical_lines) / (gray.shape[0] * gray.shape[1])
                
                # Mathematical symbol detection
                math_symbols = self._detect_math_symbols(gray)
                features['math_symbol_density'] = len(math_symbols) / (gray.shape[0] * gray.shape[1]) * 1000000
                
                # Form field detection
                form_fields = self._detect_form_fields_advanced(gray)
                features['form_field_count'] = len(form_fields)
                
                # Classification logic
                if features['horizontal_density'] > 0.01 and features['vertical_density'] > 0.01:
                    print("ℹ️ Classification logic table..")
                    return "table"
                elif features['form_field_count'] > 3:
                    print("ℹ️ Classification logic form..")
                    return "form"
                elif features['math_symbol_density'] > 5:
                    print("ℹ️ Classification logic scientific..")
                    return "scientific"
                else:
                    print("ℹ️ Classification logic general..")
                    return "general"                    
            except Exception as e:
                print(f"OpenCV classification error: {str(e)}")                                  
                return "general"
        print("✅ OpenCV-based document classifier initialized successfully.")
        return classify_document_opencv
    
    def _get_basic_classifier(self):
        """Basic fallback classifier."""
        print("ℹ️ Initializing basic document classifier as fallback.")
        def basic_classify(image):
            print("ℹ️ Using basic document classifier (general classification).")
            return "general"
        print("✅ Basic document classifier initialized successfully.")
        return basic_classify
    
    def _detect_math_symbols(self, gray_image):
        """Detect mathematical symbols and formulas."""
        print("ℹ️ Starting mathematical symbol detection...")
        try:
            symbols = []
            
            # Look for fraction-like structures
            horizontal_lines = cv.HoughLinesP(
                cv.Canny(gray_image, 50, 150), 1, np.pi/180, 
                threshold=50, minLineLength=20, maxLineGap=5
            )
            
            if horizontal_lines is not None:
                for line in horizontal_lines:
                    x1, y1, x2, y2 = line[0]
                    if abs(y2 - y1) < 5:  # Nearly horizontal
                        symbols.append(('fraction_line', (x1, y1, x2, y2)))
            
            print(f"✅ Detected {len(symbols)} mathematical symbols.")
            return symbols            
        except Exception:
            print("❌ Error detecting mathematical symbols.")
            return []
    
    def _detect_form_fields_advanced(self, gray_image):
        """Advanced form field detection."""
        print("ℹ️ Starting advanced form field detection...")
        try:
            fields = []
            
            # Rectangle detection for form fields
            print("ℹ️ Detecting contours for form fields...")
            contours, _ = cv.findContours(
                cv.threshold(gray_image, 127, 255, cv.THRESH_BINARY_INV)[1],
                cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE
            )
            
            for contour in contours:
                epsilon = 0.02 * cv.arcLength(contour, True)
                approx = cv.approxPolyDP(contour, epsilon, True)
                
                if len(approx) == 4:  # Quadrilateral
                    x, y, w, h = cv.boundingRect(contour)
                    area = w * h
                    
                    if 200 < area < 5000:
                        aspect_ratio = w / h if h > 0 else 0
                        
                        if 0.7 < aspect_ratio < 1.3:
                            fields.append(('checkbox', (x, y, w, h)))
                        elif aspect_ratio > 2:
                            fields.append(('input_field', (x, y, w, h)))
            print(f"✅ Detected {len(fields)} form fields.")
            return fields            
        except Exception:
            print("❌ Error detecting form fields.")
            return []
    
    def get_surya_ocr_engine(self, language="auto"):
        """Get Surya OCR engine - state-of-the-art open source OCR."""
        
        print("ℹ️ Initializing Surya OCR engine...")
        engine_key = f"surya_{language}"
        
        if engine_key in self.ocr_engines:
            print("ℹ️ Using cached Surya OCR engine.")
            return self.ocr_engines[engine_key]
        
        if not self.config.get("flags").get('is_surya_available'):
            print("❌ Surya OCR is not available, falling back to TrOCR.")
            return self.get_trocr_engine(language)
        
        try:
            print("ℹ️ Loading Surya OCR models (state-of-the-art)...")            
            det_processor, det_model = load_det_processor(), load_det_model()
            rec_model, rec_processor = load_rec_model(), load_rec_processor()
            print("✅ Successfully loaded Surya OCR models")
            
            def process_with_surya(image):
                try:
                    print("ℹ️ Processing image with Surya OCR...")
                    if isinstance(image, np.ndarray):
                        image = Image.fromarray(image)
                    
                    # Apply preprocessing if available
                    if self.preprocessing_pipeline:
                        processed_img = self.preprocessing_pipeline(image)
                        image = Image.fromarray(processed_img)
                    
                    # Run Surya OCR
                    print("ℹ️ Running OCR with Surya...")
                    predictions = run_ocr([image], [language], det_model, det_processor, rec_model, rec_processor)
                    
                    if predictions and len(predictions) > 0:
                        print("✅ OCR processing completed successfully.")
                        text_lines = []
                        for line in predictions[0].text_lines:
                            text_lines.append(line.text)
                        print(f"ℹ️ Extracted {len(text_lines)} text lines.")
                        return "\n".join(text_lines)
                    return ""                    
                except Exception as e:
                    print(f"❌ Surya OCR error: {str(e)}")
                    return ""
            # Store the Surya OCR engine            
            self.ocr_engines[engine_key] = process_with_surya
            print("✅ Surya OCR engine initialized successfully.")
            return process_with_surya            
        except Exception as e:
            print(f"❌ Surya OCR error: {str(e)}")           
            return self.get_trocr_engine(language)
    
    def get_trocr_engine(self, language="auto"):
        """Get enhanced TrOCR engine with latest models."""
        
        print("ℹ️ Initializing TrOCR engine...")
        engine_key = f"trocr_{language}"
        
        if engine_key in self.ocr_engines:
            print("ℹ️ Using cached TrOCR engine.")
            return self.ocr_engines[engine_key]
        
        if not self.config.get("flags").get('is_advanced_models_available'):
            print("❌ Advanced models are not available, falling back to Tesseract.")
            return self._get_tesseract_engine_enhanced(language)
        
        try:
            # Choose model based on language
            # TrOCR: Transformer-based Optical Character Recognition (large-sized model, fine-tuned on SROIE) 
            if language == "deu" or "multi" in language:
                model_name = "microsoft/trocr-large-printed"
            else:
                model_name = "microsoft/trocr-large-printed"
            
            device, dtype = get_device_and_dtype()
            
            processor = TrOCRProcessor.from_pretrained(
                model_name,
                trust_remote_code=True,
                use_fast=True
            )
            
            model = VisionEncoderDecoderModel.from_pretrained(
                model_name,
                device_map=None,
                dtype=dtype,
                trust_remote_code=True
            ).to(device)
            
            def process_with_trocr(image):
                try:
                    # Convert numpy → PIL
                    if isinstance(image, np.ndarray):
                        image = Image.fromarray(image)
                    
                    # Preprocess if available
                    if self.preprocessing_pipeline:
                        processed_img = self.preprocessing_pipeline(np.asarray(image))
                        # Handle grayscale output from preprocessing
                        if processed_img.ndim == 2:  # (H, W)
                            processed_img = np.stack([processed_img] * 3, axis=-1)  # → (H, W, 3)
                        image = Image.fromarray(processed_img)
                    
                    # Ensure final image is RGB
                    if image.mode != "RGB":
                        image = image.convert("RGB")
                    
                    # Process with TrOCR
                    pixel_values = processor(image, return_tensors="pt").pixel_values.to(device)
                    print(f"ℹ️ Pixel values dtype: {pixel_values.dtype}")
                    print(f"ℹ️ Model dtype: {next(model.parameters()).dtype}")
                    print(f"ℹ️ Model device: {next(model.parameters()).device}")
                    # Force pixel_values to float32 for TrOCR
                    pixel_values = pixel_values.to(device=device, dtype=torch.float16)
                    print(f"ℹ️ After converted to Pixel values dtype: {pixel_values.dtype} and {pixel_values.device}")
                    
                    with torch.no_grad():
                        generated_ids = model.generate(
                            pixel_values,
                            max_length=1000,
                            num_beams=5,
                            early_stopping=True
                        )
                    
                    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
                    return generated_text                    
                except Exception as e:
                    print(f"❌ TrOCR processing error: {str(e)}")
                    return ""
            
            print("✅ TrOCR engine initialized successfully.")            
            self.ocr_engines[engine_key] = process_with_trocr
            print(f"ℹ️ TrOCR engine for {language} loaded successfully.")
            return process_with_trocr            
        except Exception as e:
            print(f"❌ Error loading TrOCR engine: {str(e)}")            
            return self._get_tesseract_engine_enhanced(language)
    
    def _get_tesseract_engine_enhanced(self, language="auto"):
        """Enhanced Tesseract with better preprocessing."""

        try:   
            # Language mapping
            lang_map = {
                "auto": "eng",
                "deu": "deu",
                "fra": "fra", 
                "multi": "eng+deu+fra"
            }
            tesseract_lang = lang_map.get(language, "eng")
            
            def process_with_tesseract(image):
                try:
                    if isinstance(image, np.ndarray):
                        image = Image.fromarray(image)
                    
                    # Apply preprocessing if available
                    if self.preprocessing_pipeline:
                        processed_img = self.preprocessing_pipeline(image)
                        image = Image.fromarray(processed_img)
                    
                    # Enhanced Tesseract configuration
                    # Wrap the whitelist value in single quotes so embedded double-quotes
                    # inside the whitelist don't break Tesseract's parser. Escape the
                    # inner double-quote for the Python string.
                    custom_config = "--oem 3 --psm 6 -c tessedit_char_whitelist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzäöüßÄÖÜ.,!?;:()[]{}\"-+*/=<>@#$%&'"
                    
                    text = pytesseract.image_to_string(
                        image, 
                        lang=tesseract_lang, 
                        config=custom_config
                    )
                    return text                    
                except Exception as e:
                    print(f"❌ Enhanced Tesseract error: {str(e)}")
                    return ""
            print("✅ Enhanced Tesseract processing completed successfully.")            
            return process_with_tesseract            
        except ImportError:
            print("❌ Tesseract OCR is not available, cannot initialize enhanced Tesseract engine.")           
            return lambda image: ""
    
    async def get_best_ocr_engine(
        self, 
        document_type="general", 
        language="auto"
    ):
        """Get the best available OCR engine based on document type and language."""

        print(f"ℹ️ Selecting best OCR engine for document type '{document_type}' and language '{language}'...")
        
        # Initialize preprocessing if not done
        if self.preprocessing_pipeline is None and self.config.get("app_config").ocr_preprocessing:
            self.initialize_advanced_preprocessing()
        
        # Try engines in order of preference
        if self.config.get("app_config").preferred_ocr_engine == "surya":
            engines_to_try = [
                ("surya", self.get_surya_ocr_engine),
                ("trocr", self.get_trocr_engine),
                ("tesseract_enhanced", self._get_tesseract_engine_enhanced)
            ]
        elif self.config.get("app_config").preferred_ocr_engine == "trocr":
            engines_to_try = [
                ("trocr", self.get_trocr_engine),
                ("surya", self.get_surya_ocr_engine),
                ("tesseract_enhanced", self._get_tesseract_engine_enhanced)
            ]
        else:
            engines_to_try = [
                ("tesseract_enhanced", self._get_tesseract_engine_enhanced),
                ("trocr", self.get_trocr_engine),
                ("surya", self.get_surya_ocr_engine)
            ]
        
        for engine_name, engine_getter in engines_to_try:
            try:
                engine = engine_getter(language)
                if engine:
                    if self.config.get("app_config").debug_mode:
                        print(f"Using {engine_name} OCR engine")
                        # st.info(f"Using {engine_name} OCR engine")
                    return engine
            except Exception as e:
                print(f"❌ Failed to load {engine_name} OCR engine: {str(e)}")
                continue        
        # Last resort fallback
        print("❗ All advanced OCR engines failed, using basic fallback.")
        return lambda image: "OCR processing failed"
