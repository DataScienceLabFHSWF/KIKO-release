import os, logging, json, fitz, base64
from typing import Dict, List, Any
from PIL import Image
from io import BytesIO
from ollama import Client

logger = logging.getLogger(__name__)
DOCKER_OLLAMA_URL = os.getenv("DOCKER_OLLAMA_URL")
VLM_MODEL_NAME = os.getenv("VLM_MODEL_NAME")
VLM_EXTRACT_FORMULAS_PROMPT_NAME = "vlm_extract_formulas_prompt"
VLM_COMPRE_ANALY_PROMPT_NAME = "vlm_comprehensive_analysis_prompt"
VLM_EXTRACT_FORMS_PROMPT_NAME = "vlm_extract_forms_prompt"

class VLMProcessor:
    """Advanced VLM processor using state-of-the-art open-source models."""
    
    def __init__(self, config, prompt_manager, response_language: str):
        """Initialize with config, prompt manager, and response language. 
        The VLM client is lazily initialized on first use to allow async setup and to avoid loading models if not needed.
        config should contain 'app_config' with 'preferred_vlm_model', 'enable_vlm', 'vlm_temperature', and 'vlm_max_tokens' settings.
        prompt_manager should be an instance of PromptManager for loading prompt templates.
        response_language is the language code (e.g. 'eng', 'deu') for selecting the appropriate prompt template and 
        for guiding the VLM response language. The VLM model used is determined by the 'preferred_vlm_model' 
        setting in config, or falls back to the default VLM_MODEL_NAME. 
        The analyze_page method processes a PIL Image of a document page and returns a comprehensive analysis as text, 
        using the specified VLM model and prompt template."""
        
        self.config = config
        # Make sure we work with a dict
        self.app = (
            config["app_config"] 
            if isinstance(config.get("app_config"), dict) 
            else config.get("app_config").__dict__
        )
        self.flags = config.get("flags", {})
        self.response_language = response_language
        self.prompt_manager = prompt_manager

    def _get_ollama_client_and_model(self):
        """
        Returns (client, model_tag).
        - Host is taken from DOCKER_OLLAMA_URL or OLLAMA_HOST, default http://ollama:11434
        - Model tag from app.preferred_vlm_model or VLM_MODEL env, default 'qwen2.5vl:7b'
          (your Docker entrypoint already pulls the model)
        """
        print("ℹ️ Getting Ollama client and model tag.")        
        
        model_tag = (
            self.app.get("preferred_vlm_model")
            or VLM_MODEL_NAME
        )

        client = Client(host=DOCKER_OLLAMA_URL)
        print(f"✅ Initialized Ollama client for model: {client} FOR {model_tag}")
        return client, model_tag

    @staticmethod
    def _pil_to_base64(image: Image.Image) -> str:
        print("ℹ️ Converting PIL image to base64 string.")
        if image.mode != "RGB":
            image = image.convert("RGB")
        buf = BytesIO()
        image.save(buf, format="PNG")
        response = base64.b64encode(buf.getvalue()).decode("utf-8")
        print(f"✅ Successfully converted PIL image to base64 string.")
        return response
    
    def _pdf_to_images_fitz(self, file_path: str, dpi: int) -> List[Image.Image]:
        """Render PDF pages to PIL images using PyMuPDF (no Poppler needed)."""
        print(f"ℹ️ Converting PDF to images using fitz: {file_path} at {dpi} dpi")
        images: List[Image.Image] = []
        zoom = dpi / 72.0  # 72 dpi is the PDF default
        mat = fitz.Matrix(zoom, zoom)
        doc = fitz.open(file_path)
        print(f"ℹ️ Docs open to convert: {doc}")
        try:
            for page in doc:
                pix = page.get_pixmap(matrix=mat, alpha=False)
                mode = "RGB" if pix.n < 4 else "RGBA"
                img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
                images.append(img)
        finally:
            doc.close()
        print(f"✅ Successfully converted pdf to image: {images}")
        return images

    def _ollama_chat_image(self, client: Client, model_tag: str, image: Image.Image, prompt: str) -> str:
        """
        Single entry-point to query the Ollama VLM with one image and a text prompt.
        """
        try:
            print(f"ℹ️ Sending image and prompt to Ollama VLM model: {model_tag}")
            
            # Convert image to base64
            img_b64 = self._pil_to_base64(image)

            # Call Ollama chat endpoint
            options = {
                "temperature": self.app.get("vlm_temperature", 0.2),
                "num_predict": self.app.get("vlm_max_tokens", 512),
                "top_k": 50,
                "top_p": 0.95,
            }

            # Send request
            resp = client.chat(
                model=model_tag,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [img_b64],
                    }
                ],
                options=options,
            )

            # Extract text response
            text = resp.get("message", {}).get("content", "").strip()
            print(f"✅ Ollama VLM output ({model_tag}): {text[:200]}...")

            return text
        except Exception as e:
            print(f"❌ Ollama VLM processing error: {str(e)}")
            return f"Error in Ollama VLM processing: {str(e)}"

    async def _parse_form_output(self, output_text: str, page_idx: int) -> List[Dict[str, Any]]:
        """Parse VLM output to extract structured form field data."""
        
        fields: List[Dict[str, Any]] = []
        print(f"ℹ️ Parsing form output from VLM for page {page_idx + 1}.")
        
        try:
            # Try to parse as JSON first
            if output_text and (output_text.strip().startswith('{') or output_text.strip().startswith('[')):
                json_data = json.loads(output_text)
                if isinstance(json_data, dict) and 'fields' in json_data:
                    return json_data['fields']
                elif isinstance(json_data, list):
                    return json_data
        except:
            pass
        
        # Parse text format
        lines = (output_text or "").split('\n')
        current_field: Dict[str, Any] = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_field:
                    fields.append(current_field)
                    current_field = {}
                continue
            
            # Look for field patterns
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if 'field' in key or 'label' in key:
                    if current_field:
                        fields.append(current_field)
                    current_field = {
                        'label': value,
                        'value': '',
                        'field_type': 'text',
                        'page': page_idx + 1
                    }
                elif 'type' in key:
                    current_field['field_type'] = value
                elif 'value' in key:
                    current_field['value'] = value
                elif 'position' in key or 'location' in key:
                    current_field['bbox'] = value
        
        # Add the last field
        if current_field:
            fields.append(current_field)
        
        print(f"✅ Parsed {len(fields)} form fields from VLM output for page {page_idx + 1}.")
        return fields

    ###### High-level VLM processing methods ######
    async def analyze_document_with_advanced_vlm(self, image: Image.Image, page_idx: int) -> str:
        """Analyze document page with state-of-the-art VLM."""
        try:
            print(f"ℹ️ Analyzing document page {page_idx + 1} with advanced VLM.")
            # Get Ollama client and model
            client, model_tag = self._get_ollama_client_and_model()
            
            if not client or not model_tag:
                return "❌ VLM analysis not available."
            
            # Comprehensive analysis prompt
            analysis_prompt = self.prompt_manager.load_prompt_template(VLM_COMPRE_ANALY_PROMPT_NAME, self.response_language)

            if not analysis_prompt:
                return "❌ VLM analysis prompt not available."

            # Get VLM output
            output = self._ollama_chat_image(client, model_tag, image, analysis_prompt)

            print(f"✅ Completed VLM analysis for page {page_idx + 1} and got output: {output[:200]}...")
            return output
        except Exception as e:
            print(f"❌ VLM analysis failed for page {page_idx + 1}: {str(e)}")            
            return f"Error during VLM analysis: {str(e)}"

    async def extract_advanced_formulas(self, image, page_idx):
        """Extract mathematical formulas using advanced VLM understanding."""
        try:
            print(f"ℹ️ Extracting formulas from page {page_idx + 1} with advanced VLM.")
            # Get Ollama client and model
            client, model_tag = self._get_ollama_client_and_model()
            
            if not client or not model_tag:
                return "❌ VLM analysis not available."
            
            # Load formula extraction prompt
            formula_prompt = self.prompt_manager.load_prompt_template(VLM_EXTRACT_FORMULAS_PROMPT_NAME, self.response_language)

            if not formula_prompt:
                return "❌ Formula extraction prompt not available."

            # Get VLM output
            output = self._ollama_chat_image(client, model_tag, image, formula_prompt)

            print(f"✅ Completed formula extraction for page {page_idx + 1} and got output: {output[:200]}...")
            return output
        except Exception as e:
            print(f"❌ Formula extraction error for page {page_idx + 1}: {str(e)}")
            return f"Error during formula extraction: {str(e)}"
    
    async def extract_advanced_forms(self, image, page_idx):
        """Extract form fields using advanced VLM understanding."""
        try:
            print(f"ℹ️ Extracting form fields from page {page_idx + 1} with advanced VLM.")
            # Get Ollama client and model
            client, model_tag = self._get_ollama_client_and_model()

            if not client or not model_tag:
                return {"fields": []}
            
            # Load form extraction prompt
            form_prompt = self.prompt_manager.load_prompt_template(VLM_EXTRACT_FORMS_PROMPT_NAME, self.response_language)

            if not form_prompt:
                return {"fields": []}

            # Get VLM output
            raw = self._ollama_chat_image(client, model_tag, image, form_prompt)
            
            # Parse the output to extract structured form data
            fields = await self._parse_form_output(raw, page_idx)
            
            print(f"✅ Completed form extraction for page {page_idx + 1} and got fields: {fields}")

            return {"fields": fields}
        except Exception as e:
            print(f"❌ Form extraction error for page {page_idx + 1}: {str(e)}")            
            return {"fields": []}
        
    async def extract_vlm_from_pdf(self, file_path: str) -> List[str]:
        """Extract comprehensive document analysis using state-of-the-art VLM."""
        if not self.app.get("enable_vlm"):
            return []
        
        try:
            # Convert PDF pages to images
            dpi = self.app.get("pdf_dpi") 
            images = self._pdf_to_images_fitz(file_path, dpi=dpi)
            print(f"ℹ️ Convert PDF pages to images: {len(images)}")

            vlm_texts = []
            
            # Storage for extracted data
            formula_data = []
            form_fields_data = []
            for i, img in enumerate(images):
                if img.mode != "RGB":
                    img = img.convert("RGB")
                    
                # 1. Comprehensive document analysis
                page_analysis = await self.analyze_document_with_advanced_vlm(img, i)
                    
                # 2. Extract formulas if enabled
                formula_text = ""
                if self.app.get("extract_formulas"):
                    formula_text = await self.extract_advanced_formulas(img, i)
                    if formula_text:
                        formula_data.append({
                            "page": i + 1,
                            "formulas": formula_text
                        })
                    
                # 3. Extract form fields if enabled
                form_fields = {}
                if self.app.get("extract_forms"):
                    form_fields = await self.extract_advanced_forms(img, i)
                    if form_fields and "fields" in form_fields and form_fields["fields"]:
                        form_fields_data.append({
                            "page": i + 1,
                            "fields": form_fields["fields"]
                        })
                    
                # Combine all extracted information
                combined_text = f"[STATE-OF-THE-ART VLM ANALYSIS: PAGE {i+1}]\n\n{page_analysis}\n"
                    
                if formula_text:
                    combined_text += f"\n[MATHEMATICAL CONTENT]\n{formula_text}\n"
                    
                if form_fields and "fields" in form_fields and form_fields["fields"]:
                    combined_text += f"\n[FORM FIELDS]\n"
                    for field in form_fields["fields"]:
                        combined_text += f"- {field.get('label', 'Field')}: {field.get('value', '')} ({field.get('field_type', 'text')})\n"
                    
                vlm_texts.append(combined_text)
            
            return vlm_texts
        except Exception as e:
            print(f"❌ State-of-the-art VLM analysis failed for {file_path}: {str(e)}")
            return []
