import os, fitz,logging
from .multilingual_processor import MultilingualProcessor

logging.getLogger(__name__)

class PDFMetadataExtractor:
    """Extract and utilize metadata from PDF documents."""
    
    def __init__(self, config):
        print("ℹ️ Initializing PDFMetadataExtractor with configuration.")
        self.config = config
    
    async def extract_metadata(self, pdf_path):
        """Extract comprehensive metadata from PDF."""
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"❌ Failed to open PDF: {pdf_path} — {e}")
            return {}
        
        print(f"ℹ️ extract_metadata: PDF opened successfully: {doc}")
        
        # Basic metadata
        metadata = {}
        try:
            metadata = {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "keywords": doc.metadata.get("keywords", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "modification_date": doc.metadata.get("modDate", ""),
                "page_count": len(doc),
                "file_size": os.path.getsize(pdf_path),
                "version": doc.metadata.get("format", ""),
                "is_encrypted": doc.is_encrypted,                
            }
            
            # Try to get AcroForm field
            try:
                metadata["is_form"] = bool(doc.xref_get_key(0, "AcroForm"))
            except Exception:
                metadata["is_form"] = False
            
            print(f"ℹ️ extract_metadata: Basic metadata extracted: {metadata}")

            # Extract document structure
            try:
                toc = doc.get_toc()
                if toc:
                    metadata["table_of_contents"] = toc
                    print(f"ℹ️ extract_metadata: Table of contents extracted: {toc} and {metadata}")
            except Exception as e:
                print(f"⚠️ TOC extraction failed: {e}")
                metadata["table_of_contents"] = None
            
            # Document properties - Annotations and links
            metadata["has_annotations"] = any(page.annot_xrefs for page in doc)
            metadata["has_links"] = any(len(page.get_links()) > 0 for page in doc)
            
            # Form fields analysis
            if self.config.get("app_config").extract_forms:
                try:
                    form_fields = self._extract_form_fields(doc)
                    if form_fields:
                        metadata["form_fields"] = form_fields
                except Exception as e:
                    print(f"⚠️ Error extracting form fields: {e}")
                    metadata["form_fields"] = None
            
            # Language detection from content
            if self.config.get("app_config").language_detection:
                try:
                    sample_text = ""
                    for page_num in range(min(3, len(doc))):
                        sample_text += doc[page_num].get_text()[:500]  # Get first 500 characters from first 3 pages
                    
                    if sample_text:
                        multilingual_processor = MultilingualProcessor(self.config)
                        detected_language = await multilingual_processor.detect_language(sample_text)
                        metadata["detected_language"] = detected_language
                except Exception as e:
                    print(f"⚠️ Error detecting language: {e}")
                    metadata["detected_language"] = None
            
            print(f"✅ Metadata extracted successfully from {pdf_path}")
            return metadata               
        except Exception as e:
            print(f"❌ Error extracting metadata from {pdf_path}: {str(e)}")
            return {}
        finally:
            if 'doc' in locals():
                print(f"ℹ️ Closing document {pdf_path}.")
                doc.close()

    def _extract_form_fields(self, doc):
        """Extract form fields from PDF."""
        form_fields = []
        
        try:
            for page in doc:
                widgets = page.widgets()
                if widgets:
                    for widget in widgets:
                        field_info = {
                            "type": widget.field_type,
                            "name": widget.field_name,
                            "value": widget.field_value,
                            "page": page.number,
                            "rect": [widget.rect.x0, widget.rect.y0, widget.rect.x1, widget.rect.y1]
                        }
                        form_fields.append(field_info)
            
            print(f"✅ Extracted {len(form_fields)} form fields from PDF.")
            return form_fields
        except Exception as e:
            print(f"❌ Error extracting form fields: {str(e)}")
            return []
    
    async def enhance_document_processing(self, metadata, text_blocks):
        """Use metadata to enhance document processing."""
        if not metadata:
            print("⚠️ No metadata available to enhance document processing.")
            print("ℹ️ Returning original text blocks without enhancements.")
            return text_blocks
            
        try:
            enhanced_blocks = text_blocks.copy()
            
            # Add table of contents
            if "table_of_contents" in metadata:
                toc_text = "Document Structure:\n"
                for level, title, page in metadata["table_of_contents"]:
                    indent = "  " * (level - 1)
                    toc_text += f"{indent}- {title} (Page {page})\n"
                
                enhanced_blocks.insert(0, {
                    "text": toc_text,
                    "metadata": {
                        "source": "Document Structure",
                        "type": "table_of_contents"
                    }
                })
            
            # Add document metadata
            meta_text = "Document Metadata:\n"
            for key, value in metadata.items():
                if key not in ["table_of_contents", "form_fields"] and value:
                    meta_text += f"- {key}: {value}\n"
            
            enhanced_blocks.insert(0, {
                "text": meta_text,
                "metadata": {
                    "source": "Document Metadata",
                    "type": "metadata"
                }
            })
            
            # Add form fields information
            if "form_fields" in metadata and metadata["form_fields"]:
                form_text = "Document Form Fields:\n"
                for field in metadata["form_fields"]:
                    form_text += f"- {field['name']} ({field['type']}): {field['value']} (Page {field['page']+1})\n"
                
                enhanced_blocks.append({
                    "text": form_text,
                    "metadata": {
                        "source": "Form Fields",
                        "type": "form_fields"
                    }
                })
            
            print("✅ Document processing enhanced with metadata.")
            return enhanced_blocks
        except Exception as e:
            print(f"❌ Error enhancing document processing with metadata: {str(e)}")
            return text_blocks
