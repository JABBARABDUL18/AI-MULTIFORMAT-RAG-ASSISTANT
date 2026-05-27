import streamlit as st
import os
import shutil
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = ""
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

try:
    from file_processor import FileProcessor
    from rag_engine import RAGEngine
    RAG_AVAILABLE = True
except ImportError as e:
    RAG_AVAILABLE = False
    logger.error(f"RAG modules not found: {e}")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(
    page_title="RAG · Team 8",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@300;400;500;600&family=Caveat:wght@400;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --c-void:      #020509;
  --c-deep:      #060d14;
  --c-surface:   #0b1623;
  --c-raise:     #0f1f30;
  --c-line:      #1a3350;
  --c-line2:     #204060;
  --c-cyan:      #06eeff;
  --c-purple:    #a78bfa;
  --c-green:     #10ffaa;
  --c-red:       #ff4d6d;
  --c-text:      #e2edf8;
  --c-text2:     #6b8fa8;
  --c-text3:     #2a4a63;
  --font-ui:     'Space Grotesk', sans-serif;
  --font-code:   'IBM Plex Mono', monospace;
  --font-script: 'Caveat', cursive;
  --r-sm: 6px; --r-md: 10px; --r-lg: 16px;
}

html, body {
  min-height: 100vh !important;
  background: var(--c-void) !important;
  font-family: var(--font-ui) !important;
  overflow-x: hidden;
}

#root, .stApp, .stApp > div, .stApp > div > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section,
[data-testid="stMain"], [data-testid="stMain"] > div,
[data-testid="stMainBlockContainer"], .main {
  background: var(--c-void) !important;
  min-height: 100vh !important;
  width: 100% !important;
}

[data-testid="stDecoration"], [data-testid="stToolbar"],
#MainMenu, footer { display: none !important; }

[data-testid="stHeader"] {
  background: var(--c-void) !important;
  height: 0px !important; min-height: 0px !important;
}

.main .block-container,
[data-testid="stMainBlockContainer"] {
  background: var(--c-void) !important;
  padding: 0 !important;
  max-width: 100% !important;
  width: 100% !important;
  min-height: 100vh !important;
}

/* ══ SIDEBAR — 300px wide ══ */
[data-testid="stSidebar"] {
  background: var(--c-deep) !important;
  border-right: 1px solid var(--c-line) !important;
  min-height: 100vh !important;
  width: 300px !important;
  min-width: 300px !important;
  max-width: 300px !important;
}
[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebarContent"] {
  width: 300px !important;
  min-width: 300px !important;
  padding: 0 !important;
  background: var(--c-deep) !important;
}

/* When collapsed — shrink to zero so main fills screen (no black gap) */
[data-testid="stSidebar"][aria-expanded="false"] {
  width: 0px !important;
  min-width: 0px !important;
  border: none !important;
  overflow: hidden !important;
}
[data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
  width: 0px !important; min-width: 0px !important;
}

[data-testid="stMain"] {
  flex: 1 1 auto !important;
  min-width: 0 !important;
  background: var(--c-void) !important;
}

/* ── GLOBAL TEXT ── */
.stApp p, .stApp span, .stApp label, .stMarkdown p,
[data-testid="stChatMessageContent"] p {
  color: var(--c-text) !important;
  font-family: var(--font-ui) !important;
  font-size: 0.95rem !important;
}

/* ── BUTTONS ── */
.stButton > button {
  font-family: var(--font-code) !important;
  font-size: 0.8rem !important; font-weight: 500 !important;
  letter-spacing: 0.1em !important; text-transform: uppercase !important;
  border-radius: var(--r-sm) !important; height: 2.6rem !important;
  transition: all 0.18s !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #0091b0 0%, #5b21b6 100%) !important;
  border: none !important; color: #fff !important;
}
.stButton > button[kind="primary"]:hover { transform: translateY(-1px) !important; }
.stButton > button[kind="secondary"] {
  background: transparent !important;
  border: 1px solid var(--c-line2) !important; color: var(--c-text2) !important;
}
.stButton > button[kind="secondary"]:hover {
  border-color: var(--c-red) !important; color: var(--c-red) !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
  background: var(--c-surface) !important;
  border: 1px dashed var(--c-line2) !important; border-radius: var(--r-md) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] p,
