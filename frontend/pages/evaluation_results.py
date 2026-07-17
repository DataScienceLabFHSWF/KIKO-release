# Import necessary libraries
import os, streamlit as st, logging
from dotenv import load_dotenv
from pages import render_sidebar
from utils import require_login
import pandas as pd
from pathlib import Path
from PIL import Image
from i18n import translate
from topbar import language_topbar

logger = logging.getLogger(__name__)

# set page configuration
st.set_page_config(page_title="Evaluation Results", page_icon="🔍", layout="wide")

# Check if the user is logged in
require_login()

# Always show top-right language switch
language_topbar()

# Load API URL from environment variables
load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL")

# check if BACKEND_API_URL is set
if not BACKEND_API_URL:
    st.error(translate("eval.errors.envMissing"))
    st.stop()

# declare headers for API requests
headers = {"Authorization": f"Bearer {st.session_state.token}"}

# Render the sidebar
render_sidebar()

st.title(translate("eval.pageTitle"))
st.markdown(translate("eval.subtitle"))
st.divider()

# ---- paths (adjust if needed) ----
CORPUS_CSV = "./assets/evaluation_results/eductum_eval.csv"

# chat quality (Apertus + Llama3)
CHAT_APERTUS_CSV = "./assets/evaluation_results/chat_eval_results_Apertus.csv"
CHAT_APERTUS_IMG = "./assets/evaluation_results/distribution_chats_Apertus.png"

CHAT_LLAMA3_CSV  = "./assets/evaluation_results/chat_eval_results_llama3.csv"
CHAT_LLAMA3_IMG  = "./assets/evaluation_results/distribution_chats_llama3.png"

CHAT_KIMIK2_CSV  = "./assets/evaluation_results/chat_eval_results_kimik2.csv"
CHAT_KIMIK2_IMG  = "./assets/evaluation_results/distribution_chats_kimik2.png"

# grading (DeepSeek-R1)
GRADING_DEEPSEEK_CSV = "./assets/evaluation_results/grading_eval_results_deepseek.csv"
GRADING_DEEPSEEK_IMG = "./assets/evaluation_results/confusion_matrix_grades_deepseek.png"

# summary comparison (Apertus + DeepSeek or overall)
APERTUS_SUMMARY_CSV = "./assets/evaluation_results/summary_eval_results_Apertus_deepseek.csv"
LLAMA3_SUMMARY_CSV = "./assets/evaluation_results/summary_eval_results_llama3_deepseek.csv"
KIMIK2_SUMMARY_CSV = "./assets/evaluation_results/summary_eval_results_kimik2_deepseek.csv"

# ---- helper functions ----
def _load_csv_safe(path: str | Path) -> pd.DataFrame | None:
    try:
        p = Path(path).expanduser()
        if not p.exists():
            return None
        return pd.read_csv(p)
    except Exception as e:
        st.warning(translate("eval.warnings.csvReadFail", path=path, error=e))
        return None

def _image_safe(path: str | Path):
    try:
        p = Path(path).expanduser()
        if not p.exists():
            return None
        return Image.open(p)
    except Exception as e:
        st.warning(translate("eval.warnings.imgOpenFail", path=path, error=e))
        return None

def _df_basic_stats(df: pd.DataFrame) -> dict:
    # very general stats that don't assume a schema
    return {
        "Rows": len(df),
        "Columns": len(df.columns),
        "Missing values": int(df.isna().sum().sum()),
        "Approx. avg chars per row": int(df.astype(str).apply(lambda r: "|".join(r), axis=1).str.len().mean()),
    }
# ---- end helper functions ----

# ---- UI ----
tab_dataset, tab_chat_apertus, tab_chat_llama3, tab_chat_kimik2, tab_grading = st.tabs(
    [
        translate("eval.tabs.dataset"), 
        translate("eval.tabs.chatApertus"), 
        translate("eval.tabs.chatLlama3"),
        translate("eval.tabs.chatKimik2"), 
        translate("eval.tabs.grading"),        
    ]
)

# ============ DATASET TAB ============
with tab_dataset:
    st.subheader(translate("eval.dataset.subheader"))
    st.caption(translate("eval.dataset.caption"))

    df_corpus = _load_csv_safe(CORPUS_CSV)

    if df_corpus is None:
        st.info(translate("eval.dataset.missingDataset", path=CORPUS_CSV))
    else:
        with st.expander(translate("eval.dataset.explainerTitle")):
            st.markdown(translate("eval.dataset.explainer"))
        
        st.divider()
        # quick stats
        st.write(translate("eval.dataset.statsTitle"))
        stats = _df_basic_stats(df_corpus)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(translate("eval.dataset.stats.rows"), stats["Rows"])
        c2.metric(translate("eval.dataset.stats.columns"), stats["Columns"])
        c3.metric(translate("eval.dataset.stats.missing"), stats["Missing values"])
        c4.metric(translate("eval.dataset.stats.avgChars"), stats["Approx. avg chars per row"])
        
        st.divider()
        # preview + download
        st.write(translate("eval.dataset.previewTitle"))
        st.dataframe(df_corpus.head(25))

