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
C_BG = "#0d2818"

if not os.path.exists("images"): os.makedirs("images")

if "toast" not in st.session_state: st.session_state.toast = None
if st.session_state.toast:
    st.toast(st.session_state.toast)
    st.session_state.toast = None

st.markdown(f"""
<style>
    .stApp {{ background-color: {C_BG}; color: #e8f5e9; }}
    .stButton > button {{ background-color: {C_PRIMARY}; color: white; border-radius: 8px; width: 100%; }}
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
tab1, tab2, tab3, tab4 = st.tabs(["🏠 القطيع", "💉 إجراء", "📋 السجل", "➕ إدارة"])

with tab1:
    st.subheader("📊 إحصائيات القطيع")
    df = st.session_state.herd
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1: st.metric("🐑 العدد الكلي", len(df))
        with col2: st.metric("♀️ إناث", len(df[df["الجنس"].isin(["أنثى", "أنثى صغيرة"])]))
    
    st.divider()
    if not df.empty:
        for idx, row in df.iterrows():
            try: kids_list = ast.literal_eval(row['الأبناء'])
            except: kids_list = []
            with st.expander(f"🏷️ {row['القلادة']}"):
                col_img, col_info = st.columns([1, 2])
                with col_img:
                    if row.get('صورة') and os.path.exists(row['صورة']): st.image(row['صورة'], use_container_width=True)
                with col_info:
                    st.write(f"**الجنس:** {row.get('الجنس')}")
                    st.write(f"**العمر:** {row.get('العمر', 0)} {row.get('وحدة', 'شهر')}")
                    if row.get('الأم'): st.write(f"**الأم:** {row['الأم']}")
                    if len(kids_list) > 0: st.write(f"**الأبناء:** {', '.join(kids_list)}")

with tab2:
    st.subheader("💉 إجراء طبي")
    if not st.session_state.herd.empty:
        selected_collars = st.multiselect("اختر الأغنام:", st.session_state.herd["القلادة"].tolist())
        action_type = st.radio("نوع الإجراء:", ["تطعيم", "جرعة طفيلية", "تغطيس"], horizontal=True)
        treatment = st.selectbox("العلاج:", ['إيفومك', 'معوي/دموي', 'طاعون', 'جدري', 'حمى قلاعية', 'جرعة كبدية', 'تغطيس شامل'])
        date = str(st.date_input("التاريخ:"))
        if st.button("حفظ الإجراء"):
            new_hist = pd.DataFrame([{"ID": str(datetime.now().timestamp()), "التاريخ": date, "الإجراء": action_type, "العلاج": treatment, "الأغنام": ", ".join(selected_collars), "صورة": ""}])
            st.session_state.history = pd.concat([st.session_state.history, new_hist], ignore_index=True)
            save_data(st.session_state.history, HISTORY_FILE)
            st.rerun()

with tab3:
    st.subheader("📋 السجل الطبي")
    if not st.session_state.history.empty:
        for idx, row in st.session_state.history.iterrows():
            with st.expander(f"🗓️ {row['التاريخ']} - {row['الإجراء']}"):
                if st.button("🗑️ حذف السجل", key=f"del_{idx}"):
                    st.session_state.history = st.session_state.history.drop(idx)
                    save_data(st.session_state.history, HISTORY_FILE)
                    st.rerun()

with tab4:
    st.subheader("➕ إدارة القطيع")
    with st.expander("➕ إضافة رأس جديد", expanded=True):
        with st.form("add_form"):
            collar = st.text_input("القلادة")
            gender = st.selectbox("الجنس", ["أنثى", "ذكر", "أنثى صغيرة", "ذكر صغير"])
            age_val = st.number_input("العمر:", 0)
            age_unit = st.selectbox("الوحدة:", ["شهر", "سنة"])
            births = st.number_input("عدد الولادات:", 0)
            mothers_list = st.session_state.herd[st.session_state.herd["الجنس"].isin(["أنثى", "أنثى صغيرة"])]["القلادة"].tolist()
            mother_sel = st.selectbox("الأم (اختياري):", ["لا يوجد"] + mothers_list)
            img_file = st.file_uploader("صورة الغنمة", type=['jpg', 'png'])
            
            if st.form_submit_button("إضافة"):
                img_path = save_image(img_file)
                if mother_sel != "لا يوجد":
                    m_idx = st.session_state.herd[st.session_state.herd["القلادة"] == mother_sel].index[0]
                    current_kids = ast.literal_eval(st.session_state.herd.at[m_idx, "الأبناء"])
                    current_kids.append(collar)
                    st.session_state.herd.at[m_idx, "الأبناء"] = str(current_kids)
                
                new_row = pd.DataFrame([{"ID": str(datetime.now().timestamp()), "القلادة": collar, "الجنس": gender, "العمر": age_val, "وحدة": age_unit, "عدد الولادات": births, "صورة": img_path, "الأم": mother_sel if mother_sel != "لا يوجد" else "", "الأبناء": "[]", "اللقاحات": "[]", "الجرعات": "[]", "آخر تغطيس": ""}])
                st.session_state.herd = pd.concat([st.session_state.herd, new_row], ignore_index=True)
                save_data(st.session_state.herd, DATA_FILE)
                st.rerun()

    if not st.session_state.herd.empty:
        with st.expander("✏️ تعديل / 🗑️ حذف رأس"):
            selected_edit_collar = st.selectbox("اختر الرأس:", st.session_state.herd["القلادة"].tolist())
            sheep_row = st.session_state.herd[st.session_state.herd["القلادة"] == selected_edit_collar].iloc[0]
            idx = st.session_state.herd[st.session_state.herd["القلادة"] == selected_edit_collar].index[0]
            
            with st.form("edit_form"):
                edit_collar = st.text_input("القلادة", value=sheep_row["القلادة"])
                edit_gender = st.selectbox("الجنس", ["أنثى", "ذكر", "أنثى صغيرة", "ذكر صغير"], index=["أنثى", "ذكر", "أنثى صغيرة", "ذكر صغير"].index(sheep_row["الجنس"]))
                edit_age = st.number_input("العمر", value=int(sheep_row.get("العمر", 0)))
                edit_births = st.number_input("عدد الولادات", value=int(sheep_row.get("عدد الولادات", 0)))
                edit_unit = st.selectbox("الوحدة", ["شهر", "سنة"], index=0 if sheep_row.get("وحدة") == "شهر" else 1)
                
                mothers_list = st.session_state.herd[st.session_state.herd["الجنس"].isin(["أنثى", "أنثى صغيرة"]) & (st.session_state.herd["القلادة"] != edit_collar)]["القلادة"].tolist()
                current_m = sheep_row.get("الأم", "لا يوجد")
                edit_mother = st.selectbox("الأم:", ["لا يوجد"] + mothers_list, index=0 if current_m == "لا يوجد" or current_m == "" else (mothers_list.index(current_m) + 1 if current_m in mothers_list else 0))
                
                new_img = st.file_uploader("تحديث الصورة", type=['jpg', 'png'])
                
                if st.form_submit_button("حفظ التعديلات"):
                    old_mother = sheep_row.get("الأم", "")
                    if old_mother != edit_mother:
                        if old_mother in st.session_state.herd["القلادة"].values:
                            m_idx = st.session_state.herd[st.session_state.herd["القلادة"] == old_mother].index[0]
                            kids = ast.literal_eval(st.session_state.herd.at[m_idx, "الأبناء"])
                            if sheep_row["القلادة"] in kids: kids.remove(sheep_row["القلادة"]); st.session_state.herd.at[m_idx, "الأبناء"] = str(kids)
                        if edit_mother != "لا يوجد":
                            m_idx = st.session_state.herd[st.session_state.herd["القلادة"] == edit_mother].index[0]
                            kids = ast.literal_eval(st.session_state.herd.at[m_idx, "الأبناء"])
                            kids.append(sheep_row["القلادة"]); st.session_state.herd.at[m_idx, "الأبناء"] = str(kids)
                    
                    st.session_state.herd.at[idx, "القلادة"] = edit_collar
                    st.session_state.herd.at[idx, "الجنس"] = edit_gender
                    st.session_state.herd.at[idx, "العمر"] = edit_age
                    st.session_state.herd.at[idx, "عدد الولادات"] = edit_births
                    st.session_state.herd.at[idx, "وحدة"] = edit_unit
                    st.session_state.herd.at[idx, "الأم"] = edit_mother if edit_mother != "لا يوجد" else ""
                    if new_img: st.session_state.herd.at[idx, "صورة"] = save_image(new_img)
                    
                    save_data(st.session_state.herd, DATA_FILE)
                    st.rerun()
                    
