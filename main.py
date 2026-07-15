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
    .stButton > button {{ background-color: {C_PRIMARY}; color: white; border-radius: 8px; width: 100%; }}
    /* تحسين شكل المتركس للجوال */
    [data-testid="stMetricValue"] {{ font-size: 20px !important; }}
</style>
""", unsafe_allow_html=True)

# ─── إدارة البيانات ────────────────────────────────────────────────────────
DATA_FILE = "herd_data.json"
HISTORY_FILE = "medical_history.json"

def load_data(file, columns):
    if not os.path.exists(file): return pd.DataFrame(columns=columns)
    try:
        with open(file, "r", encoding="utf-8") as f:
            return pd.DataFrame(json.load(f))
    except: return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_json(file, orient="records", force_ascii=False, indent=4)

if "herd" not in st.session_state: 
    st.session_state.herd = load_data(DATA_FILE, ["ID", "القلادة", "الجنس", "العمر", "عدد الولادات", "الحالة الصحية", "اللقاحات", "الجرعات", "آخر تغطيس"])
if "history" not in st.session_state: 
    st.session_state.history = load_data(HISTORY_FILE, ["التاريخ", "الإجراء", "العلاج", "الأغنام"])

# ─── واجهة التطبيق ─────────────────────────────────────────────────────────
st.title("🐑 Sheep Manager Pro")
tab1, tab2, tab3, tab4 = st.tabs(["🏠 القطيع", "💉 إجراء", "📋 سجل", "➕ إدارة"])

with tab1:
    st.subheader("لوحة التحكم")
    df = st.session_state.herd
    
    # ── تصميم 2x2 ليناسب شاشة الهاتف ──
    row1_c1, row1_c2 = st.columns(2)
    row1_c1.metric("الكل", len(df))
    row1_c2.metric("ذكور", len(df[df["الجنس"].isin(["ذكر", "ذكر صغير"])]))
    
    row2_c1, row2_c2 = st.columns(2)
    row2_c1.metric("إناث", len(df[df["الجنس"].isin(["أنثى", "أنثى صغيرة"])]))
    row2_c2.metric("صغار", len(df[df["الجنس"].str.contains("صغير", na=False)]))
    
    st.divider()
    
    # ── نموذج التعديل ──
    if "edit_id" in st.session_state and st.session_state.edit_id:
        idx = df[df["ID"] == st.session_state.edit_id].index[0]
        animal = df.loc[idx]
        with st.form("edit_form"):
            new_collar = st.text_input("القلادة", animal["القلادة"])
            options = ["أنثى", "ذكر", "أنثى صغيرة", "ذكر صغير"]
            new_gender = st.selectbox("الجنس", options, index=options.index(animal["الجنس"]) if animal["الجنس"] in options else 0)
            new_age = st.number_input("العمر (أشهر)", value=int(animal["العمر"]))
            new_births = st.number_input("الولادات", value=int(animal["عدد الولادات"]))
            if st.form_submit_button("حفظ التعديلات"):
                st.session_state.herd.at[idx, "القلادة"] = new_collar
                st.session_state.herd.at[idx, "الجنس"] = new_gender
                st.session_state.herd.at[idx, "العمر"] = new_age
                st.session_state.herd.at[idx, "عدد الولادات"] = new_births
                st.session_state.edit_id = None
                save_data(st.session_state.herd, DATA_FILE)
                st.rerun()

    # ── القائمة ──
    filter_type = st.selectbox("فرز حسب:", ["الكل", "ذكر", "أنثى", "ذكر صغير", "أنثى صغيرة"])
    view_df = df if filter_type == "الكل" else df[df["الجنس"] == filter_type]
    
    for idx, row in view_df.iterrows():
        with st.expander(f"🏷️ {row['القلادة']} | {row['الجنس']}"):
            st.write(f"عمر: {row['العمر']} شهر | ولادات: {row['عدد الولادات']}")
            if st.button("تعديل", key=f"edit_{row['ID']}"):
                st.session_state.edit_id = row['ID']
                st.rerun()

with tab2:
    st.subheader("إجراء طبي")
    selected_collars = st.multiselect("اختر الأغنام:", st.session_state.herd["القلادة"].tolist())
    action_type = st.radio("نوع الإجراء:", ["تطعيم", "جرعة طفيلية", "تغطيس"])
    tr_opts = ['إيفومك', 'معوي/دموي', 'طاعون', 'جدري', 'حمى قلاعية'] if action_type == "تطعيم" else (['جرعة كبدية', 'جرعة معوية'] if action_type == "جرعة طفيلية" else ['تغطيس شامل'])
    treatment = st.selectbox("العلاج:", tr_opts)
    date = str(st.date_input("التاريخ:"))
    
    if st.button("حفظ الإجراء"):
        for collar in selected_collars:
            idx = st.session_state.herd[st.session_state.herd["القلادة"] == collar].index[0]
            if action_type == "تغطيس": st.session_state.herd.at[idx, "آخر تغطيس"] = date
            else: 
                col = "اللقاحات" if action_type == "تطعيم" else "الجرعات"
                val = json.loads(st.session_state.herd.at[idx, col]) if isinstance(st.session_state.herd.at[idx, col], str) and st.session_state.herd.at[idx, col] else []
                if treatment not in val: val.append(treatment)
                st.session_state.herd.at[idx, col] = json.dumps(val)
        
        new_hist = pd.DataFrame([{"التاريخ": date, "الإجراء": action_type, "العلاج": treatment, "الأغنام": ", ".join(selected_collars)}])
        st.session_state.history = pd.concat([st.session_state.history, new_hist], ignore_index=True)
        save_data(st.session_state.herd, DATA_FILE)
        save_data(st.session_state.history, HISTORY_FILE)
        st.success("تم الحفظ!")

with tab3:
    st.subheader("📋 السجل الطبي")
    if not st.session_state.history.empty:
        st.dataframe(st.session_state.history.sort_values(by="التاريخ", ascending=False), use_container_width=True)
    else:
        st.write("لا يوجد بيانات.")

with tab4:
    st.subheader("إضافة رأس جديد")
    with st.form("add_form"):
        collar = st.text_input("القلادة")
        gender = st.selectbox("الجنس", ["أنثى", "ذكر", "أنثى صغيرة", "ذكر صغير"])
        age = st.number_input("العمر (أشهر)", 0)
        births = st.number_input("الولادات", 0)
        if st.form_submit_button("إضافة"):
            new_row = pd.DataFrame([{"ID": str(datetime.now().timestamp()), "القلادة": collar, "الجنس": gender, "العمر": age, "عدد الولادات": births, "الحالة الصحية": "سليم", "اللقاحات": "[]", "الجرعات": "[]", "آخر تغطيس": ""}])
            st.session_state.herd = pd.concat([st.session_state.herd, new_row], ignore_index=True)
            save_data(st.session_state.herd, DATA_FILE)
            st.rerun()
    st.divider()
    del_collar = st.selectbox("حذف رأس:", st.session_state.herd["القلادة"].tolist())
    if st.button("تأكيد الحذف"):
        st.session_state.herd = st.session_state.herd[st.session_state.herd["القلادة"] != del_collar]
        save_data(st.session_state.herd, DATA_FILE)
        st.rerun()
        
