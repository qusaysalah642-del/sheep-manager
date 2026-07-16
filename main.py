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
    p, div, h1, h2, h3, h4, h5, h6, label, span {{ direction: rtl; }}
    .stButton > button {{ background-color: {C_PRIMARY} !important; color: white !important; border-radius: 8px; width: 100%; }}
    [data-testid="stMetricValue"] {{ font-size: 18px !important; color: #a5d6a7 !important; text-align: center !important; }}
    [data-testid="stMetricLabel"] {{ font-size: 14px !important; color: #c8e6c9 !important; text-align: center !important; }}
    .stTabs [data-baseweb="tab-list"] {{ direction: rtl; gap: 5px; flex-wrap: wrap; }}
    [data-testid="collapsedControl"] {{ display: none; }}
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
            df = pd.DataFrame(data)
            for col in columns:
                if col not in df.columns:
                    if col == "الأبناء": df[col] = "[]"
                    elif col == "الأم": df[col] = ""
                    else: df[col] = "شهر" if col == "وحدة" else ("[]" if col in ["اللقاحات", "الجرعات"] else "")
            return df
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
    df = st.session_state.herd
    if not df.empty:
        total, males, females, young = len(df), len(df[df["الجنس"].isin(["ذكر", "ذكر صغير"])]), len(df[df["الجنس"].isin(["أنثى", "أنثى صغيرة"])]), len(df[df["الجنس"].str.contains("صغير", na=False)])
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True): st.metric("🐑 العدد الكلي", total)
            with st.container(border=True): st.metric("♂️ ذكور", males)
        with col2:
            with st.container(border=True): st.metric("♀️ إناث", females)
            with st.container(border=True): st.metric("👶 صغار", young)
    st.divider()
    if not df.empty:
        for idx, row in df.iterrows():
            try: kids_list = ast.literal_eval(row.get('الأبناء', '[]'))
            except: kids_list = []
            with st.expander(f"🏷️ {row['القلادة']}"):
                col_img, col_info = st.columns([1, 2])
                with col_img:
                    if row.get('صورة') and os.path.exists(row['صورة']): st.image(row['صورة'], use_container_width=True)
                with col_info:
                    st.write(f"**الجنس:** {row.get('الجنس', 'غير معروف')}")
                    st.write(f"**العمر:** {row.get('العمر', 0)} {row.get('وحدة', 'شهر')}")
                    st.write(f"**الولادات:** {row.get('عدد الولادات', 0)}")
                    if row.get('الأم'): st.write(f"**الأم:** {row['الأم']}")
                    if kids_list: 
                        st.write("**الأبناء:**")
                        for i, kid in enumerate(kids_list, 1): st.write(f"{i}. {kid}")
    else: st.info("القطيع فارغ حالياً.")

with tab2:
    st.subheader("💉 إجراء طبي")
    if not st.session_state.herd.empty:
        selected_collars = st.multiselect("اختر الأغنام:", st.session_state.herd["القلادة"].tolist())
        action_type = st.radio("نوع الإجراء:", ["تطعيم", "جرعة طفيلية", "تغطيس"], horizontal=True)
        tr_opts = ['إيفومك', 'معوي/دموي', 'طاعون', 'جدري', 'حمى قلاعية'] if action_type == "تطعيم" else (['جرعة كبدية', 'جرعة معوية'] if action_type == "جرعة طفيلية" else ['تغطيس شامل'])
        treatment = st.selectbox("العلاج:", tr_opts)
        date = str(st.date_input("التاريخ:"))
        img_file = st.file_uploader("صورة التوثيق (اختياري)", type=['jpg', 'png'])
        if st.button("حفظ الإجراء"):
            img_path = save_image(img_file)
            new_hist = pd.DataFrame([{"ID": str(datetime.now().timestamp()), "التاريخ": date, "الإجراء": action_type, "العلاج": treatment, "الأغنام": ", ".join(selected_collars), "صورة": img_path}])
            st.session_state.history = pd.concat([st.session_state.history, new_hist], ignore_index=True)
            save_data(st.session_state.history, HISTORY_FILE)
            st.session_state.toast = "تمت إضافة الإجراء بنجاح! ✅"
            st.rerun()

with tab3:
    st.subheader("📋 السجل الطبي")
    if not st.session_state.history.empty:
        for idx, row in st.session_state.history.iterrows():
            with st.expander(f"🗓️ {row['التاريخ']} - {row['الإجراء']} ({row['العلاج']})"):
                if row.get('صورة') and os.path.exists(row['صورة']): st.image(row['صورة'], width=100)
                if st.button("🗑️ حذف السجل", key=f"del_{idx}"):
                    st.session_state.history = st.session_state.history.drop(idx)
                    save_data(st.session_state.history, HISTORY_FILE)
                    st.rerun()

with tab4:
    st.subheader("➕ إدارة القطيع")
    with st.expander("إضافة رأس جديد"):
        with st.form("add_form"):
            collar = st.text_input("القلادة")
            gender = st.selectbox("الجنس", ["أنثى", "ذكر", "أنثى صغيرة", "ذكر صغير"])
            age_val = st.number_input("العمر", 0)
            age_unit = st.radio("وحدة:", ["شهر", "سنة"], horizontal=True)
            births = st.number_input("الولادات", 0)
            img_file = st.file_uploader("صورة", type=['jpg', 'png'])
            if st.form_submit_button("إضافة"):
                img_path = save_image(img_file)
                new_row = pd.DataFrame([{"ID": str(datetime.now().timestamp()), "القلادة": collar, "الجنس": gender, "العمر": age_val, "وحدة": age_unit, "عدد الولادات": births, "صورة": img_path, "الأبناء": "[]"}])
                st.session_state.herd = pd.concat([st.session_state.herd, new_row], ignore_index=True)
                save_data(st.session_state.herd, DATA_FILE)
                st.rerun()

    st.subheader("✏️ تعديل / حذف")
    if not st.session_state.herd.empty:
        selected_edit_collar = st.selectbox("اختر للتحرير:", st.session_state.herd["القلادة"].tolist())
        sheep_row = st.session_state.herd[st.session_state.herd["القلادة"] == selected_edit_collar].iloc[0]
        idx = st.session_state.herd[st.session_state.herd["القلادة"] == selected_edit_collar].index[0]
        with st.form("edit_form"):
            edit_collar = st.text_input("القلادة", value=sheep_row["القلادة"])
            if st.form_submit_button("حذف الرأس نهائياً ⚠️"):
                st.session_state.herd = st.session_state.herd.drop(idx)
                save_data(st.session_state.herd, DATA_FILE)
                st.rerun()

with tab5:
    st.subheader("⚙️ الإعدادات العامة")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "rb") as f: st.download_button("📥 تحميل القطيع", f, file_name="herd_data.json")
    with col_d2:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "rb") as f: st.download_button("📥 تحميل السجل", f, file_name="medical_history.json")
    
    st.divider()
    st.subheader("🔄 الاستعادة الموحدة")
    col_u1, col_u2 = st.columns(2)
    with col_u1: uploaded_herd = st.file_uploader("📂 ملف القطيع", type=['json'])
    with col_u2: uploaded_hist = st.file_uploader("📂 ملف السجل", type=['json'])
        
    if st.button("استعادة الكل الآن ⚠️", type="primary"):
        success = True
        if uploaded_herd:
            try:
                st.session_state.herd = pd.DataFrame(json.load(uploaded_herd))
                save_data(st.session_state.herd, DATA_FILE)
            except: success = False
        if uploaded_hist:
            try:
                st.session_state.history = pd.DataFrame(json.load(uploaded_hist))
                save_data(st.session_state.history, HISTORY_FILE)
            except: success = False
        if success:
            st.session_state.toast = "تمت الاستعادة بنجاح!"
            st.rerun()
        else: st.error("خطأ في الاستعادة.")
            
