import os, fitz, numpy as np, logging
from typing import Dict, Any
from PIL import Image
from .ocr_manager import OCRManager
from .vlm_processor import VLMProcessor
from .prompt_manager import PromptManager
from .multilingual_processor import MultilingualProcessor
from .pdf_metadata_extractor import PDFMetadataExtractor
from .table_extractor import TableExtractor
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL")

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """State-of-the-art document processor with all advanced features."""
    
    def __init__(self, config, response_language: str):
        print(f"ℹ️ DocumentProcessor core: Initializing DocumentProcessor with advanced features.")
        self.config = config
        self.ocr_manager = OCRManager(config)
        self.vlm_processor = VLMProcessor(config, PromptManager(config), response_language)
        self.multilingual = MultilingualProcessor(config)
        self.metadata_extractor = PDFMetadataExtractor(config)
        self.table_extractor = TableExtractor(config)
        
    async def process_document(
        self, 
        org_file_name: str, 
        content_hash: str, 
        file_path: str
    ) -> Dict[str, Any]:
        """Process document with state-of-the-art AI models."""
        try:
            # Open document
            doc = fitz.open(file_path)
            
            # Extract metadata if enabled
            metadata = {}
            if self.config.get("app_config").extract_metadata:
                print(f"ℹ️ Core: Extracting document metadata from file path: {file_path}")
                metadata = await self.metadata_extractor.extract_metadata(file_path)
            
            # Process with state-of-the-art models
            chunks = []
            metadatas = []
            all_tables = []
            
            print(f"ℹ️ Processing {len(doc)} pages with state-of-the-art AI...")

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size= self.config.get("app_config").chunk_size,
                chunk_overlap= self.config.get("app_config").chunk_overlap
            )
            
            # Get advanced document classifier
            doc_classifier = await self.ocr_manager.get_advanced_document_classifier()
            
            for page_idx, page in enumerate(doc):
                
                print(f"ℹ️ Processing page {page_idx + 1}/{len(doc)}.")

                # Extract text directly from PDF
                print(f"ℹ️ Extracting text from page {page_idx + 1}.")
                page_text = page.get_text()
                print(f"✅ Extracted {len(page_text)} characters from page {page_idx + 1}")
                
                # Language detection
                page_language = "auto"
                if self.config.get("app_config").language_detection and page_text.strip():
                    print(f"ℹ️ Detecting page language for page {page_idx + 1}.")
                    page_language = await self.multilingual.detect_language(page_text)
                    print(f"✅ Detected language: {page_language}")
                
                # Render page as high-quality image
                print(f"ℹ️ Rendering page {page_idx + 1} as high-quality image for OCR.")
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x resolution
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                print(f"✅ Rendered page {page_idx + 1} as image ({pix.width}x{pix.height})")
                
                # Advanced document type classification
                doc_type = "general"
                if self.config.get("app_config").enable_document_classification:
                    print(f"ℹ️ Classifying document type for page {page_idx + 1}.")
                    doc_type = doc_classifier(img)
                    print(f"✅ Classified document type: {doc_type}")
                
                # Get best OCR engine for this document type
                ocr_engine = await self.ocr_manager.get_best_ocr_engine(doc_type, page_language)
                print(f"✅ Selected OCR engine: {ocr_engine}")
                
                # Apply advanced OCR if needed                
                enhanced_text = ""
                if self.config.get("app_config").use_advanced_ocr and len(page_text.strip()) < 100:
                    print(f"ℹ️ Applying advanced OCR for page {page_idx + 1}.")
                    enhanced_text = ocr_engine(img)
                    print(f"✅ Enhanced OCR extracted {len(enhanced_text)} characters")
                
                # Enhanced table extraction
                page_tables = []
                if self.config.get("app_config").enhanced_table_extraction:
                    print(f"ℹ️ Applying Enhanced table extraction for page {page_idx + 1}.")

                    print(f"ℹ️ Detecting tables on the page {page_idx + 1}...")
                    table_regions = await self.table_extractor.detect_tables(img)
                    
                    for i, table_bbox in enumerate(table_regions):
                        print(f"ℹ️ Extracting table structure from bbox {table_bbox} on page {page_idx + 1}...")
                        table_data = await self.table_extractor.extract_table_structure(img, table_bbox)
                        if table_data and "error" not in table_data:
                            page_tables.append({
                                "id": f"table_{page_idx+1}_{i+1}",
                                "page": page_idx + 1,
                                "bbox": table_bbox,
                                "structure": table_data
                            })
                            print(f"✅ Extracted table {i+1} structure from page {page_idx + 1}")
                        print(f"ℹ️ Finished extracting tables from page {page_idx + 1}. Found {len(page_tables)} tables.")
                    print(f"✅ Total tables extracted from page {page_idx + 1}: {len(page_tables)}")
                
                all_tables.extend(page_tables)

                # Combine text sources intelligently
                combined_text = page_text
                
                # Use enhanced OCR if it provides better results
                if enhanced_text and len(enhanced_text) > len(page_text) * 1.2:
                    print(f"ℹ️ Using enhanced OCR text for page {page_idx + 1}.")
                    combined_text = enhanced_text
                elif enhanced_text and len(page_text.strip()) < 50:
                    print(f"ℹ️ Using enhanced OCR text for page {page_idx + 1} due to low original text length.")
                    combined_text = enhanced_text
                
                # Add structured table data
                if page_tables:
                    print(f"ℹ️ Add structured table data for page {page_idx + 1}.")
                    table_text = "\n\n[EXTRACTED TABLES]\n"
                    for table in page_tables:
                        table_text += f"\n=== Table {table['id']} ===\n"
                        if "text" in table["structure"]:
                            table_text += table["structure"]["text"] + "\n"
                        table_text += f"Location: Page {table['page']}, Bbox: {table['bbox']}\n"
                    combined_text += table_text
                                
                # Translation if needed
                if (self.config.get("app_config").enable_multilingual and 
                    page_language != "eng" and 
                    page_language != self.config.get("app_config").default_language and
                    page_language != "auto"):

                    print(f"ℹ️ Translating text from {page_language} to English for page {page_idx + 1}.")
                    # Translate text to Target Language
                    target_lang = getattr(self.config.get("app_config"), "default_language", None) or "eng"
                    
                    translated_text = await self.multilingual.translate_text(
                        combined_text,
                        source_lang=page_language,
                        target_lang= target_lang
                    )                    
                    if translated_text and len(translated_text) > 0:
                        print(f"✅ Translated text from {page_language} to English for page {page_idx + 1}.")
                        combined_text = (f"[TRANSLATED FROM {page_language.upper()}]\n{translated_text}\n\n" +
                                        f"[ORIGINAL TEXT]\n{combined_text}")
                        print(f"ℹ️ Combined text for page {page_idx + 1} after translation: {len(combined_text)} characters")
                
                # Text chunking
                print(f"ℹ️ Splitting text into chunks for page {page_idx + 1}.")
                if combined_text.strip():
                    page_chunks = text_splitter.split_text(combined_text)
                    chunks.extend(page_chunks)
                    
                    # Enhanced metadata with confidence scoring
                    confidence_score = 0.95  # High confidence for state-of-the-art processing
                    if enhanced_text and len(enhanced_text) > len(page_text):
                        confidence_score = 0.85  # Slightly lower for OCR-heavy pages
                    
                    for _ in page_chunks:
                        metadatas.append({
                            "source": org_file_name,
                            "content_hash": content_hash,
                            "file_path": file_path,
                            "download_url": f"{BACKEND_API_URL}/api/files/{content_hash}/download" if content_hash else None,
                            "preview_url": f"{BACKEND_API_URL}/api/files/{content_hash}/page/{page_idx + 1}.png" if content_hash else None,
                            "page": page_idx + 1,
                            "total_pages": len(doc),
                            "language": page_language,
                            "document_type": doc_type,
                            "has_tables": page_tables,
                            "processing_method": "state_of_the_art",
                            "confidence_score": confidence_score,
                            "ocr_engine": self.config.get("app_config").preferred_ocr_engine,
                            "vlm_model": self.config.get("app_config").preferred_vlm_model
                        })
                    print(f"✅ Processed page {page_idx + 1} with {len(page_chunks)} chunks created.")
                else:
                    print(f"ℹ️ No text extracted from page {page_idx + 1}. Skipping Text chunking.")
            
            print(f"✅ Finished processing document {file_path}. Total pages: {len(doc)}, Total chunks: {len(chunks)}")

            # Prepare result
            print("ℹ️ Preparing final result with chunks, metadata, tables, and processing_stats.")
            result = {
                "doc_metadata": metadata,
                "chunks": chunks,
                "metadatas": metadatas,
                "tables": all_tables,
                "processing_stats": {
                    "total_pages": len(doc),
                    "total_chunks": len(chunks),
                    "average_confidence": np.mean([m.get("confidence_score", 0.8) for m in metadatas]),
                    "languages_detected": list(set([m.get("language", "auto") for m in metadatas])),
                    "document_types": list(set([m.get("document_type", "general") for m in metadatas]))
                }
            }
            print(f"✅ Final result prepared before VLM enhancement.")
            
            # Add VLM analysis if enabled
            if self.config.get("app_config").enable_vlm:
                print("ℹ️ Extracting VLM insights from PDF...")
                vlm_texts = await self.vlm_processor.extract_vlm_from_pdf(file_path)
                if vlm_texts:
                    result["vlm_texts"] = vlm_texts
                    
                    # Enhance chunks with VLM insights
                    for i, vlm_text in enumerate(vlm_texts):
                        if i < len(chunks):
                            # Create VLM-enhanced chunk
                            print(f"ℹ️ Enhancing chunk {i+1} with VLM insights.")
                            enhanced_chunk = f"[PAGE {i+1} - ENHANCED WITH VLM]\n{vlm_text}\n\n[ORIGINAL TEXT]\n{chunks[i]}"
                            chunks[i] = enhanced_chunk
                            print(f"✅ Successfully enhanced chunk {i+1} with VLM insights.")
                        else:
                            # Add as new chunk
                            print(f"ℹ️ Adding new VLM chunk for page {i+1}.")
                            chunks.append(f"[PAGE {i+1} - VLM ANALYSIS]\n{vlm_text}")
                            metadatas.append({
                                "source": os.path.basename(file_path),
                                "file_path": file_path,
                                "page": i + 1,
                                "total_pages": len(doc),
                                "processing_method": "vlm_only",
                                "confidence_score": 0.9
                            })
                            print(f"✅ Added new VLM chunk for page {i+1}.")
                else:
                    print("ℹ️ No VLM insights extracted from PDF.")
            
            # Cache results
            print(f"ℹ️ Processed data result after VLM enhancement: {len(chunks)} chunks, {len(metadatas)} metadata entries.")
            print(f"✅ Processed {os.path.basename(file_path)} with state-of-the-art AI: {len(chunks)} chunks created")
            
            return result
        except Exception as e:
            print(f"❌ Error processing document {file_path}: {str(e)}")
            print("ℹ️ returning empty chunks and metadata due to error.")
            return {}        
        finally:
            if 'doc' in locals():
                print(f"ℹ️ Closing document {file_path}.")
                doc.close()
