import os, streamlit as st, requests, re, fitz, html, logging
from typing import List, Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DocumentDisplayer:
    """Display source documents with intelligent highlighting."""
    
    def __init__(self, config):
        self.config = config
    
    def _auth_headers(self) -> dict:
        token = st.session_state.get("token")
        return {"Authorization": f"Bearer {token}"} if token else {}
    
    def _safe_image(self, data, caption=None):
        try:
            st.image(data, caption=caption, width="stretch")
        except TypeError:
            st.image(data, caption=caption, width="stretch")
    
    def _fetch_bytes(self, url: str) -> bytes | None:
        try:
            headers = self._auth_headers()
            print(f"ℹ️ Fetching bytes from {url} Headers: {headers}")

            response = requests.get(url, headers=headers)

            print(f"ℹ️ Fetching preview with status {response}")
            
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            return None
    
    def find_relevant_passages(self, text: str, query: str) -> List[Tuple[str, float, int]]:
        """Find and score relevant passages using advanced matching."""
        if not query:
            return []
            
        try:
            # Split into paragraphs and sentences
            paragraphs = re.split(r'\n\s*\n', text)
            sentences = []
            para_indices = []
            
            for i, para in enumerate(paragraphs):
                para_sentences = re.split(r'(?<=[.!?])\s+', para)
                sentences.extend(para_sentences)
                para_indices.extend([i] * len(para_sentences))
            
            if not sentences:
                return []
            
            # Advanced scoring with multiple criteria
            scored_sentences = []
            query_words = set(re.findall(r'\w+', query.lower()))
            
            for i, sentence in enumerate(sentences):
                sentence_words = set(re.findall(r'\w+', sentence.lower()))
                if not sentence_words:
                    continue
                
                # Calculate multiple similarity scores
                overlap = query_words.intersection(sentence_words)
                if not overlap:
                    continue
                
                # Basic overlap score
                overlap_score = len(overlap) / len(query_words)
                
                # Jaccard similarity
                jaccard_score = len(overlap) / len(query_words.union(sentence_words))
                
                # Position bonus (earlier sentences get slight boost)
                position_bonus = max(0, 1 - (i / len(sentences)) * 0.1)
                
                # Combine scores
                final_score = (overlap_score * 0.6) + (jaccard_score * 0.3) + (position_bonus * 0.1)
                
                scored_sentences.append((sentence, final_score, para_indices[i]))
            
            # Sort by score
            scored_sentences.sort(key=lambda x: x[1], reverse=True)
            
            return [(sent, score, para_idx) for sent, score, para_idx in scored_sentences if score > 0]
            
        except Exception as e:
            st.error(f"❌ Error finding relevant passages: {str(e)}")
            return []
    
    def highlight_text(self, text: str, query: str) -> str:
        """Add intelligent HTML highlighting to relevant passages."""
        if not query or not self.config['enable_highlighting']:
            return f"<pre style='white-space: pre-wrap; overflow-wrap: break-word;'>{html.escape(text)}</pre>"
            
        relevant_passages = self.find_relevant_passages(text, query)
        
        if not relevant_passages:
            return f"<pre style='white-space: pre-wrap; overflow-wrap: break-word;'>{html.escape(text)}</pre>"
        
        # Enhanced highlighting with gradient intensity
        paragraphs = re.split(r'\n\s*\n', text)
        highlighted_paragraphs = []
        
        for para_idx, para_text in enumerate(paragraphs):
            escaped_para = html.escape(para_text)
            
            # Find passages for this paragraph
            para_passages = [(p, s) for p, s, idx in relevant_passages if idx == para_idx]
            
            if not para_passages:
                highlighted_paragraphs.append(escaped_para)
                continue
                
            # Sort by relevance score
            para_passages.sort(key=lambda x: x[1], reverse=True)
            
            # Apply highlighting with intensity based on score
            replacements = []
            
            for passage, score in para_passages[:3]:  # Top 3 matches
                if len(passage) < 10:
                    continue
                    
                passage_escaped = html.escape(passage)
                pos = 0
                while True:
                    pos = escaped_para.find(passage_escaped, pos)
                    if pos == -1:
                        break
                        
                    # Calculate highlight intensity
                    intensity = min(80, int(score * 100))  # Max 80% opacity
                    highlight_color = f'rgba(255, 255, 0, {intensity/100})'
                    
                    # Add confidence indicator
                    confidence_indicator = "🎯" if score > 0.7 else "📍" if score > 0.4 else "📌"
                    
                    highlighted =(
                        f'<span style="background-color: {highlight_color}; padding: 2px; border-radius: 3px;"'
                        f'title="Relevance: {score:.2f}">{confidence_indicator} {passage_escaped}</span>'
                    )

                    replacements.append((pos, passage_escaped, highlighted))
                    pos += len(passage_escaped)
            
            # Apply replacements (reverse order to maintain positions)
            replacements.sort(key=lambda x: x[0], reverse=True)
            
            for pos, original, replacement in replacements:
                escaped_para = escaped_para[:pos] + replacement + escaped_para[pos + len(original):]
            
            highlighted_paragraphs.append(escaped_para)
        
        # Combine with enhanced styling
        highlighted_text = '<pre style="white-space: pre-wrap; overflow-wrap: break-word; line-height: 1.6;">'
        highlighted_text += '\n\n'.join(highlighted_paragraphs)
        highlighted_text += '</pre>'
        
        return highlighted_text
    
    def display_source_document(self, doc_metadata: Dict[str, Any], query: Optional[str] = None) -> None:
        """Display source document with enhanced features."""
        try:
            preview_url = doc_metadata.get("preview_url")
            download_url = doc_metadata.get("download_url")
            file_path = doc_metadata.get("file_path") # Only if local file access is needed or fallback
            content_hash = doc_metadata.get("content_hash")
            doc_type = doc_metadata.get("document_type", "general")
            page_value = doc_metadata.get("page")
            page_num_1idx = int(page_value) if isinstance(page_value, (int, float, str)) and str(page_value).isdigit() else None
            page_num = max(0, page_num_1idx - 1) if page_num_1idx else None  # Convert to 0-indexed
            
            # Enhanced source information display
            confidence_score = float(doc_metadata.get("confidence_score", 0.8))
            processing_method = doc_metadata.get("processing_method", "standard")
            
            confidence_color = "green" if confidence_score > 0.9 else "orange" if confidence_score > 0.7 else "red"
            method_icon = "🚀" if processing_method == "state_of_the_art" else "📄"
            source_name = doc_metadata.get("source", "Unknown")
            total_pages = doc_metadata.get("total_pages", "Unknown")
            
            # Render header differently for markdown (no pages)
            if doc_type == "markdown":
                st.markdown(
                    f"""
                    <div style="background-color: #f0f8ff; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>{method_icon} Source:</strong> {source_name}<br>
                    <strong>🌍 Language:</strong> {doc_metadata.get('language', 'auto')}<br>
                    <strong>📋 Type:</strong> {doc_type}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="background-color: #f0f8ff; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>{method_icon} Source:</strong> {source_name}<br>
                    <strong>📄 Page:</strong> {page_num_1idx if page_num_1idx is not None else '-'} of {total_pages}<br>
                    <strong>🌍 Language:</strong> {doc_metadata.get('language', 'auto')}<br>
                    <strong>📋 Type:</strong> {doc_type}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Markdown rendering path
            if doc_type == "markdown":
                text = None
                # Prefer the retrieved chunk from retrieval step
                if isinstance(doc_metadata.get("retrieved_chunks"), str):
                    text = doc_metadata.get("retrieved_chunks")
                elif file_path and os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
                            text = fh.read()
                    except Exception:
                        text = None

                if text:
                    st.markdown("### 📝 Markdown Content")
                    # Render markdown richly (no HTML escaping)
                    st.markdown(text, unsafe_allow_html=False)
                    # Provide a raw view as fallback
                    with st.expander("View Raw Markdown"):
                        st.code(text, language="markdown")

                # Offer download of original markdown
                if file_path and os.path.exists(file_path):
                    try:
                        with open(file_path, "rb") as fh:
                            md_bytes = fh.read()
                        st.download_button(
                            "⬇️ Download Markdown",
                            type="primary",
                            data=md_bytes,
                            file_name=os.path.basename(file_path),
                            mime="text/markdown",
                            key=f"dl_md_{content_hash}_{os.urandom(4).hex()}",
                            help="Download document."
                        )
                    except Exception:
                        pass

                return

            # Display preview or download options (served by backend) for PDFs and others
            if preview_url:
                img_bytes = self._fetch_bytes(preview_url)
                if img_bytes:
                    caption = f"Preview of {source_name}"
                    if page_num_1idx is not None:
                        caption += f" (Page {page_num_1idx})"
                    self._safe_image(img_bytes, caption=caption)
                else:
                    st.info(f"ℹ️ Preview image not available for {source_name}.")
            elif file_path and os.path.exists(file_path):
                # --- Fallback: local file render (dev/prototype) ---
                doc = fitz.open(file_path)
                
                if page_num is None or page_num >= len(doc):
                    st.warning(f"⚠️ Page {((page_num or 0)+1)} not found in document with {len(doc)} pages")
                    return
                
                # Render the specified page
                page = doc[page_num]
                
                # Render page as high-quality image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                img_bytes = pix.tobytes("png")
                st.image(img_bytes, width="stretch", caption=f"Page {page_num_1idx} of {len(doc)}")
                
                # Extract and display text with highlighting
                text = page.get_text()

                if query and self.config['enable_highlighting'] and text:
                    highlighted_text = self.highlight_text(text, query)
                    with st.expander("📝 Page Text (Relevant sections highlighted)", expanded=True):
                        st.markdown(highlighted_text, unsafe_allow_html=True)
                
                    # Show relevance analysis
                    relevant_passages = self.find_relevant_passages(text, query)
                    if relevant_passages:
                        max_score = max([score for _, score, _ in relevant_passages])
                        st.caption(f"🎯 Relevance Score: {max_score:.2f}")
                        
                        with st.expander("🔍 Top Matching Passages"):
                            for i, (passage, score, _) in enumerate(relevant_passages[:3]):
                                confidence_emoji = "🎯" if score > 0.7 else "📍" if score > 0.4 else "📌"
                                st.markdown(f"**{confidence_emoji} Match {i+1}** (Score: {score:.2f})")
                                st.markdown(f"> {passage}")
                else:
                    with st.expander("📝 Page Text"):
                        st.markdown(f"<pre style='white-space: pre-wrap;'>{text}</pre>", unsafe_allow_html=True)
                
                # Close the document
                doc.close()
                return
            else:
                st.info(f"ℹ️ Preview image not available for {source_name}. Please check the download link.")
            
            if download_url:
                pdf_bytes = self._fetch_bytes(download_url)

                if pdf_bytes:
                    st.download_button(
                        "⬇️ Download Document",
                        type="primary",
                        data=pdf_bytes,
                        file_name=source_name + f"_page_{page_num_1idx}.pdf",
                        mime="application/pdf",
                        key=f"dl_{content_hash}_{os.urandom(4).hex()}_{page_num_1idx}",
                        help="Download document."
                    )
                else:
                    st.warning(f"⚠️ Unable to fetch document for download: {source_name}.")
            else:
                st.warning(f"⚠️ No download link available for {source_name}.")      
        except Exception as e:
            st.error(f"❌ Error displaying source document: {str(e)}")
