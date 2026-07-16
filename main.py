import streamlit as st
import pandas as pd
import json
import os
import uuid
from datetime import datetime
import ast 

st.set_page_config(page_title="Sheep Manager Pro", layout="wide")

# CSS لإجبار المتصفح على عرض العناصر بشكل صحيح
st.markdown("""
<style>
    .stApp { background-color: #102A1F; color: #e8f5e9; direction: rtl; }
    * { text-align: right !important; }
    .stButton > button { background-color: #2e7d32 !important; color: white !important; border-radius: 8px; width: 100%; margin-top: 10px; }
    [data-testid="collapsedControl"] { display: none; }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "herd_data.json"
HISTORY_FILE = "medical_history.json"

# دوال البيانات
def load_data(file):
    if not os.path.exists(file): return pd.DataFrame()
    with open(file, "r", encoding="utf-8") as f: return pd.DataFrame(json.load(f))

def save_data(df, file):
    df.to_json(file, orient="records", force_ascii=False, indent=4)

if "herd" not in st.session_state: st.session_state.herd = load_data(DATA_FILE)
if "history" not in st.session_state: st.session_state.history = load_data(HISTORY_FILE)

st.title("🐑 Sheep Manager Pro")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠", "💉", "📋", "➕", "⚙️"])

with tab5:
    st.subheader("⚙️ الإعدادات")
    
    # تحميل
    if st.button("📥 تحميل النسخ الاحتياطية"):
        st.write("الروابط ستظهر أدناه:")
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "rb") as f: st.download_button("تحميل القطيع", f, "herd.json")
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "rb") as f: st.download_button("تحميل السجل", f, "hist.json")

    st.divider()
    st.subheader("🔄 الاستعادة الموحدة")
    
    # رفع الملفات
    u1 = st.file_uploader("📂 ملف القطيع", type=['json'], key="u1")
    u2 = st.file_uploader("📂 ملف السجل", type=['json'], key="u2")
    
    # زر الاستعادة موجود هنا ومباشر
    if st.button("🚀 اضغط هنا لاستعادة البيانات المرفوعة", type="primary"):
        if u1:
            st.session_state.herd = pd.DataFrame(json.load(u1))
            save_data(st.session_state.herd, DATA_FILE)
        if u2:
            st.session_state.history = pd.DataFrame(json.load(u2))
            save_data(st.session_state.history, HISTORY_FILE)
        st.success("تم التحديث! يرجى عمل Refresh للصفحة.")
        st.rerun()

# باقي التبويبات (اختصار لتوفير المساحة)
with tab1: st.write("القطيع:", len(st.session_state.herd))
with tab2: st.write("أضف إجراء طبي من هنا")
with tab3: st.write("السجل الطبي")
with tab4: st.write("إدارة
القطيع")