[data-testid="stFileUploaderDropzoneInstructions"] span {
  color: var(--c-text2) !important; font-size: 0.82rem !important;
  font-family: var(--font-code) !important;
}
[data-testid="stFileUploaderFile"] {
  background: var(--c-raise) !important; border: 1px solid var(--c-line) !important;
  border-radius: var(--r-sm) !important;
}
[data-testid="stFileUploaderFileName"] {
  color: var(--c-text) !important; font-family: var(--font-code) !important; font-size: 0.8rem !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
  background: var(--c-raise) !important; border: 1px solid var(--c-line) !important;
  border-radius: var(--r-md) !important; padding: 8px 12px !important;
}
[data-testid="stMetricValue"] {
  color: var(--c-cyan) !important; font-family: var(--font-code) !important;
  font-size: 1.6rem !important; font-weight: 600 !important;
}
[data-testid="stMetricLabel"] {
  color: var(--c-text3) !important; font-family: var(--font-code) !important;
  font-size: 0.62rem !important; text-transform: uppercase; letter-spacing: 0.15em;
}

[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--c-surface) !important;
  border: 1px solid var(--c-line) !important; border-radius: var(--r-lg) !important;
}
[data-testid="stExpander"] {
  background: var(--c-raise) !important; border: 1px solid var(--c-line) !important;
  border-radius: var(--r-sm) !important;
}
[data-testid="stExpander"] summary {
  color: var(--c-text2) !important; font-family: var(--font-code) !important;
  font-size: 0.8rem !important;
}

[data-testid="stTextInput"] input {
  background: var(--c-raise) !important; color: var(--c-text) !important;
  border: 1px solid var(--c-line2) !important; border-radius: var(--r-sm) !important;
  font-family: var(--font-code) !important; font-size: 0.85rem !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: rgba(6,238,255,0.4) !important; outline: none !important; box-shadow: none !important;
}

[data-testid="stChatInput"] {
  background: var(--c-raise) !important; border: 1px solid var(--c-line2) !important;
  border-radius: var(--r-md) !important; box-shadow: none !important;
}
[data-testid="stChatInput"]:focus-within { border-color: rgba(6,238,255,0.4) !important; }
[data-testid="stChatInput"] textarea {
  background: transparent !important; color: var(--c-text) !important;
  font-family: var(--font-ui) !important; caret-color: var(--c-cyan) !important;
  font-size: 0.95rem !important; border: none !important; outline: none !important; box-shadow: none !important;
}
[data-testid="stChatInputSubmitButton"] button {
  background: linear-gradient(135deg, #0091b0, #5b21b6) !important;
  border: none !important; border-radius: 6px !important;
}
textarea:focus, input:focus { outline: none !important; box-shadow: none !important; }
div[data-baseweb="textarea"], div[data-baseweb="base-input"] {
  border-color: var(--c-line2) !important; background: transparent !important; box-shadow: none !important;
}

hr { border-color: var(--c-line) !important; }
.stCaption, [data-testid="stCaptionContainer"] p {
  color: var(--c-text3) !important; font-family: var(--font-code) !important; font-size: 0.72rem !important;
}
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: var(--c-void); }
::-webkit-scrollbar-thumb { background: var(--c-line2); border-radius: 2px; }
[data-testid="stNotification"], div[data-testid="stAlert"] {
  background: var(--c-raise) !important; border-radius: var(--r-sm) !important; font-family: var(--font-ui) !important;
}