# ============ CHAT: APERTUS TAB ============
with tab_chat_apertus:
    st.subheader(translate("eval.chatApertus.subheader"))
    df = _load_csv_safe(CHAT_APERTUS_CSV)
    img = _image_safe(CHAT_APERTUS_IMG)
    df_summary = _load_csv_safe(APERTUS_SUMMARY_CSV)

    if df is not None and df_summary is not None:
        with st.expander(translate("eval.chatApertus.explainerTitle")):
            st.markdown(translate("eval.chatApertus.explainer"))
        
        st.divider()
        st.write(translate("eval.chatApertus.resultsTable"))
        st.dataframe(df)
        
        st.divider()
        st.write(translate("eval.chatApertus.quickAggregates"))
        st.dataframe(df_summary[["chat_ROUGE-L_avg", "chat_BLEU_avg", "chat_BERTScore_F1_avg", "chat_CitationRate", "chat_Recall_k_avg", "chat_MRR_avg", "chat_nDCG_avg", "chat_AttributionMatch_avg"]])
    
    st.divider()
    if img is not None:
        st.write(translate("eval.chatApertus.visualization"))
        st.image(img, caption=translate("eval.chatApertus.vizCaption"), width="stretch")

    if df is None and img is None or df_summary is None:
        st.info(translate("eval.chatApertus.artifactsMissing"))

# ============ CHAT: LLAMA3 TAB ============
with tab_chat_llama3:
    st.subheader(translate("eval.chatLlama3.subheader"))
    df = _load_csv_safe(CHAT_LLAMA3_CSV)
    img = _image_safe(CHAT_LLAMA3_IMG)
    df_summary = _load_csv_safe(LLAMA3_SUMMARY_CSV)

    if df is not None and df_summary is not None:
        with st.expander(translate("eval.chatLlama3.explainerTitle")):
            st.markdown(translate("eval.chatLlama3.explainer"))
        
        st.divider()
        st.write(translate("eval.chatLlama3.resultsTable"))
        st.dataframe(df)
        
        st.divider()
        st.write(translate("eval.chatLlama3.quickAggregates"))
        st.dataframe(df_summary[["chat_ROUGE-L_avg", "chat_BLEU_avg", "chat_BERTScore_F1_avg", "chat_CitationRate", "chat_Recall_k_avg", "chat_MRR_avg", "chat_nDCG_avg", "chat_AttributionMatch_avg"]])

    st.divider()
    if img is not None:
        st.write(translate("eval.chatLlama3.visualization"))
        st.image(img, caption=translate("eval.chatLlama3.vizCaption"), width="stretch")

    if df is None and img is None or df_summary is None:
        st.info(translate("eval.chatLlama3.artifactsMissing"))

# ============ CHAT: Kimi K2-Instruct-0905 TAB ============
with tab_chat_kimik2:
    st.subheader(translate("eval.chatKimik2.subheader"))
    df = _load_csv_safe(CHAT_KIMIK2_CSV)
    img = _image_safe(CHAT_KIMIK2_IMG)
    df_summary = _load_csv_safe(KIMIK2_SUMMARY_CSV)

    if df is not None and df_summary is not None:
        with st.expander(translate("eval.chatKimik2.explainerTitle")):
            st.markdown(translate("eval.chatKimik2.explainer"))
        
        st.divider()
        st.write(translate("eval.chatKimik2.resultsTable"))
        st.dataframe(df)
        
        st.divider()
        st.write(translate("eval.chatKimik2.quickAggregates"))
        st.dataframe(df_summary[["chat_ROUGE-L_avg", "chat_BLEU_avg", "chat_BERTScore_F1_avg", "chat_CitationRate", "chat_Recall_k_avg", "chat_MRR_avg", "chat_nDCG_avg", "chat_AttributionMatch_avg"]])

    st.divider()
    if img is not None:
        st.write(translate("eval.chatKimik2.visualization"))
        st.image(img, caption=translate("eval.chatKimik2.vizCaption"), width="stretch")

    if df is None and img is None or df_summary is None:
        st.info(translate("eval.chatKimik2.artifactsMissing"))

# ============ GRADING: DEEPSEEK TAB ============
with tab_grading:
    st.subheader(translate("eval.grading.subheader"))
    df = _load_csv_safe(GRADING_DEEPSEEK_CSV)
    img = _image_safe(GRADING_DEEPSEEK_IMG)
    df_summary = _load_csv_safe(LLAMA3_SUMMARY_CSV)

    if df is not None and df_summary is not None:
        with st.expander(translate("eval.grading.explainerTitle")):
            st.markdown(translate("eval.grading.explainer"))
        
        st.divider()
        st.write(translate("eval.grading.resultsTable"))
        st.dataframe(df)
        
        st.divider()
        st.write(translate("eval.grading.quickAggregates"))
        st.dataframe(df_summary[["grade_n_items", "grade_Accuracy_exact", "grade_MAE", "grade_Within1", "grade_QWKappa"]])            

    st.divider()
    if img is not None:
        st.write(translate("eval.grading.visualization"))
        st.image(img, caption=translate("eval.grading.vizCaption"), width="stretch")

    if df is None and img is None or df_summary is None:
        st.info(translate("eval.grading.artifactsMissing"))
