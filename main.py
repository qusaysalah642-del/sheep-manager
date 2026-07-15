import streamlit as st
import pandas as pd
import json
import os
import uuid
from datetime import datetime

# ─── إعداد الصفحة ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sheep Manager Pro", layout="wide")

C_PRIMARY = "#2e7d32"
C_BG = "#0d2818"

if not os.path.exists("images"): os.makedirs("images")

st.markdown(f"""
<style>
    .stApp {{ background-color: {C_BG}; color: #e8f5e9; }}
    .stButton > button {{ background-color: {C_PRIMARY}; color: white; border-radius: 8px; width: 100%; }}
    [data-testid="column"] {{ width: 25% !important; flex: 1 1 25% !important; }}
    [data-testid="stMetricValue"] {{ font-size: 16px !important; }}
    [data-testid="stMetricLabel"] {{ font-size: 12px !important; }}
</style>
""", unsafe_allow_html=True)

# ─── إدارة البيانات ────────────────────────────────────────────────────────
DATA_FILE = "herd_data.json"
HISTORY_FILE = "medical_history.json"
REQUIRED_COLS = ["ID", "القلادة", "الجنس", "العمر", "عدد الولادات", "صورة", "اللقاحات", "الجرعات", "آخر تغطيس"]

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
            needs_save = False
            for col in columns:
                if col not in df.columns:
                    df[col] = "[]" if col in ["اللقاحات", "الجرعات"] else ""
                    needs_save = True
            if needs_save:
                df.to_json(file, orient="records", force_ascii=False, indent=4)
            return df
    except: return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_json(file, orient="records", force_ascii=False, indent=4)

if "herd" not in st.session_state: 
    st.session_state.herd = load_data(DATA_FILE, REQUIRED_COLS)
if "history" not in st.session_state: 
    st.session_state.history = load_data(HISTORY_FILE, ["التاريخ", "الإجراء", "العلاج", "الأغنام", "صورة"])

# ─── واجهة التطبيق ─────────────────────────────────────────────────────────
st.title("🐑 Sheep Manager Pro")
tab1, tab2, tab3, tab4 = st.tabs(["🏠 القطيع", "💉 إجراء", "📋 السجل", "➕ إدارة"])

with tab1:
    st.subheader("القطيع")
    df = st.session_state.herd
    if not df.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("الكل", len(df))
        c2.metric("ذكور", len(df[df["الجنس"].isin(["ذكر", "ذكر صغير"])]))
        c3.metric("إناث", len(df[df["الجنس"].isin(["أنثى", "أنثى صغيرة"])]))
        c4.metric("صغار", len(df[df["الجنس"].str.contains("صغير", na=False)]))
    else:
        st.write("القطيع فارغ حالياً، أضف رؤوساً جديدة من تبويب (➕ إدارة).")
    
    st.divider()
    if not df.empty:
        filter_type = st.selectbox("فرز:", ["الكل", "ذكر", "أنثى", "ذكر صغير", "أنثى صغيرة"])
        view_df = df if filter_type == "الكل" else df[df["الجنس"] == filter_type]
        for idx, row in view_df.iterrows():
            with st.expander(f"🏷️ {row['القلادة']}"):
                if row.get('صورة') and os.path.exists(row['صورة']): 
                    st.image(row['صورة'], width=150)
                st.write(f"الجنس: {row.get('الجنس', 'غير معروف')} | العمر: {row.get('العمر', 0)} شهر | الولادات: {row.get('عدد الولادات', 0)}")

with tab2:
    st.subheader("إجراء طبي")
    if not st.session_state.herd.empty:
        selected_collars = st.multiselect("اختر الأغنام:", st.session_state.herd["القلادة"].tolist())
        action_type = st.radio("نوع الإجراء:", ["تطعيم", "جرعة طفيلية", "تغطيس"], horizontal=True)
        tr_opts = ['إيفومك', 'معوي/دموي', 'طاعون', 'جدري', 'حمى قلاعية'] if action_type == "تطعيم" else (['جرعة كبدية', 'جرعة معوية'] if action_type == "جرعة طفيلية" else ['تغطيس شامل'])
        treatment = st.selectbox("العلاج:", tr_opts)
        date = str(st.date_input("التاريخ:"))
        img_file = st.file_uploader("صورة الإجراء (اختياري)", type=['jpg', 'png'])
        if st.button("حفظ الإجراء"):
            img_path = save_image(img_file)
            new_hist = pd.DataFrame([{"التاريخ": date, "الإجراء": action_type, "العلاج": treatment, "الأغنام": ", ".join(selected_collars), "صورة": img_path}])
            st.session_state.history = pd.concat([st.session_state.history, new_hist], ignore_index=True)
            save_data(st.session_state.history, HISTORY_FILE)
            st.success("تم الحفظ!")
    else:
        st.warning("يجب إضافة أغنام أولاً.")

