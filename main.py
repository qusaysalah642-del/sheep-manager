import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ─── إعداد الصفحة ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sheep Manager Pro", layout="wide")

# ─── الإعدادات والألوان ────────────────────────────────────────────────────────
C_PRIMARY = "#2e7d32"
C_BG = "#0d2818"

st.markdown(f"""
<style>
    .stApp {{ background-color: {C_BG}; color: #e8f5e9; }}
    .stButton > button {{ background-color: {C_PRIMARY}; color: white; border-radius: 8px; }}
    .metric-card {{ background: #1b3a2a; padding: 15px; border-radius: 10px; border: 1px solid #388e3c; }}
</style>
""", unsafe_allow_html=True)

# ─── إدارة البيانات (JSON) ──────────────────────────────────────────────────
DATA_FILE = "herd_data.json"

def init_df():
    return pd.DataFrame(columns=[
        "ID", "القلادة", "الجنس", "العمر", "الحالة الصحية", 
        "اللقاحات", "الجرعات", "آخر تغطيس"
    ])

def load_data():
    if not os.path.exists(DATA_FILE):
        return init_df()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            df = pd.DataFrame(data)
            # التأكد من وجود الأعمدة الطبية
            for col in ["اللقاحات", "الجرعات", "آخر تغطيس"]:
                if col not in df.columns: df[col] = "[]"
            return df
    except:
        return init_df()

def save_data(df):
    df.to_json(DATA_FILE, orient="records", force_ascii=False, indent=4)

if "herd" not in st.session_state:
    st.session_state.herd = load_data()

# ─── واجهة التطبيق ─────────────────────────────────────────────────────────
st.title("🐑 Sheep Manager Pro")

tab1, tab2, tab3 = st.tabs(["🏠 القطيع", "💉 السجل الصحي", "➕ إضافة/حذف"])

with tab1:
    st.subheader("سجل القطيع")
    st.dataframe(st.session_state.herd, use_container_width=True)

with tab2:
    st.subheader("تسجيل إجراء طبي")
    col1, col2 = st.columns(2)
    with col1:
        selected_collar = st.selectbox("اختر القلادة:", st.session_state.herd["القلادة"].tolist())
        action_type = st.radio("نوع الإجراء:", ["تطعيم", "جرعة طفيلية", "تغطيس"])
    with col2:
        if action_type == "تطعيم":
            treatment = st.selectbox("نوع اللقاح:", ["إيفومك", "معوي/دموي", "طاعون", "جدري", "حمى قلاعية"])
            key_to_update = "اللقاحات"
        elif action_type == "جرعة طفيلية":
            treatment = st.selectbox("نوع الجرعة:", ["جرعة كبدية", "جرعة معوية"])
            key_to_update = "الجرعات"
        else:
            treatment = "تغطيس شامل"
            key_to_update = "آخر تغطيس"
        
        date = st.date_input("التاريخ:")

    if st.button("حفظ الإجراء الطبي"):
        idx = st.session_state.herd[st.session_state.herd["القلادة"] == selected_collar].index[0]
        
        if action_type == "تغطيس":
            st.session_state.herd.at[idx, key_to_update] = str(date)
        else:
            # تحديث قائمة اللقاحات أو الجرعات
            current_list = json.loads(st.session_state.herd.at[idx, key_to_update])
            if treatment not in current_list:
                current_list.append(treatment)
            st.session_state.herd.at[idx, key_to_update] = json.dumps(current_list)
        
        save_data(st.session_state.herd)
        st.success(f"تم تسجيل {action_type} للقلادة {selected_collar}")

with tab3:
    st.subheader("إضافة رأس جديد")
    with st.form("add_animal"):
        collar = st.text_input("رقم القلادة")
        gender = st.selectbox("الجنس", ["أنثى (نعجة)", "ذكر (كبش)", "ذكر (فحل)", "طلية", "بكري"])
        age = st.number_input("العمر (أشهر)", 0, 240)
        submitted = st.form_submit_button("إضافة")
        if submitted:
            new_row = pd.DataFrame([{
                "ID": str(datetime.now().timestamp()),
                "القلادة": collar,
                "الجنس": gender,
                "العمر": age,
                "الحالة الصحية": "سليم",
                "اللقاحات": "[]",
                "الجرعات": "[]",
                "آخر تغطيس": ""
            }])
            st.session_state.herd = pd.concat([st.session_state.herd, new_row], ignore_index=True)
            save_data(st.session_state.herd)
         
            st.rerun()
