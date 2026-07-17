# Import necessary libraries
import os, streamlit as st, requests, logging
from dotenv import load_dotenv
from pages import render_sidebar
from utils import (
    require_login, initialize_session_state, show_file_status_list,
    get_backend_app_config_library
)
from components import ChatInterface, DocumentDisplayer
from i18n import translate
from topbar import language_topbar
from http_headers import auth_headers

logger = logging.getLogger(__name__)

# set page configuration
st.set_page_config(page_title="Chat Assistant", page_icon="🤖", layout="wide")

# Check if the user is logged in
require_login()

# Load API URL from environment variables
load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL")

# check if BACKEND_API_URL is set
if not BACKEND_API_URL:
    st.error(translate("error.env"))
    st.stop()

# Always show top-right language switch
language_topbar()

# declare headers for API requests
headers = {"Authorization": f"Bearer {st.session_state.token}"}

token = st.session_state.token

if "confirm_clear_chat" not in st.session_state:
    st.session_state.confirm_clear_chat = False

def load_history_into_session(API_BASE, headers):
    if st.session_state.get("loaded_history"):
        return
    try:
        response = requests.get(f"{API_BASE}/api/chatbot/chat/history", headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to load chat history: {response.status_code} - {response.text}")
        else:
            data = response.json()
            
            msgs = data.get("messages", [])
            print(f"ℹ️ Loaded {len(msgs)} messages from chat history.")
            
            # Initialize messages if missing
            if "messages" not in st.session_state:
                st.session_state["messages"] = []
            st.session_state["messages"].extend(msgs)
            st.session_state["loaded_history"] = True
    except Exception as e:
        st.warning(translate("chat.history.loadWarn", error=str(e)))

@st.dialog(translate("chat.config.clear.dialog.title"))
def confirm_clear_chat_dialog():
    st.write(translate("chat.config.clear.dialog.body"))
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button(translate("chat.config.clear.dialog.yes"), key="clear_chat_yes", type="primary", help=translate("chat.config.clear.dialog.yes_help")):
            try:
                response = requests.delete(f"{BACKEND_API_URL}/api/chatbot/history", headers=headers)

                if response.status_code in (200, 204):
                    # wipe local session history too
                    st.session_state["messages"] = []
                    st.session_state["loaded_history"] = False
                    st.toast(translate("chat.config.clear.dialog.toast"), icon="🧹")
                else:
                    st.error(translate("chat.config.clear.dialog.error", status=response.status_code, text=getattr(response, 'text', '')))
            except Exception as e:
                st.error(translate("chat.config.clear.dialog.exception", error=str(e)))
            finally:
                st.session_state.confirm_clear_chat = False
                st.rerun()
    with c2:
        if st.button(translate("chat.config.clear.dialog.no"), type="primary", key="clear_chat_no", help=translate("chat.config.clear.dialog.no_help")):
            st.session_state.confirm_clear_chat = False
            st.rerun()

# Render the sidebar
render_sidebar()

# ---------------------------------------
# Page layout - Chat (left) | Config (right)
# ---------------------------------------
col_chat, col_config = st.columns([2, 1], gap="large")

app_config_library_data = get_backend_app_config_library(BACKEND_API_URL, headers)

if not app_config_library_data:
    st.error(translate("chat.errors.configEmpty"))
    st.stop()
else:
    if app_config_library_data:
        
        initialize_session_state()
        app_config_data = app_config_library_data.get("app_config")

        document_displayer = DocumentDisplayer(app_config_data)
        chat_interface = ChatInterface(app_config_data, document_displayer)
        
        # Set default models if not already set
        # Todo: Later we will have multiple models and embeddings.
        default_embedding_model_name = app_config_data['default_embedding_model']
        
        ################################
        # Chat Assistant
        ################################
        
        with col_chat:

            st.title(translate("chat.pageTitle"))
            st.markdown(translate("chat.subtitle"))
            st.divider()

            # Create enhanced chat container
            chat_container = st.container()
            
            load_history_into_session(BACKEND_API_URL, headers)
            
            # Display messages with enhanced features
            with chat_container:
                if "messages" in st.session_state and len(st.session_state.get("messages", [])) > 0:
                    for i, message in enumerate(st.session_state.messages):
                        chat_interface.display_message(
                            role=message["role"],
                            content=message["content"],
                            inference_time=message.get("inference_time"),
                            sources=message.get("sources"),
                            msg_index=i if message["role"] == "assistant" else None
                        )
                    
                    print(f"ℹ️ FE: Displaying messages from session state.{chat_interface}")
            
            # Spacer for fixed chat bar
            st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)           

            # Enhanced input widgets
            st.text_area(
                translate("chat.input.label"),
                key="temp_input",
                label_visibility="collapsed",
                placeholder=translate("chat.input.placeholder")
            )

            st.button(
                translate("chat.input.send.label"), 
                on_click=chat_interface.handle_user_input, 
                type="primary", 
                help=translate("chat.input.send.help")
            )
        # Chat Assistant code end here---
        
        ##########################################
        # Configurations options
        ##########################################
        with col_config:
            # Document Upload with enhanced features
            st.subheader(translate("chat.config.upload.title"))
            
            uploaded_files = st.file_uploader(
                translate("chat.config.upload.uploaderLabel"),
                type=["pdf"],
                accept_multiple_files=True,
                help=translate("chat.config.upload.uploaderHelp")
            )

            if uploaded_files and st.button(translate("chat.config.upload.process.label"), type="primary", help=translate("chat.config.upload.process.help")):
                with st.spinner(translate("chat.config.upload.process.spinner")):
                    try:
                        # Get unique filename based on content hash
                        print(f"ℹ️ FE: Getting unique filename based on content hash.")
                        
                        # Build multipart: list of ("files", (filename, bytes, mimetype))
                        files_payload = []
                        for uf in uploaded_files:
                            content = uf.read()
                            if not content:
                                st.warning(translate("chat.config.upload.process.fileEmptyWarn", file=uf.name))
                                continue
                            files_payload.append(("files", (uf.name, content, "application/pdf")))
                        
                        if not files_payload:
                            st.warning(translate("chat.config.upload.process.noFilesWarn"))
                        else:
                            payload = {
                                "embedding_model_name": default_embedding_model_name,
                            }
                            
                            # API call to documnets
                            upload_response = requests.post(
                                f"{BACKEND_API_URL}/api/document/process_uploaded_docs", 
                                files=files_payload, 
                                data=payload, 
                                headers=auth_headers(token)
                            )
                            
                            if upload_response.status_code != 200:
                                st.error(translate("chat.config.upload.process.error",status=upload_response.status_code, detail=upload_response.detail))
                            else:
                                data = upload_response.json()
                                print(f"✅ FE: Uploaded API successfull: {upload_response} and {data}")
                                show_file_status_list(data)                                
                    except Exception as e:
                        st.error(translate("chat.config.upload.process.networkError", error=str(e)))
                        logger.error(f"Error processing document: {str(e)}")                        
            
            st.session_state.embedding_model = default_embedding_model_name
            
            # LLM model selection
            previous_llm = st.session_state.get('llm_model', app_config_data['default_llm_model'])
            
            llm_models = [
                "llama3.3:70b",
                "Apertus-8B-Instruct-2509",
                "nemotron:70b",
            ]
            
            llm_model = st.selectbox(
                translate("chat.config.models.llmLabel"),
                llm_models,
                index=0,
                help=translate("chat.config.models.llmHelp")
            )
            
            # Check for model change
            if previous_llm != llm_model:
                st.warning(translate("chat.config.models.switchedWarn", model=llm_model))
            
            st.session_state.llm_model = llm_model
            
            # System Information (use safe .get access to avoid KeyError)
            flags = app_config_library_data.get("flags", {})
            modules = app_config_library_data.get("modules", {})
            env = app_config_library_data.get("environment", {})

            with st.expander(translate("chat.config.system.expander")):
                st.write(translate("chat.config.system.modelsTitle"))
                if flags.get("is_advanced_models_available"):
                    st.info(translate("chat.config.system.vlmAdvanced"))
                else:
                    st.warning(translate("chat.config.system.vlmBasic"))

                if flags.get("is_surya_available"):
                    st.info(translate("chat.config.system.ocrSurya"))
                else:
                    st.info(translate("chat.config.system.ocrTrocr"))

                if flags.get("is_cv2_available"):
                    st.info(translate("chat.config.system.cvOn"))
                else:
                    st.warning(translate("chat.config.system.cvOff"))

                st.write(translate("chat.config.system.embAndLlmTitle"))
                st.info(translate("chat.config.system.embedding", model=default_embedding_model_name))
                st.info(translate("chat.config.system.llm", model=st.session_state.get('llm_model')))

                st.write(translate("chat.config.system.systemTitle"))
                st.info(translate("chat.config.system.python", version=env.get('python_version', 'unknown')))
                torch = modules.get('torch', {})
                st.info(translate("chat.config.system.pytorch", version=torch.get('torch_version', 'unknown')))
                if torch.get("is_available"):
                    cuda = torch.get('cuda', {})
                    st.info(translate("chat.config.system.cuda",
                                      version=cuda.get('version', 'unknown'),
                                      device=cuda.get('device', 'unknown'),
                                      memory=cuda.get('memory_gb', 'unknown')))
                else:
                    st.info(translate("chat.config.system.cpu"))
            
            if st.button(
                translate("chat.config.clear.button.label"), 
                key="btn_clear_chat", 
                type="primary", 
                width="stretch", 
                help=translate("chat.config.clear.button.help")
            ):
                st.session_state.confirm_clear_chat = True
            
            # open the dialog if requested
            if st.session_state.confirm_clear_chat:
                confirm_clear_chat_dialog()
            
            # Usage Statistics
            if "usage_stats" in st.session_state and st.session_state.usage_stats["total_queries"] > 0:
                with st.expander(translate("chat.config.usage.expander")):
                    stats = st.session_state.usage_stats
                    st.metric(translate("chat.config.usage.total"), stats["total_queries"])
                    st.metric(translate("chat.config.usage.avgTime"), f"{stats['total_time']/stats['total_queries']:.1f}s")
                    if stats["avg_confidence"] > 0:
                        st.metric(translate("chat.config.usage.avgConfidence"), f"{stats['avg_confidence']:.1%}")
    else:
        st.error(translate("chat.errors.configMissing"))
        st.stop()
