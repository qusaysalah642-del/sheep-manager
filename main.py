import streamlit as st
import pandas as pd
import json
import os
import uuid
import ast
from datetime import datetime

# ─── إعداد الصفحة ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sheep Manager Pro", page_icon="🐑", layout="wide")

# نظام الألوان والخطوط
C_BG_DEEP = "#0b1f16"
C_BG_PANEL = "#123326"
C_BG_PANEL_2 = "#16402f"
C_BORDER = "rgba(255,255,255,0.08)"
C_TEXT = "#eef6f0"
C_TEXT_MUTED = "#93b3a1"
C_GREEN = "#4c9a6a"
C_GREEN_DARK = "#2f6b48"
C_AMBER = "#d3a15c"
C_AMBER_DARK = "#a97c3c"
C_DANGER = "#e2665a"

if not os.path.exists("images"): os.makedirs("images")
if "toast" not in st.session_state: st.session_state.toast = None
if st.session_state.toast:
    st.toast(st.session_state.toast)
    st.session_state.toast = None

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;700;800&family=Tajawal:wght@400;500;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Tajawal', sans-serif; }}
    h1, h2, h3, .app-hero-title {{ font-family: 'Cairo', sans-serif; }}
    .stApp {{ background: linear-gradient(180deg, {C_BG_DEEP} 0%, #0e2a1e 100%); color: {C_TEXT}; }}
    .app-hero {{ display: flex; align-items: center; gap: 18px; background: linear-gradient(135deg, {C_BG_PANEL} 0%, {C_BG_DEEP} 100%); border: 1px solid {C_BORDER}; border-radius: 18px; padding: 22px 28px; margin-bottom: 22px; box-shadow: 0 6px 24px rgba(0,0,0,0.25); }}
    .app-hero-icon {{ font-size: 40px; line-height: 1; background: linear-gradient(135deg, {C_AMBER}, {C_AMBER_DARK}); width: 64px; height: 64px; border-radius: 16px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 4px 14px rgba(211,161,92,0.25); }}
    .app-hero-title {{ font-size: 26px; font-weight: 800; margin: 0; color: {C_TEXT}; }}
    .app-hero-subtitle {{ font-size: 14px; color: {C_TEXT_MUTED}; margin-top: 2px; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; background: transparent; }}
    .stTabs [data-baseweb="tab"] {{ background: {C_BG_PANEL}; border: 1px solid {C_BORDER}; border-radius: 999px !important; padding: 8px 20px; color: {C_TEXT_MUTED}; font-weight: 700; }}
    .stTabs [aria-selected="true"] {{ background: linear-gradient(135deg, {C_GREEN} 0%, {C_GREEN_DARK} 100%) !important; color: white !important; border: 1px solid {C_GREEN} !important; }}
    [data-testid="stExpander"] {{ background: {C_BG_PANEL}; border: 1px solid {C_BORDER} !important; border-radius: 14px !important; margin-bottom: 10px; }}
    .stButton > button {{ background: linear-gradient(135deg, {C_GREEN} 0%, {C_GREEN_DARK} 100%); color: white; border: none; border-radius: 10px; width: 100%; font-weight: 700; padding: 10px 0; }}
    .stButton > button[kind="primary"] {{ background: linear-gradient(135deg, {C_DANGER} 0%, #b8443a 100%); }}
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {{ background: {C_BG_DEEP} !important; border: 1px solid {C_BORDER} !important; border-radius: 10px !important; color: {C_TEXT} !important; }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-hero"><div class="app-hero-icon">🐑</div><div><p class="app-hero-title">Sheep Manager Pro</p><p class="app-hero-subtitle">إدارة القطيع والسجل الطبي</p></div></div>', unsafe_allow_html=True)

# ─── إدارة البيانات ────────────────────────────────────────────────────────
DATA_FILE = "herd_data.json"
HISTORY_FILE = "medical_history.json"
REQUIRED_COLS = ["ID", "القلادة", "الجنس", "العمر", "وحدة", "عدد الولادات", "صورة", "اللقاحات", "الجرعات", "آخر تغطيس", "الأم", "الأبناء"]
HISTORY_COLS = ["ID", "التاريخ", "الإجراء", "العلاج", "الأغنام", "صورة"]

def save_image(uploaded_file):
    if uploaded_file is not None:
        file_path = f"images/{uuid.uuid4()}.jpg"
        with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
        return file_path
    return ""

def safe_delete_image(path):
    if path and isinstance(path, str) and os.path.exists(path):
        try: os.remove(path)
        except: pass

def safe_literal_eval(value):
    try: return ast.literal_eval(value) if isinstance(value, str) else value
    except: return []

def load_data(file, columns):
    if not os.path.exists(file): return pd.DataFrame(columns=columns)
    try:
        with open(file, "r", encoding="utf-8") as f: return pd.DataFrame(json.load(f))
    except: return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_json(file, orient="records", force_ascii=False, indent=4)

if "herd" not in st.session_state: st.session_state.herd = load_data(DATA_FILE, REQUIRED_COLS)
if "history" not in st.session_state: st.session_state.history = load_data(HISTORY_FILE, HISTORY_COLS)

# ─── واجهة التطبيق ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 القطيع", "💉 إجراء", "📋 السجل", "⚙️ إدارة", "💾 النسخة الاحتياطية"])

with tab1:
    st.subheader("📊 إحصائيات القطيع")
    if not st.session_state.herd.empty:
        for idx, row in st.session_state.herd.iterrows():
            with st.expander(f"🏷️ {row['القلادة']}"):
                st.write(f"الجنس: {row['الجنس']} | العمر: {row['العمر']} {row['وحدة']}")
    else: st.info("لا توجد بيانات")

with tab2:
    st.subheader("💉 تسجيل إجراء طبي")
    # ... (كود تسجيل الإجراء) ...

with tab3:
    st.subheader("📋 السجل الطبي")
    # ... (كود عرض السجل الطبي) ...

with tab4:
    st.subheader("⚙️ إدارة القطيع")
    st.markdown("---")
    
    # قسم الحذف (تم إصلاحه ليعتمد على Index)
    st.markdown("### 🗑️ حذف رأس من القطيع")
    if not st.session_state.herd.empty:
        sheep_id_to_delete = st.selectbox("اختر الرأس للحذف:", st.session_state.herd["ID"].tolist(), format_func=lambda x: st.session_state.herd[st.session_state.herd["ID"]==x].iloc[0]["القلادة"], key="del_select")
        if st.button("تأكيد الحذف نهائياً", type="primary"):
            row_idx = st.session_state.herd[st.session_state.herd["ID"] == sheep_id_to_delete].index[0]
            safe_delete_image(st.session_state.herd.at[row_idx, "صورة"])
            st.session_state.herd = st.session_state.herd.drop(row_idx).reset_index(drop=True)
            save_data(st.session_state.herd, DATA_FILE)
            st.success("تم الحذف!")
            st.rerun()

with tab5:
    st.header("💾 النسخة الاحتياطية")
    col1, col2 = st.columns(2)
    with col1:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "rb") as f: st.download_button("📥 تحميل بيانات القطيع", f, "herd_data.json")
    with col2:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "rb") as f: st.download_button("📥 تحميل السجل الطبي", f, "medical_history.json")
    
    st.divider()
    st.subheader("🔄 استعادة البيانات")
    u1 = st.file_uploader("رفع ملف القطيع (JSON)", type=['json'])
    u2 = st.file_uploader("رفع ملف السجل (JSON)", type=['json'])
    if st.button("🚀 استعادة البيانات الآن"):
        if u1:
            st.session_state.herd = pd.read_json(u1)
            save_data(st.session_state.herd, DATA_FILE)
        if u2:
            st.session_state.history = pd.read_json(u2)
            save_data(st.session_state.history, HISTORY_FILE)
        st.success("تمت الاستعادة بنجاح!")
        st.rerun()
        