/* ══ SIDEBAR COMPONENTS ══ */
.sb-logo {
  display: flex; align-items: center; gap: 12px;
  padding: 20px 18px 16px; border-bottom: 1px solid var(--c-line);
}
.sb-logo-icon {
  width: 42px; height: 42px; min-width: 42px; border-radius: 10px;
  background: linear-gradient(135deg, rgba(6,238,255,0.12), rgba(167,139,250,0.12));
  border: 1px solid var(--c-line2);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.sb-logo-title {
  font-family: var(--font-ui); font-size: 1.1rem; font-weight: 600;
  background: linear-gradient(110deg, var(--c-text) 0%, var(--c-cyan) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  line-height: 1.2;
}
.sb-logo-sub {
  font-family: var(--font-code); font-size: 0.62rem; color: var(--c-text3);
  letter-spacing: 0.1em; text-transform: uppercase; margin-top: 2px;
}
.sb-section {
  padding: 13px 18px 8px;
  font-family: var(--font-code); font-size: 0.62rem; font-weight: 500;
  color: var(--c-cyan); letter-spacing: 0.15em; text-transform: uppercase;
  display: flex; align-items: center; gap: 7px;
}
.sb-section::after {
  content: ''; flex: 1; height: 1px;
  background: linear-gradient(90deg, var(--c-line2), transparent);
}
.status-pill {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 6px 14px; border-radius: 14px;
  font-family: var(--font-code); font-size: 0.68rem;
  font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase;
}
.status-ready {
  background: rgba(16,255,170,0.07); border: 1px solid rgba(16,255,170,0.25); color: var(--c-green);
}
.status-waiting {
  background: rgba(167,139,250,0.07); border: 1px solid rgba(167,139,250,0.25); color: var(--c-purple);
}
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }

.sb-footer {
  padding: 12px 18px; border-top: 1px solid var(--c-line);
  font-family: var(--font-code); font-size: 0.6rem; color: var(--c-text3);
  letter-spacing: 0.06em; text-align: center; line-height: 1.6;
}
.file-item {
  display: flex; align-items: center; gap: 8px;
  padding: 7px 12px; border-radius: var(--r-sm);
  background: var(--c-raise); border: 1px solid var(--c-line);
  margin-bottom: 5px; font-family: var(--font-code); font-size: 0.74rem; color: var(--c-text2);
}
.file-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--c-green); flex-shrink: 0; }

