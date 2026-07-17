import os, streamlit as st, requests, html, logging, time, numpy as np
from typing import Optional, List, Any, Dict
from utils import format_time
from i18n import translate
from http_headers import auth_headers

logger = logging.getLogger(__name__)
BACKEND_API_URL = os.getenv("BACKEND_API_URL") 

class ChatInterface:
    """Enhanced chat interface with state-of-the-art features."""
    
    def __init__(self, config, document_displayer):
        self.config = config
        self.document_displayer = document_displayer
        self.current_query = None
    
    def _display_document_group(self, docs):
        """Display a group of documents from the same source."""
        labels = []
        for i, doc in enumerate(docs):
            conf = doc.get("confidence_score", 0.8)
            page = doc.get("page")
            doc_type = doc.get("document_type", "general")
            if page is not None:
                label = f"Page {page}"
            elif doc_type == "markdown":
                label = f"Chunk {i+1}"
            else:
                label = f"Item {i+1}"
            labels.append(label)
        
        if len(docs) > 1:
            page_tabs = st.tabs(labels)
            for page_idx, (page_tab, doc) in enumerate(zip(page_tabs, docs)):
                with page_tab:
                    self.document_displayer.display_source_document(doc, query=self.current_query)
        else:
            self.document_displayer.display_source_document(docs[0], query=self.current_query)
    
    def display_message(
        self, 
        role: str, 
        content: str, 
        inference_time: Optional[float] = None, 
        sources: Optional[List[Dict[str, Any]]] = None, 
        msg_index: Optional[int] = None
    ) -> None:
        """Display enhanced chat message with state-of-the-art indicators."""
        print(f"ℹ️ FE - CI: Displaying message - Role: {role}, Content: {content[:30]}..., Inference Time: {inference_time}, Sources: {len(sources) if sources else 0}, Msg Index: {msg_index}")
        if role == "user":
            avatar_content = "👤"
            message_class = "user"
            self.current_query = content
        else:
            avatar_content = "🤖"
            message_class = "bot"

        # Enhanced message with AI indicators
        ai_indicator = ""
        if role == "assistant" and sources:
            avg_confidence = np.mean([s.get("confidence_score", 0.8) for s in sources])
            processing_methods = set([s.get("processing_method", "standard") for s in sources])
            
            if "state_of_the_art" in processing_methods:
                ai_indicator = "🚀 State-of-the-Art AI"
            elif avg_confidence > 0.9:
                ai_indicator = "🎯 High Confidence"
            elif avg_confidence > 0.7:
                ai_indicator = "📍 Good Confidence"

        message_html = f"""
        <div class="chat-message {message_class}">
            <div class="avatar {message_class}">
                {avatar_content}
            </div>
            <div class="content">
                {content}
        """
        
        if inference_time is not None:
            formatted_time = format_time(inference_time)
            speed_indicator = "⚡" if inference_time < 2 else "🐌" if inference_time > 10 else "⏱️"
            message_html += f'<div class="inference-time">{speed_indicator} Response Time: {formatted_time}</div>'

        message_html += "</div></div>"

        st.markdown(message_html, unsafe_allow_html=True)

        # Enhanced source display
        if sources and msg_index is not None:
            sources_count = len(sources)
            avg_confidence = np.mean([s.get("confidence_score", 0.8) for s in sources])
            
            confidence_emoji = "🎯" if avg_confidence > 0.9 else "📍" if avg_confidence > 0.7 else "📌"
            button_text = "Hide Sources" if st.session_state.show_sources.get(msg_index, False) else f"Show {sources_count} Source{'s' if sources_count > 1 else ''}"

            if st.button(f"{confidence_emoji} {button_text}", key=f"toggle_source_{msg_index}", type="primary", help="Chcekout the sources."):
                st.session_state.show_sources[msg_index] = not st.session_state.show_sources.get(msg_index, False)

            if st.session_state.show_sources.get(msg_index, False):
                # Group sources by document and processing method
                doc_groups = {}
                for doc in sources:
                    source_name = doc.get('source', 'Unknown')
                    processing_method = doc.get('processing_method', 'standard')
                    key = f"{source_name}"
                    
                    if key not in doc_groups:
                        doc_groups[key] = []
                    doc_groups[key].append(doc)
                
                print(f"ℹ️ Displaying {len(doc_groups)} source groups for message index {msg_index} \n")

                print(f"ℹ️ Source groups: {doc_groups} \n")

                st.markdown('<div class="source-container">', unsafe_allow_html=True)

                if len(doc_groups) > 1:
                    tabs = st.tabs(list(doc_groups.keys()))
                    for tab_idx, (doc_name, docs) in enumerate(doc_groups.items()):
                        with tabs[tab_idx]:
                            self._display_document_group(docs)
                else:
                    doc_name = list(doc_groups.keys())[0]
                    docs = doc_groups[doc_name]
                    self._display_document_group(docs)

                st.markdown('</div>', unsafe_allow_html=True)
    
    def add_message(
        self, 
        role: str, 
        content: str, 
        inference_time: Optional[float] = None, 
        sources: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Add message to chat history with enhanced metadata."""
        message = {
            "role": role,
            "content": content,
            "inference_time": inference_time,
            "sources": sources,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.messages.append(message)
    
    def handle_user_input(self) -> None:
        """Handle user input with state-of-the-art processing."""
        
        user_input = st.session_state.get("temp_input", "").strip()
        
        if not user_input:
            return
        
        print(f"ℹ️ FE - CI: User input received: {user_input}")
                
        # Add user message
        self.add_message("user", user_input)
        
        # Clear input
        st.session_state.temp_input = ""
        
        api_url = f"{BACKEND_API_URL}/api/chatbot/query"
        token = st.session_state.get('token')
        
        payload = {
            "query": user_input,
            "llm_model": st.session_state.get("llm_model"),
            "embedding_model": st.session_state.get("embedding_model")
        }
        print(f"ℹ️ FE: Sending query to API: {api_url} and {payload}")

        try:
            # Generate response with enhanced processing
            with st.spinner(translate("chat.input.send.loader")):
                start_time = time.time()

                query_response = requests.post(api_url, json=payload, headers=auth_headers(token))
                
                if query_response.status_code != 200:
                    err_json = query_response.json()
                    err_text = err_json.get("detail")
                    self.add_message("assistant", f"❌ Error while Q&A: {err_text}")
                    return
                
                data = query_response.json().get("data", {})
                
                print(f"ℹ️ FE: Received response data: {data}")
                
                llm_answer = data["answer"]
                source_docs = data["source_docs"]
                # inference_time = data.get("inference_time")                
                
                end_time = time.time()
                inference_time = end_time - start_time
                
                # Add enhanced response
                self.add_message("assistant", llm_answer, inference_time, source_docs)
                
                # Update usage statistics
                if "usage_stats" not in st.session_state:
                    st.session_state.usage_stats = {
                        "total_queries": 0,
                        "total_time": 0.0,
                        "avg_confidence": 0
                    }
                
                st.session_state.usage_stats["total_queries"] += 1
                st.session_state.usage_stats["total_time"] += inference_time
                
                if source_docs:
                    avg_confidence = np.mean([s.get("confidence_score", 0.8) for s in source_docs])
                    st.session_state.usage_stats["avg_confidence"] = avg_confidence
        except Exception as e:
                error_msg = f"❌ An error occurred: {str(e)}"
                self.add_message("assistant", error_msg)
