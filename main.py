import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ─── إعداد الصفحة ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sheep Manager Pro", layout="wide")

C_PRIMARY = "#2e7d32"
C_BG = "#0d2818"

st.markdown(f"""
<style>
    .stApp {{ background-color: {C_BG}; color: #e8f5e9; }}
    .stButton > button {{ background-color: {C_PRIMARY}; color: white; border-radius: 8px; }}
</style>
""", unsafe_allow_html=True)

# ─── إدارة البيانات ────────────────────────────────────────────────────────
DATA_FILE = "herd_data.json"

def init_df():
    return pd.DataFrame(columns=[
        "ID", "القلادة", "الجنس", "العمر", "عدد الولادات", "الحالة الصحية", 
        "اللقاحات", "الجرعات", "آخر تغطيس"
    ])

def load_data():
    if not os.path.exists(DATA_FILE): return init_df()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            df = pd.DataFrame(json.load(f))
            cols = ["ID", "القلادة", "الجنس", "العمر", "عدد الولادات", "الحالة الصحية", "اللقاحات", "الجرعات", "آخر تغطيس"]
            for col in cols:
                if col not in df.columns: df[col] = 0 if col in ["العمر", "عدد الولادات"] else ""
            return df
    except: return init_df()

def save_data(df):
    df.to_json(DATA_FILE, orient="records", force_ascii=False, indent=4)

if "herd" not in st.session_state: st.session_state.herd = load_data()
if "edit_id" not in st.session_state: st.session_state.edit_id = None

# ─── واجهة التطبيق ─────────────────────────────────────────────────────────
st.title("🐑 Sheep Manager Pro")
tab1, tab2, tab3 = st.tabs(["🏠 القطيع", "💉 السجل الصحي", "➕ إضافة/تعديل"])

with tab1:
    st.subheader("سجل القطيع")
    filter_type = st.selectbox("فرز القطيع حسب:", ["الكل", "ذكر", "أنثى", "ذكر صغير", "أنثى صغيرة"])
    df = st.session_state.herd
    if filter_type != "الكل": df = df[df["الجنس"] == filter_type]
    
    for idx, row in df.iterrows():
        col1, col2 = st.columns([0.8, 0.2])
        col1.write(f"🏷️ **{row['القلادة']}** | {row['الجنس']} | عمر: {row['العمر']} شهر | ولادات: {row['عدد الولادات']}")
        if col2.button("تعديل", key=f"edit_{row['ID']}"):
            st.session_state.edit_id = row['ID']
            st.rerun()

with tab2:
    st.subheader("تسجيل إجراء طبي")
    selected_collars = st.multiselect("اختر الأغنام:", st.session_state.herd["القلادة"].tolist())
    action_type = st.radio("نوع الإجراء:", ["تطعيم", "جرعة طفيلية", "تغطيس"])
    
    # ── قائمة العلاجات المتغيرة حسب النوع ──
    if action_type == "تطعيم":
        treatment_options = ['إيفومك', 'معوي/دموي', 'طاعون', 'جدري', 'حمى قلاعية']
    elif action_type == "جرعة طفيلية":
        treatment_options = ['جرعة كبدية', 'جرعة معوية']
    else:
        treatment_options = ['تغطيس شامل']
        
    treatment = st.selectbox("نوع العلاج/اللقاح:", treatment_options)
    date = st.date_input("التاريخ:")
    
    if st.button("حفظ الإجراء"):
        for collar in selected_collars:
            idx = st.session_state.herd[st.session_state.herd["القلادة"] == collar].index[0]
            if action_type == "تغطيس": st.session_state.herd.at[idx, "آخر تغطيس"] = str(date)
            else: 
                col_name = "اللقاحات" if action_type == "تطعيم" else "الجرعات"
                val = st.session_state.herd.at[idx, col_name]
                current = json.loads(val) if isinstance(val, str) and val else []
                if treatment not in current: current.append(treatment)
                st.session_state.herd.at[idx, col_name] = json.dumps(current)
        save_data(st.session_state.herd)
        st.success("تم الحفظ!")

with tab3:
    if st.session_state.edit_id:
        st.subheader("تعديل")
        target_id = st.session_state.edit_id
        row_idx = st.session_state.herd[st.session_state.herd["ID"] == target_id].index[0]
        animal = st.session_state.herd.loc[row_idx]
        with st.form("edit_form"):
            new_collar = st.text_input("القلادة", animal["القلادة"])
            new_births = st.number_input("عدد الولادات", value=int(animal["عدد الولادات"]))
            if st.form_submit_button("حفظ"):
                st.session_state.herd.at[row_idx, "القلادة"] = new_collar
                st.session_state.herd.at[row_idx, "عدد الولادات"] = new_births
                st.session_state.edit_id = None
                save_data(st.session_state.herd)
                st.rerun()
    else:
        st.subheader("إضافة رأس جديد")
        with st.form("add_form"):
            collar = st.text_input("رقم القلادة")
            gender = st.selectbox("الجنس", ["أنثى", "ذكر", "أنثى صغيرة", "ذكر صغير"])
            age = st.number_input("العمر (أشهر)", 0)
            births = st.number_input("عدد الولادات (للالاناث فقط)", 0) if gender == "أنثى" else 0
            submitted = st.form_submit_button("إضافة")
            if submitted:
                new_row = pd.DataFrame([{
                    "ID": str(datetime.now().timestamp()), "القلادة": collar, "الجنس": gender,
                    "العمر": age, "عدد الولادات": births, "الحالة الصحية": "سليم",
                    "اللقاحات": "[]", "الجرعات": "[]", "آخر تغطيس": ""
                }])
                st.session_state.herd = pd.concat([st.session_state.herd, new_row], ignore_index=True)
                save_data(st.session_state.herd)
              
                st.rerun()