/* ══ TOPBAR — title uses clamp so it never clips ══ */
.topbar {
  display: flex; align-items: center; gap: 18px;
  padding: 16px 28px;
  border-bottom: 1px solid var(--c-line); background: var(--c-deep);
  width: 100%; overflow: hidden;
}
.topbar-icon {
  width: 54px; height: 54px; min-width: 54px; border-radius: 12px;
  background: linear-gradient(135deg, rgba(6,238,255,0.12), rgba(167,139,250,0.15));
  border: 1px solid var(--c-line2);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.topbar-title-wrap { flex: 1; min-width: 0; }
.topbar-title {
  font-family: var(--font-ui); font-weight: 700;
  letter-spacing: -0.02em; line-height: 1.1;
  background: linear-gradient(110deg, #e2edf8 0%, #06eeff 40%, #a78bfa 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  /* clamp: min 1.5rem, scales with viewport, max 2.6rem — never overflows */
  font-size: clamp(1.5rem, 3.2vw, 2.6rem);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.topbar-sub {
  font-family: var(--font-code); font-size: 0.64rem; color: var(--c-text3);
  letter-spacing: 0.15em; text-transform: uppercase; margin-top: 4px;
}
.topbar-badges {
  margin-left: auto; flex-shrink: 0;
  display: flex; gap: 7px; align-items: center; flex-wrap: wrap;
}
.tb-badge {
  padding: 5px 12px; border-radius: 5px;
  font-family: var(--font-code); font-size: 0.7rem;
  background: var(--c-raise); border: 1px solid var(--c-line2); color: var(--c-text2);
}

/* ══ PANEL HEADERS ══ */
.panel-head {
  display: flex; align-items: center; gap: 8px;
  padding: 13px 18px; border-bottom: 1px solid var(--c-line); background: var(--c-deep);
}
.panel-head-label {
  font-family: var(--font-code); font-size: 0.72rem; font-weight: 500;
  color: var(--c-cyan); letter-spacing: 0.16em; text-transform: uppercase;
}
.panel-head-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--c-cyan); opacity: 0.7; }

/* ══ CHAT MESSAGES ══ */
.chat-empty {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 100%; min-height: 320px; gap: 14px;
  color: var(--c-text3); font-family: var(--font-code); font-size: 0.85rem; letter-spacing: 0.08em;
}
.chat-empty-icon {
  width: 54px; height: 54px; border-radius: 12px;
  background: var(--c-surface); border: 1px solid var(--c-line);
  display: flex; align-items: center; justify-content: center; opacity: 0.5;
}
.msg-row-user { display: flex; justify-content: flex-end; margin: 10px 0; }
.msg-row-ai   { display: flex; justify-content: flex-start; margin: 10px 0; }
.msg-bubble-user {
  max-width: 75%;
  background: linear-gradient(135deg, #071e36, #0a2848);
  border: 1px solid rgba(6,238,255,0.15); border-radius: 13px 3px 13px 13px;
  padding: 12px 16px; color: #c8e6ff;
  font-family: var(--font-ui); font-size: 0.95rem; line-height: 1.6;
}
.msg-bubble-ai {
  max-width: 80%;
  background: var(--c-surface); border: 1px solid var(--c-line);
  border-radius: 3px 13px 13px 13px;
  padding: 12px 16px; color: var(--c-text);
  font-family: var(--font-ui); font-size: 0.95rem; line-height: 1.6;
}
.msg-label {
  font-family: var(--font-code); font-size: 0.63rem;
  letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 4px;
}
.msg-label-user { color: var(--c-cyan); text-align: right; }
.msg-label-ai   { color: var(--c-purple); }

/* ══ DEBUG ══ */
.debug-section { padding: 14px 16px; }
.debug-kv {
  display: flex; justify-content: space-between; align-items: center;
  padding: 7px 0; border-bottom: 1px solid var(--c-line);
  font-family: var(--font-code); font-size: 0.76rem;
}
.debug-kv:last-child { border-bottom: none; }
.debug-key { color: var(--c-text2); }
.debug-val { color: var(--c-cyan); font-weight: 500; }

/* ══ FOOTER ══ */
.footer-bar {
  padding: 14px 22px; border-top: 1px solid var(--c-line); background: var(--c-deep);
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap; justify-content: center;
}
.footer-team {
  font-family: var(--font-script); font-size: 1.5rem;
  color: var(--c-cyan); letter-spacing: 0.05em; font-weight: 600;
}
.chip-name {
  padding: 5px 14px; border-radius: 20px;
  font-family: var(--font-script); font-size: 1.15rem; font-weight: 600;
  background: rgba(167,139,250,0.12); border: 1px solid rgba(167,139,250,0.3); color: #e2b5fd;
}
</style>
""", unsafe_allow_html=True)


# ─── Session State ─────────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "messages": [], "indexed": False, "files": [],
        "rag": None, "status": "ready", "processed_names": set(),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def clear_all_data():
    try:
        shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    except Exception as e:
        logger.error(f"Error clearing uploads: {e}")
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    init_session_state()
    st.rerun()


# ─── File Processing ───────────────────────────────────────────────────────────
def process_uploaded_files(uploaded_files: List) -> bool:
    if not uploaded_files:
        return False
    new_files = [f for f in uploaded_files if f.name not in st.session_state.processed_names]
    if not new_files:
        st.info("All files already indexed.")
        return False
    progress_bar = st.progress(0)
    with st.spinner("Processing..."):
        try:
            if st.session_state.rag is None:
                st.session_state.rag = RAGEngine()
            processed_files = []
            for i, uf in enumerate(new_files):
                try:
                    fp = os.path.join(UPLOAD_FOLDER, uf.name)
                    with open(fp, "wb") as f:
                        f.write(uf.getbuffer())
                    text = FileProcessor.extract_text(fp)
                    if text and text.strip():
                        st.session_state.rag.add_document(text, uf.name)
                        processed_files.append(uf.name)
                        st.session_state.processed_names.add(uf.name)
                        st.success(f"✅ {uf.name}")
                    else:
                        st.warning(f"⚠️ {uf.name} — no text extracted")
                    progress_bar.progress((i + 1) / len(new_files))
                except Exception as e:
                    st.error(f"❌ {uf.name}: {e}")
            if processed_files:
                st.session_state.files.extend(processed_files)
                st.session_state.indexed = True
                return True
            return False
        except Exception as e:
            st.error(f"❌ {e}")
            return False


# ─── Chat Display ──────────────────────────────────────────────────────────────
def display_chat_messages():
    if not st.session_state.messages:
        AI_EMPTY = """<svg width="32" height="32" viewBox="0 0 32 32" fill="none">
          <circle cx="16" cy="16" r="3.5" fill="#06eeff" opacity="0.4"/>
          <circle cx="8"  cy="8"  r="2"   fill="#a78bfa" opacity="0.4"/>
          <circle cx="24" cy="8"  r="2"   fill="#a78bfa" opacity="0.4"/>
          <circle cx="8"  cy="24" r="2"   fill="#a78bfa" opacity="0.4"/>
          <circle cx="24" cy="24" r="2"   fill="#a78bfa" opacity="0.4"/>
          <line x1="16" y1="12.5" x2="9.5"  y2="9.5"  stroke="#06eeff" stroke-width="1" opacity="0.3"/>
          <line x1="16" y1="12.5" x2="22.5" y2="9.5"  stroke="#06eeff" stroke-width="1" opacity="0.3"/>
          <line x1="16" y1="19.5" x2="9.5"  y2="22.5" stroke="#06eeff" stroke-width="1" opacity="0.3"/>
          <line x1="16" y1="19.5" x2="22.5" y2="22.5" stroke="#06eeff" stroke-width="1" opacity="0.3"/>
        </svg>"""
        st.markdown(f"""
        <div class="chat-empty">
          <div class="chat-empty-icon">{AI_EMPTY}</div>
          <div>// awaiting documents</div>
          <div style="font-size:0.7rem;opacity:0.5;">upload files via sidebar to begin querying</div>
        </div>""", unsafe_allow_html=True)
        return

    for msg in st.session_state.messages[-30:]:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="msg-row-user">
              <div>
                <div class="msg-label msg-label-user">you</div>
                <div class="msg-bubble-user">{msg["content"]}</div>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-row-ai">
              <div>
                <div class="msg-label msg-label-ai">rag · assistant</div>
                <div class="msg-bubble-ai">{msg["content"]}</div>
              </div>
            </div>""", unsafe_allow_html=True)
            if msg.get("sources"):
                with st.expander(f"📎 {len(msg['sources'])} source(s)", expanded=False):
                    for src in msg["sources"][:3]:
                        c1, c2 = st.columns([5, 1])
                        with c1:
                            st.markdown(
                                f'<span style="font-family:var(--font-code);color:var(--c-cyan);'
                                f'font-size:0.78rem;">{src.get("filename","Unknown")}</span>',
                                unsafe_allow_html=True)
                            st.caption(src.get("text", "")[:200])
                        with c2:
                            st.caption("📄")


AI_SVG = """<svg width="30" height="30" viewBox="0 0 32 32" fill="none">
  <circle cx="16" cy="16" r="3.8" fill="#06eeff"/>
  <circle cx="7"  cy="7"  r="2.1" fill="#a78bfa"/>
  <circle cx="25" cy="7"  r="2.1" fill="#a78bfa"/>
  <circle cx="7"  cy="25" r="2.1" fill="#a78bfa"/>
  <circle cx="25" cy="25" r="2.1" fill="#a78bfa"/>
  <circle cx="16" cy="4"  r="1.7" fill="#06eeff" opacity="0.7"/>
  <circle cx="16" cy="28" r="1.7" fill="#06eeff" opacity="0.7"/>
  <circle cx="4"  cy="16" r="1.7" fill="#06eeff" opacity="0.7"/>
  <circle cx="28" cy="16" r="1.7" fill="#06eeff" opacity="0.7"/>
  <line x1="16" y1="12.2" x2="9"    y2="9"    stroke="#06eeff" stroke-width="1.1" opacity="0.5"/>
  <line x1="16" y1="12.2" x2="23"   y2="9"    stroke="#06eeff" stroke-width="1.1" opacity="0.5"/>
  <line x1="16" y1="19.8" x2="9"    y2="23"   stroke="#06eeff" stroke-width="1.1" opacity="0.5"/>
  <line x1="16" y1="19.8" x2="23"   y2="23"   stroke="#06eeff" stroke-width="1.1" opacity="0.5"/>
  <line x1="12.2" y1="16" x2="5.7"  y2="16"   stroke="#a78bfa" stroke-width="1.1" opacity="0.5"/>
  <line x1="19.8" y1="16" x2="26.3" y2="16"   stroke="#a78bfa" stroke-width="1.1" opacity="0.5"/>
  <line x1="16" y1="12.2" x2="16"   y2="5.7"  stroke="#a78bfa" stroke-width="1.1" opacity="0.5"/>
  <line x1="16" y1="19.8" x2="16"   y2="26.3" stroke="#a78bfa" stroke-width="1.1" opacity="0.5"/>
</svg>"""

# ═══════════════════════════════════════════════════════════════════════════════
init_session_state()

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div class="sb-logo">
      <div class="sb-logo-icon">{AI_SVG}</div>
      <div>
        <div class="sb-logo-title">RAG Assistant</div>
        <div class="sb-logo-sub">Team 8 · v2.0</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sb-section">Status</div>', unsafe_allow_html=True)
    if st.session_state.indexed:
        st.markdown(
            '<div style="padding:0 18px 14px;">'
            '<span class="status-pill status-ready"><span class="status-dot"></span>Ready</span>'
            '</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="padding:0 18px 14px;">'
            '<span class="status-pill status-waiting"><span class="status-dot"></span>Waiting</span>'
            '</div>', unsafe_allow_html=True)

    if st.session_state.indexed and st.session_state.rag is not None:
        try:
            stats = st.session_state.rag.stats()
            fc = stats.get("docs", len(st.session_state.files))
            cc = stats.get("chunks", 0)
        except Exception:
            fc = len(st.session_state.files)
            cc = 0
        c1, c2 = st.columns(2)
        c1.metric("Files", fc)
        c2.metric("Chunks", cc)

    st.markdown('<div class="sb-section">Documents</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "drop files", accept_multiple_files=True,
        type=["pdf", "docx", "txt", "csv", "xlsx"],
        label_visibility="collapsed",
    )
    if uploaded_files:
        if st.button("⚡ Index Files", type="primary", use_container_width=True):
            success = process_uploaded_files(uploaded_files)
            if success:
                st.rerun()

    if st.session_state.files:
        st.markdown('<div class="sb-section">Indexed</div>', unsafe_allow_html=True)
        st.markdown('<div style="padding:0 18px 10px;">', unsafe_allow_html=True)
        for fname in st.session_state.files[-6:]:
            short = fname[:20] + "…" if len(fname) > 22 else fname
            st.markdown(
                f'<div class="file-item"><div class="file-dot"></div>{short}</div>',
                unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-section">Engine</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="padding:0 18px 14px;">
      <div class="debug-kv"><span class="debug-key">LLM</span><span class="debug-val">GPT-3.5</span></div>
      <div class="debug-kv"><span class="debug-key">Embed</span><span class="debug-val">MiniLM</span></div>
      <div class="debug-kv"><span class="debug-key">Store</span><span class="debug-val">FAISS</span></div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div style="padding:0 18px 14px;">', unsafe_allow_html=True)
    st.button("🗑 Clear All", type="secondary", use_container_width=True, on_click=clear_all_data)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-footer">RAG · FAISS · GPT-3.5 · Streamlit</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN AREA
# ═══════════════════════════════════════════════════════════════════════════════
if not RAG_AVAILABLE:
    st.error("❌ Missing file_processor.py / rag_engine.py")
    st.stop()

# TOPBAR — title uses clamp() so it never clips at any viewport width
st.markdown(f"""
<div class="topbar">
  <div class="topbar-icon">{AI_SVG}</div>
  <div class="topbar-title-wrap">
    <div class="topbar-title">RAG Assistant</div>
    <div class="topbar-sub">// AI · Intelligent · Retrieval</div>
  </div>
  <div class="topbar-badges">
    <span class="tb-badge">PDF</span>
    <span class="tb-badge">DOCX</span>
    <span class="tb-badge">CSV</span>
    <span class="tb-badge">XLSX</span>
    <span class="tb-badge">TXT</span>
  </div>
</div>""", unsafe_allow_html=True)

col_chat, col_debug = st.columns([2.5, 1], gap="small")

# ── CHAT PANEL ────────────────────────────────────────────────────────────────
with col_chat:
    st.markdown("""
    <div class="panel-head">
      <div class="panel-head-dot"></div>
      <span class="panel-head-label">Chat</span>
    </div>""", unsafe_allow_html=True)

    chat_container = st.container(border=True)
    with chat_container:
        display_chat_messages()

    if st.session_state.indexed:
        prompt = st.chat_input("Ask anything about your documents...", key="main_chat")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.markdown(f"""
            <div class="msg-row-user">
              <div>
                <div class="msg-label msg-label-user">you</div>
                <div class="msg-bubble-user">{prompt}</div>
              </div>
            </div>""", unsafe_allow_html=True)

            full_response = ""
            sources = []
            if st.session_state.rag:
                try:
                    for chunk in st.session_state.rag.stream_answer(prompt):
                        full_response += chunk
                    docs = st.session_state.rag.get_sources(prompt)
                    sources = [
                        {"filename": d.metadata.get("filename"), "text": d.page_content[:200]}
                        for d in docs[:3]
                    ]
                    if not full_response.strip():
                        full_response = "No relevant information found."
                except Exception as e:
                    full_response = f"Error: {e}"

                st.markdown(f"""
                <div class="msg-row-ai">
                  <div>
                    <div class="msg-label msg-label-ai">rag · assistant</div>
                    <div class="msg-bubble-ai">{full_response}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

                st.session_state.messages.append({
                    "role": "assistant", "content": full_response, "sources": sources,
                })
                st.rerun()
    else:
        st.markdown(
            '<p style="font-family:var(--font-code);font-size:0.85rem;color:var(--c-text3);'
            'letter-spacing:0.06em;padding:10px 0;">⬆ Upload and index files to start chatting.</p>',
            unsafe_allow_html=True)

# ── DEBUG PANEL ───────────────────────────────────────────────────────────────
with col_debug:
    st.markdown("""
    <div class="panel-head">
      <div class="panel-head-dot" style="background:var(--c-purple)"></div>
      <span class="panel-head-label" style="color:var(--c-purple)">Debug</span>
    </div>""", unsafe_allow_html=True)

    with st.container(border=True):
        if st.session_state.indexed and st.session_state.rag is not None:
            try:
                s = st.session_state.rag.stats()
                chunks = s.get("chunks", 0)
                docs   = s.get("docs", 0)
            except Exception:
                chunks, docs = 0, len(st.session_state.files)

            st.markdown(f"""
            <div class="debug-section">
              <div class="debug-kv"><span class="debug-key">Docs</span><span class="debug-val">{docs}</span></div>
              <div class="debug-kv"><span class="debug-key">Chunks</span><span class="debug-val">{chunks}</span></div>
              <div class="debug-kv"><span class="debug-key">Model</span><span class="debug-val">GPT-3.5</span></div>
              <div class="debug-kv"><span class="debug-key">Embed</span><span class="debug-val">MiniLM</span></div>
              <div class="debug-kv"><span class="debug-key">Vector</span><span class="debug-val">FAISS</span></div>
              <div class="debug-kv"><span class="debug-key">Msgs</span><span class="debug-val">{len(st.session_state.messages)}</span></div>
            </div>""", unsafe_allow_html=True)

            st.markdown("---")

            with st.expander("🔍 Test Query", expanded=False):
                test_q = st.text_input("", key="dbq", placeholder="query...")
                if st.button("Run", key="dbs", use_container_width=True):
                    try:
                        chunks_res = st.session_state.rag.debug_retrieval(test_q)
                        if not chunks_res:
                            st.warning("No results.")
                        for i, c in enumerate(chunks_res[:2]):
                            txt = c.page_content if hasattr(c, "page_content") else str(c)
                            st.text_area(f"#{i+1}", txt[:150], height=60)
                    except Exception as e:
                        st.error(str(e))

            if st.session_state.messages:
                with st.expander("💬 History", expanded=False):
                    for m in st.session_state.messages[-3:]:
                        role_color = "#06eeff" if m["role"] == "user" else "#a78bfa"
                        preview = m["content"][:60] + "…" if len(m["content"]) > 60 else m["content"]
                        st.markdown(
                            f'<div style="font-family:var(--font-code);font-size:0.7rem;'
                            f'color:{role_color};margin-bottom:6px;">'
                            f'[{m["role"]}] <span style="color:var(--c-text2)">{preview}</span></div>',
                            unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="debug-section">
              <div style="font-family:var(--font-code);font-size:0.78rem;color:var(--c-text3);
                          text-align:center;padding:2rem 0;letter-spacing:0.08em;">
                index files<br>to unlock
              </div>
            </div>""", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-bar">
  <span class="footer-team">Team 8</span>
  <span class="chip-name">Abdul Jabbar</span>
  <span class="chip-name">Sk. Yaseen</span>
  <span class="chip-name">L. Pavan Kumar</span>
  <span class="chip-name">Ch. Bharat</span>
</div>""", unsafe_allow_html=True)