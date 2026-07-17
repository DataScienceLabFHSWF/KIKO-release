# Mehrsprachige Unterstützung mit Open-Source-Tools
import os, torch, fasttext, urllib.request, logging
from langdetect import detect
from transformers import MarianMTModel, MarianTokenizer
from app.utils import get_device_and_dtype

logger = logging.getLogger(__name__)

class MultilingualProcessor:
    """Process multilingual documents using open-source tools."""
    
    def __init__(self, config):
        print("ℹ️ Initializing MultilingualProcessor with Open-Source tools...")
        self.config = config
        self.language_detector = None
        self.translation_models = {}
    
    async def detect_language(
        self, 
        text
    ):
        """Recognize the language of text with open source tools."""

        if not self.config.get("app_config").language_detection:
            print("⚠️ Speech recognition is disabled. Use default language.")
            return self.config.get("app_config").default_language
            
        if not text or len(text.strip()) < 10:
            print("⚠️ Text is too short for language detection. Use default language.")
            return self.config.get("app_config").default_language
            
        try:
            # Initialize speech detector if not already done 
            if self.language_detector is None:
                try:           
                    # Load pre-trained speech identification model
                    model_path = os.path.join(self.config.get("app_config").be_cache_dir, "lid.176.bin")

                    # Ensure cache directory exists
                    os.makedirs(os.path.dirname(model_path), exist_ok=True)
                                       
                    # Download if not already available
                    if not os.path.exists(model_path):
                        urllib.request.urlretrieve(
                            "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin", 
                            model_path
                        )
                    
                    # Lade das Modell
                    self.language_detector = fasttext.load_model(model_path)
                except ImportError:
                    # Fallback to langdetect (lighter alternative)
                    try:
                        # from langdetect import detect
                        self.language_detector = detect
                    except ImportError:
                        print("⚠️ No speech recognition library available. Use default language.")                        
                        return self.config.get("app_config").default_language
            
            # Erkenne Sprache
            if hasattr(self.language_detector, 'predict'):
                # Clean text for fastText
                clean_text = text.replace('\n', ' ')
                predictions = self.language_detector.predict(clean_text, k=1)
                lang_code = predictions[0][0].replace("__label__", "")
            else:
                # Verwende langdetect
                lang_code = self.language_detector(text)
            
            # Konvertiere zu standardisierten Codes
            lang_mapping = {
                "en": "eng",
                "de": "deu",
                # "fr": "fra",
                # "es": "spa",
                # "it": "ita",
                # "pt": "por",
                # "nl": "nld",
                # "ru": "rus",
                # "zh": "zho",
                # "ja": "jpn",
                # "ko": "kor",
                # "ar": "ara"
            }
            print(f"ℹ️ Recognized language: {lang_code} -> {lang_mapping.get(lang_code[:2], self.config.get('app_config').default_language)}")            
            return lang_mapping.get(lang_code[:2], self.config.get("app_config").default_language)
        except Exception as e:
            print(f"❌ Speech recognition error: {str(e)}")
            return self.config.get("app_config").default_language
    
    async def translate_text(
        self, 
        text, 
        source_lang, 
        target_lang="eng"
    ):
        """Translate text from source_lang to target_lang using open source tools."""
        
        if not text or source_lang == target_lang:
            print("⚠️ No translation needed (same source and target language).")
            return text
            
        try:
            # Lade Übersetzungsmodell falls nicht bereits geladen
            model_key = f"{source_lang}_{target_lang}"
            
            if model_key not in self.translation_models:
                try:               
                    # Sprachcode auf Modellnamen mappen
                    model_name = None
                    if source_lang == "deu" and target_lang == "eng":
                        model_name = "Helsinki-NLP/opus-mt-de-en"
                    elif source_lang == "fra" and target_lang == "eng":
                        model_name = "Helsinki-NLP/opus-mt-fr-en"
                    elif source_lang == "eng" and target_lang == "deu":
                        model_name = "Helsinki-NLP/opus-mt-en-de"
                    elif source_lang == "eng" and target_lang == "fra":
                        model_name = "Helsinki-NLP/opus-mt-en-fr"
                    
                    if model_name:
                        device, dtype = get_device_and_dtype()
                        
                        tokenizer = MarianTokenizer.from_pretrained(
                            model_name,
                            trust_remote_code=True,
                            use_fast=True
                        )

                        model = MarianMTModel.from_pretrained(
                            model_name,
                            device_map=None,
                            dtype=dtype,
                            trust_remote_code=True
                        ).to(device)
                        
                        self.translation_models[model_key] = (tokenizer, model)
                    else:
                        # Kein Modell für dieses Sprachpaar verfügbar
                        print(f"⚠️ No translation model available for {source_lang} to {target_lang}.")
                        return text
                except Exception as e:
                    print(f"❌ Error loading translation model: {str(e)}")              
                    return text
            
            # Übersetze den Text
            tokenizer, model = self.translation_models[model_key]
            
            # Teile Text in handhabbare Chunks, um OOM-Fehler zu vermeiden
            max_length = 512
            chunks = []
            
            for i in range(0, len(text), max_length):
                chunk = text[i:i+max_length]
                chunks.append(chunk)
            
            # Übersetze jeden Chunk
            translated_chunks = []
            
            for chunk in chunks:                
                inputs = tokenizer([chunk], return_tensors="pt", padding=True)
                
                with torch.no_grad():
                    translated_ids = model.generate(**inputs)
                    translated_text = tokenizer.batch_decode(translated_ids, skip_special_tokens=True)[0]
                    translated_chunks.append(translated_text)
            
            # Kombiniere die übersetzten Chunks
            print(f"ℹ️ Translated {len(chunks)} chunks from {source_lang} to {target_lang}.")
            return " ".join(translated_chunks)
        except Exception as e:
            print(f"❌ Translation error: {str(e)}")
            return text