with tab3:
    st.subheader("📋 السجل الطبي")
    if not st.session_state.history.empty:
        for _, row in st.session_state.history.iterrows():
            st.write(f"**{row['التاريخ']}** - {row['الإجراء']} ({row['العلاج']})")
            if row.get('صورة') and os.path.exists(row['صورة']): st.image(row['صورة'], width=100)
            st.divider()
    else:
        st.write("لا يوجد إجراءات مسجلة بعد.")

with tab4:
    st.subheader("إدارة القطيع")
    
    # ── القسم الأول: إضافة رأس جديد ──
    with st.expander("➕ إضافة رأس جديد للقطيع", expanded=True):
        with st.form("add_form"):
            collar = st.text_input("القلادة")
            gender = st.selectbox("الجنس", ["أنثى", "ذكر", "أنثى صغيرة", "ذكر صغير"])
            age_unit = st.radio("وحدة العمر عند الإضافة:", ["أشهر", "سنوات"], horizontal=True)
            age_val = st.number_input("قيمة العمر:", 0)
            actual_age = age_val * 12 if age_unit == "سنوات" else age_val
            births = st.number_input("الولادات", 0)
            img_file = st.file_uploader("صورة الغنمة", type=['jpg', 'png'])
            if st.form_submit_button("إضافة"):
                img_path = save_image(img_file)
                new_row = pd.DataFrame([{
                    "ID": str(datetime.now().timestamp()), "القلادة": collar, "الجنس": gender, 
                    "العمر": actual_age, "عدد الولادات": births, "صورة": img_path,
                    "اللقاحات": "[]", "الجرعات": "[]", "آخر تغطيس": ""
                }])
                st.session_state.herd = pd.concat([st.session_state.herd, new_row], ignore_index=True)
                save_data(st.session_state.herd, DATA_FILE)
                st.success("تمت الإضافة بنجاح!")
                st.rerun()

    # ── القسم الثاني: تعديل بيانات رأس موجود ──
    if not st.session_state.herd.empty:
        with st.expander("✏️ تعديل بيانات رأس موجود"):
            selected_edit_collar = st.selectbox("اختر القلادة المراد تعديلها:", st.session_state.herd["القلادة"].tolist(), key="edit_select")
            
            # جلب البيانات الحالية للرأس المختار
            sheep_row = st.session_state.herd[st.session_state.herd["القلادة"] == selected_edit_collar].iloc[0]
            
            with st.form("edit_form"):
                edit_collar = st.text_input("القلادة الجديدة", value=sheep_row["القلادة"])
                genders = ["أنثى", "ذكر", "أنثى صغيرة", "ذكر صغير"]
                gender_idx = genders.index(sheep_row["الجنس"]) if sheep_row["الجنس"] in genders else 0
                edit_gender = st.selectbox("الجنس", genders, index=gender_idx)
                
                edit_age_unit = st.radio("وحدة العمر الجديدة:", ["أشهر", "سنوات"], horizontal=True)
                # عرض العمر الحالي في الإدخال
                current_age = int(sheep_row["العمر"])
                edit_age_val = st.number_input("قيمة العمر الجديدة:", value=current_age)
                
                edit_births = st.number_input("عدد الولادات الحالي", value=int(sheep_row["عدد الولادات"]))
                edit_img_file = st.file_uploader("تحديث الصورة (اختياري)", type=['jpg', 'png'])
                
                if st.form_submit_button("حفظ التعديلات"):
                    actual_age = edit_age_val * 12 if edit_age_unit == "سنوات" else edit_age_val
                    
                    # معالجة الصورة: إذا لم يرفع صورة جديدة، نحتفظ بالقديمة
                    img_path = sheep_row["صورة"]
                    if edit_img_file is not None:
                        img_path = save_image(edit_img_file)
                    
                    # تحديث السطر في قاعدة البيانات
                    idx = st.session_state.herd[st.session_state.herd["القلادة"] == selected_edit_collar].index[0]
                    st.session_state.herd.at[idx, "القلادة"] = edit_collar
                    st.session_state.herd.at[idx, "الجنس"] = edit_gender
                    st.session_state.herd.at[idx, "العمر"] = actual_age
                    st.session_state.herd.at[idx, "عدد الولادات"] = edit_births
                    st.session_state.herd.at[idx, "صورة"] = img_path
                    
                    save_data(st.session_state.herd, DATA_FILE)
                    st.success("تم تعديل البيانات بنجاح!")
                    st.rerun()

        # ── القسم الثالث: حذف رأس من القطيع ──
        with st.expander("🗑️ حذف رأس من القطيع"):
            selected_del_collar = st.selectbox("اختر القلادة التي تريد حذفها نهائياً:", st.session_state.herd["القلادة"].tolist(), key="del_select")
            if st.button("تأكيد الحذف النهائي ⚠️", type="primary"):
                st.session_state.herd = st.session_state.herd[st.session_state.herd["القلادة"] != selected_del_collar]
                save_data(st.session_state.herd, DATA_FILE)
                st.success(f"تم حذف الرأس ذو القلادة '{selected_del_collar}' بنجاح!")
                st.rerun()
                
