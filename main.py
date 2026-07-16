import streamlit as st
import pandas as pd
import json
import os
import uuid
from datetime import datetime
import ast 

# ─── إعداد الصفحة ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sheep Manager Pro", layout="wide")

C_PRIMARY = "#2e7d32"
C_BG = "#102A1F" 

if not os.path.exists("images"): os.makedirs("images")

if "toast" not in st.session_state: st.session_state.toast = None
if st.session_state.toast:
    st.toast(st.session_state.toast)
    st.session_state.toast = None

st.markdown(f"""
<style>
    .stApp {{ background-color: {C_BG}; color: #e8f5e9; direction: rtl; }}
    * {{ text-align: right !important; }}
    .stButton > button {{ background-color: {C_PRIMARY} !important; color: white !important; border-radius: 8px; width: 100%; }}
    [data-testid="stMetricValue"] {{ font-size: 18px !important; color: #a5d6a7 !important; text-align: center !important; }}
</style>
""", unsafe_allow_html=True)

# ─── إدارة البيانات ────────────────────────────────────────────────────────
DATA_FILE = "herd_data.json"
HISTORY_FILE = "medical_history.json"
REQUIRED_COLS = ["ID", "القلادة", "الجنس", "العمر", "وحدة", "عدد الولادات", "صورة", "اللقاحات", "الجرعات", "آخر تغطيس", "الأم", "الأبناء"]

def save_image(uploaded_file):
    if uploaded_file is not None:
        file_path = f"images/{uuid.uuid4()}.jpg"
        with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
        return file_path
    return ""

def load_data(file, columns):
    if not os.path.exists(file): return pd.DataFrame(columns=columns)
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return pd.DataFrame(data)
    except: return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_json(file, orient="records", force_ascii=False, indent=4)

if "herd" not in st.session_state: st.session_state.herd = load_data(DATA_FILE, REQUIRED_COLS)
if "history" not in st.session_state: st.session_state.history = load_data(HISTORY_FILE, ["ID", "التاريخ", "الإجراء", "العلاج", "الأغنام", "صورة"])

# ─── واجهة التطبيق ─────────────────────────────────────────────────────────
st.title("🐑 Sheep Manager Pro")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 القطيع", "💉 إجراء", "📋 السجل", "➕ إدارة", "⚙️ الإعدادات"])

with tab1:
    st.subheader("📊 إحصائيات القطيع")
    if not st.session_state.herd.empty:
        df = st.session_state.herd
        col1, col2 = st.columns(2)
        with col1: st.metric("🐑 العدد الكلي", len(df))
        with col2: st.metric("♂️ ذكور", len(df[df["الجنس"].isin(["ذكر", "ذكر صغير"])]))
        for idx, row in df.iterrows():
            with st.expander(f"🏷️ {row['القلادة']}"):
                if row.get('صورة') and os.path.exists(row['صورة']): st.image(row['صورة'], width=150)
                st.write(f"**الجنس:** {row.get('الجنس')}")

with tab2:
    st.subheader("💉 إجراء طبي")
    if not st.session_state.herd.empty:
        selected = st.multiselect("اختر الأغنام:", st.session_state.herd["القلادة"].tolist())
        action = st.radio("نوع الإجراء:", ["تطعيم", "جرعة طفيلية", "تغطيس"], horizontal=True)
        if st.button("حفظ الإجراء"):
            new_hist = pd.DataFrame([{"ID": str(datetime.now().timestamp()), "التاريخ": str(datetime.now().date()), "الإجراء": action, "العلاج": "...", "الأغنام": ", ".join(selected), "صورة": ""}])
            st.session_state.history = pd.concat([st.session_state.history, new_hist], ignore_index=True)
            save_data(st.session_state.history, HISTORY_FILE)
            st.rerun()

with tab3:
    st.subheader("📋 السجل الطبي")
    st.dataframe(st.session_state.history)

with tab4:
    st.subheader("➕ إدارة القطيع")
    with st.form("add_form"):
        collar = st.text_input("القلادة")
        if st.form_submit_button("إضافة"):
            new_row = pd.DataFrame([{"ID": str(datetime.now().timestamp()), "القلادة": collar, "الجنس": "ذكر", "صورة": ""}])
            st.session_state.herd = pd.concat([st.session_state.herd, new_row], ignore_index=True)
            save_data(st.session_state.herd, DATA_FILE)
            st.rerun()

# ─── تبويب الإعدادات (الاستعادة الموحدة) ───────────────────────────────────
with tab5:
    st.subheader("⚙️ الإعدادات العامة")
    # التصدير
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "rb") as f: st.download_button("📥 تحميل القطيع", f, file_name="herd_data.json")
    with col_d2:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "rb") as f: st.download_button("📥 تحميل السجل", f, file_name="medical_history.json")
    
    st.divider()
    st.subheader("🔄 استعادة البيانات")
    u1 = st.file_uploader("📂 ملف القطيع", type=['json'])
    u2 = st.file_uploader("📂 ملف السجل", type=['json'])
    
    if st.button("🚀 استعادة الكل الآن", type="primary"):
        if u1:
            st.session_state.herd = pd.DataFrame(json.load(u1))
            save_data(st.session_state.herd, DATA_FILE)
        if u2:
            st.session_state.history = pd.DataFrame(json.load(u2))
            save_data(st.session_state.history, HISTORY_FILE)
        st.success("تمت الاستعادة بنجاح!")
   
        st.rerun()
