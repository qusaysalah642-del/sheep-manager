import streamlit as st
import pandas as pd
import json
import os
import uuid
import ast
from datetime import datetime

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
    [data-testid="stMetricValue"] {{ font-size: 18px !important; color: #a5d6a7 !important; }}
    [data-testid="stMetricLabel"] {{ font-size: 14px !important; color: #c8e6c9 !important; }}
</style>
""", unsafe_allow_html=True)

# ─── إدارة البيانات ────────────────────────────────────────────────────────
DATA_FILE = "herd_data.json"
HISTORY_FILE = "medical_history.json"
REQUIRED_COLS = ["ID", "القلادة", "الجنس", "العمر", "وحدة", "عدد الولادات", "صورة", "اللقاحات", "الجرعات", "آخر تغطيس", "الأم", "الأبناء"]
HISTORY_COLS = ["ID", "التاريخ", "الإجراء", "العلاج", "الأغنام", "صورة"]


def save_image(uploaded_file):
    """يحفظ صورة مرفوعة ويرجع مسارها، أو نص فارغ إذا لا توجد صورة."""
    if uploaded_file is not None:
        file_path = f"images/{uuid.uuid4()}.jpg"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return ""


def safe_delete_image(path):
    """يحذف ملف صورة بأمان إذا كان موجوداً، مع تجاهل أي خطأ بدون كسر التطبيق."""
    if path and isinstance(path, str) and os.path.exists(path):
        try:
            os.remove(path)
        except OSError as e:
            st.warning(f"⚠️ تعذر حذف ملف الصورة: {e}")


def safe_literal_eval(value, default=None):
    """يحلل نصاً يمثل قائمة بايثون بأمان، ويرجع قيمة افتراضية لو فشل التحليل."""
    if default is None:
        default = []
    try:
        result = ast.literal_eval(value)
        return result if isinstance(result, list) else default
    except (ValueError, SyntaxError, TypeError):
        return default


def load_data(file, columns):
    if not os.path.exists(file):
        return pd.DataFrame(columns=columns)
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        for col in columns:
            if col not in df.columns:
                if col == "الأبناء":
                    df[col] = "[]"
                elif col == "الأم":
                    df[col] = ""
                elif col == "وحدة":
                    df[col] = "شهر"
                elif col in ["اللقاحات", "الجرعات"]:
                    df[col] = "[]"
                else:
                    df[col] = ""
        return df
    except (json.JSONDecodeError, ValueError, OSError) as e:
        st.error(f"⚠️ تعذرت قراءة ملف البيانات ({file}): {e}. تم تحميل قاعدة بيانات فارغة لتفادي فقدان البيانات الحالية على القرص.")
        return pd.DataFrame(columns=columns)


def save_data(df, file):
    try:
        df.to_json(file, orient="records", force_ascii=False, indent=4)
    except OSError as e:
        st.error(f"⚠️ فشل حفظ البيانات في {file}: {e}")


if "herd" not in st.session_state:
    st.session_state.herd = load_data(DATA_FILE, REQUIRED_COLS)
if "history" not in st.session_state:
    st.session_state.history = load_data(HISTORY_FILE, HISTORY_COLS)


# ─── دوال مساعدة للعلاقات (الأم/الأبناء) والعرض ─────────────────────────────
def get_collar_by_id(sheep_id):
    """يرجع القلادة الحالية لرأس معيّن حسب الـ ID، أو تنويه لو الرأس محذوف."""
    if not sheep_id:
        return ""
    row = st.session_state.herd[st.session_state.herd["ID"] == sheep_id]
    if row.empty:
        return "(محذوف)"
    return row.iloc[0]["القلادة"]


def format_sheep_label(sheep_id):
    """يبني تسمية عرض فريدة تجمع القلادة مع جزء من المعرف لتفادي التشابه بين الرؤوس."""
    row = st.session_state.herd[st.session_state.herd["ID"] == sheep_id]
    if row.empty:
        return sheep_id
    row = row.iloc[0]
    short_id = str(sheep_id)[-4:] if len(str(sheep_id)) >= 4 else str(sheep_id)
    return f"{row['القلادة']} ({row['الجنس']} #{short_id})"


def format_mother_option(m_id):
    return "لا يوجد" if m_id is None else format_sheep_label(m_id)


def add_kid_to_mother(mother_id, kid_id):
    """يضيف معرف الابن إلى قائمة أبناء الأم، إن كانت الأم موجودة."""
    m_rows = st.session_state.herd[st.session_state.herd["ID"] == mother_id]
    if m_rows.empty:
        return
    m_idx = m_rows.index[0]
    kids = safe_literal_eval(st.session_state.herd.at[m_idx, "الأبناء"])
    if kid_id not in kids:
        kids.append(kid_id)
        st.session_state.herd.at[m_idx, "الأبناء"] = str(kids)


def remove_kid_from_mother(mother_id, kid_id):
    """يحذف معرف الابن من قائمة أبناء الأم، إن كانت الأم موجودة."""
    m_rows = st.session_state.herd[st.session_state.herd["ID"] == mother_id]
    if m_rows.empty:
        return
    m_idx = m_rows.index[0]
    kids = safe_literal_eval(st.session_state.herd.at[m_idx, "الأبناء"])
    if kid_id in kids:
        kids.remove(kid_id)
        st.session_state.herd.at[m_idx, "الأبناء"] = str(kids)


# ─── واجهة التطبيق ─────────────────────────────────────────────────────────
st.title("🐑 Sheep Manager Pro")
tab1, tab2, tab3, tab4 = st.tabs(["🏠 القطيع", "💉 إجراء", "📋 السجل", "➕ إدارة"])

with tab1:
    st.subheader("📊 إحصائيات القطيع")
    df = st.session_state.herd

    if not df.empty:
        total = len(df)
        males = len(df[df["الجنس"].isin(["ذكر", "ذكر صغير"])])
        females = len(df[df["الجنس"].isin(["أنثى", "أنثى صغيرة"])])
        young = len(df[df["الجنس"].str.contains("صغير", na=False)])

        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.metric("🐑 العدد الكلي", total)
            with st.container(border=True):
                st.metric("♂️ ذكور", males)
        with col2:
            with st.container(border=True):
                st.metric("♀️ إناث", females)
            with st.container(border=True):
                st.metric("👶 صغار", young)
    else:
        st.info("لا توجد أغنام مسجلة بعد. أضف رأساً جديداً من تبويب «إدارة».")

    st.divider()

    if not df.empty:
        for idx, row in df.iterrows():
            kids_ids = safe_literal_eval(row.get('الأبناء', '[]'))

            with st.expander(f"🏷️ {row['القلادة']}"):
                col_img, col_info = st.columns([1, 2])
                with col_img:
                    if row.get('صورة') and os.path.exists(row['صورة']):
                        st.image(row['صورة'], use_container_width=True)
                with col_info:
                    unit = row.get("وحدة", "شهر")
                    st.write(f"**الجنس:** {row.get('الجنس', 'غير معروف')}")
                    st.write(f"**العمر:** {row.get('العمر', 0)} {unit}")
                    st.write(f"**الولادات:** {row.get('عدد الولادات', 0)}")
                    if row.get('الأم'):
                        st.write(f"**الأم:** {get_collar_by_id(row['الأم'])}")
                    if kids_ids:
                        st.write("**الأبناء:**")
                        for i, kid_id in enumerate(kids_ids, 1):
                            st.write(f"{i}. {get_collar_by_id(kid_id)}")

with tab2:
    st.subheader("💉 إجراء طبي")
    if not st.session_state.herd.empty:
        herd_ids = st.session_state.herd["ID"].tolist()
        selected_ids = st.multiselect(
            "اختر الأغنام:", herd_ids, format_func=format_sheep_label
        )
        action_type = st.radio("نوع الإجراء:", ["تطعيم", "جرعة طفيلية", "تغطيس"], horizontal=True)
        tr_opts = (
            ['إيفومك', 'معوي/دموي', 'طاعون', 'جدري', 'حمى قلاعية'] if action_type == "تطعيم"
            else (['جرعة كبدية', 'جرعة معوية'] if action_type == "جرعة طفيلية" else ['تغطيس شامل'])
        )
        treatment = st.selectbox("العلاج:", tr_opts)
        date = str(st.date_input("التاريخ:"))
        img_file = st.file_uploader("صورة التوثيق (اختياري)", type=['jpg', 'png'])
        if st.button("حفظ الإجراء"):
            if not selected_ids:
                st.warning("⚠️ الرجاء اختيار رأس واحد على الأقل قبل الحفظ.")
            else:
                selected_collars = [get_collar_by_id(sid) for sid in selected_ids]
                img_path = save_image(img_file)
                new_hist = pd.DataFrame([{
                    "ID": str(uuid.uuid4()),
                    "التاريخ": date,
                    "الإجراء": action_type,
                    "العلاج": treatment,
                    "الأغنام": ", ".join(selected_collars),
                    "صورة": img_path
                }])
                st.session_state.history = pd.concat([st.session_state.history, new_hist], ignore_index=True)
                save_data(st.session_state.history, HISTORY_FILE)
                st.session_state.toast = "تمت إضافة الإجراء بنجاح! ✅"
                st.rerun()
    else:
        st.warning("يجب إضافة أغنام أولاً.")

with tab3:
    st.subheader("📋 السجل الطبي")
    if not st.session_state.history.empty:
        for idx, row in st.session_state.history.iterrows():
            with st.expander(f"🗓️ {row['التاريخ']} - {row['الإجراء']} ({row['العلاج']})"):
                if row.get('صورة') and os.path.exists(row['صورة']):
                    st.image(row['صورة'], width=100)

                action_opts = ["تطعيم", "جرعة طفيلية", "تغطيس"]
                curr_action = row['الإجراء']
                act_idx = action_opts.index(curr_action) if curr_action in action_opts else 0
                selected_action = st.selectbox("الإجراء", action_opts, index=act_idx, key=f"a_{idx}")

                if selected_action == "تطعيم":
                    tr_opts = ['إيفومك', 'معوي/دموي', 'طاعون', 'جدري', 'حمى قلاعية']
                elif selected_action == "جرعة طفيلية":
                    tr_opts = ['جرعة كبدية', 'جرعة معوية']
                else:
                    tr_opts = ['تغطيس شامل']

                with st.form(f"edit_hist_{idx}"):
                    new_date = st.date_input("التاريخ", value=pd.to_datetime(row['التاريخ']), key=f"d_{idx}")

                    curr_treat = row['العلاج']
                    tr_idx = tr_opts.index(curr_treat) if curr_treat in tr_opts else 0
                    new_treat = st.selectbox("العلاج", tr_opts, index=tr_idx, key=f"t_{idx}")

                    remove_hist_img = False
                    current_hist_img = row.get('صورة', "")
                    if current_hist_img and os.path.exists(current_hist_img):
                        remove_hist_img = st.checkbox("🗑️ حذف الصورة الحالية", key=f"rm_img_h_{idx}")

                    new_img = st.file_uploader("تحديث صورة التوثيق", type=['jpg', 'png'], key=f"img_h_{idx}")

                    if st.form_submit_button("حفظ التعديلات"):
                        st.session_state.history.at[idx, "التاريخ"] = str(new_date)
                        st.session_state.history.at[idx, "الإجراء"] = selected_action
                        st.session_state.history.at[idx, "العلاج"] = new_treat

                        if remove_hist_img:
                            safe_delete_image(current_hist_img)
                            st.session_state.history.at[idx, "صورة"] = ""
                        elif new_img:
                            safe_delete_image(current_hist_img)
                            st.session_state.history.at[idx, "صورة"] = save_image(new_img)

                        save_data(st.session_state.history, HISTORY_FILE)
                        st.session_state.toast = "تم التعديل بنجاح! 📝"
                        st.rerun()

                if st.button("🗑️ حذف السجل", key=f"del_{idx}"):
                    safe_delete_image(row.get('صورة', ""))
                    st.session_state.history = st.session_state.history.drop(idx).reset_index(drop=True)
                    save_data(st.session_state.history, HISTORY_FILE)
                    st.session_state.toast = "تم الحذف بنجاح! 🗑️"
                    st.rerun()
    else:
        st.write("لا يوجد إجراءات مسجلة بعد.")

with tab4:
    st.subheader("➕ إدارة القطيع")
    with st.expander("➕ إضافة رأس جديد", expanded=True):
        with st.form("add_form"):
            collar = st.text_input("القلادة")
            gender = st.selectbox("الجنس", ["أنثى", "ذكر", "أنثى صغيرة", "ذكر صغير"])
            age_unit = st.radio("وحدة العمر:", ["شهر", "سنة"], horizontal=True)
            age_val = st.number_input("قيمة العمر:", min_value=0, step=1)
            births = st.number_input("الولادات", min_value=0, step=1)

            mother_options = [None] + st.session_state.herd[
                st.session_state.herd["الجنس"].isin(["أنثى", "أنثى صغيرة"])
            ]["ID"].tolist()
            mother_sel = st.selectbox("الأم (اختياري)", mother_options, format_func=format_mother_option)

            img_file = st.file_uploader("صورة الغنمة", type=['jpg', 'png'])
            submitted = st.form_submit_button("إضافة")
            if submitted:
                collar_clean = collar.strip()
                if not collar_clean:
                    st.error("⚠️ يجب إدخال رقم/اسم القلادة.")
                elif collar_clean in st.session_state.herd["القلادة"].values:
                    st.error(f"⚠️ يوجد رأس آخر بنفس القلادة «{collar_clean}» بالفعل. الرجاء استخدام قلادة مختلفة لتفادي الالتباس.")
                else:
                    new_id = str(uuid.uuid4())
                    img_path = save_image(img_file)
                    new_row = pd.DataFrame([{
                        "ID": new_id, "القلادة": collar_clean, "الجنس": gender,
                        "العمر": age_val, "وحدة": age_unit, "عدد الولادات": births, "صورة": img_path,
                        "اللقاحات": "[]", "الجرعات": "[]", "آخر تغطيس": "",
                        "الأم": mother_sel if mother_sel else "", "الأبناء": "[]"
                    }])
                    st.session_state.herd = pd.concat([st.session_state.herd, new_row], ignore_index=True)
                    if mother_sel:
                        add_kid_to_mother(mother_sel, new_id)
                    save_data(st.session_state.herd, DATA_FILE)
                    st.session_state.toast = "تمت الإضافة بنجاح! ✅"
                    st.rerun()

    if not st.session_state.herd.empty:
        with st.expander("✏️ تعديل / 🗑️ حذف رأس"):
            herd_ids = st.session_state.herd["ID"].tolist()
            selected_edit_id = st.selectbox(
                "اختر الرأس:", herd_ids, format_func=format_sheep_label, key="edit_select"
            )
            sheep_row = st.session_state.herd[st.session_state.herd["ID"] == selected_edit_id].iloc[0]
            idx = st.session_state.herd[st.session_state.herd["ID"] == selected_edit_id].index[0]

            with st.form("edit_form"):
                edit_collar = st.text_input("القلادة", value=sheep_row["القلادة"])

                genders = ["أنثى", "ذكر", "أنثى صغيرة", "ذكر صغير"]
                current_g = sheep_row.get("الجنس", "أنثى")
                gender_idx = genders.index(current_g) if current_g in genders else 0
                edit_gender = st.selectbox("الجنس", genders, index=gender_idx)

                edit_age = st.number_input("العمر", min_value=0, step=1, value=int(sheep_row["العمر"]))
                edit_births = st.number_input("عدد الولادات", min_value=0, step=1, value=int(sheep_row["عدد الولادات"]))
                edit_unit = st.selectbox("الوحدة", ["شهر", "سنة"], index=0 if sheep_row.get("وحدة", "شهر") == "شهر" else 1)

                mother_options = [None] + st.session_state.herd[
                    st.session_state.herd["الجنس"].isin(["أنثى", "أنثى صغيرة"])
                    & (st.session_state.herd["ID"] != selected_edit_id)
                ]["ID"].tolist()
                old_mother_id = sheep_row.get("الأم", "") or None
                mother_idx = mother_options.index(old_mother_id) if old_mother_id in mother_options else 0
                edit_mother_sel = st.selectbox("الأم", mother_options, index=mother_idx, format_func=format_mother_option)

                current_img = sheep_row.get("صورة", "")
                remove_img = False
                if current_img and os.path.exists(current_img):
                    st.image(current_img, width=100)
                    remove_img = st.checkbox("🗑️ حذف الصورة الحالية")

                new_img = st.file_uploader("تحديث الصورة (اختياري)", type=['jpg', 'png'])

                if st.form_submit_button("حفظ التعديلات"):
                    edit_collar_clean = edit_collar.strip()
                    duplicate = (
                        (st.session_state.herd["القلادة"] == edit_collar_clean)
                        & (st.session_state.herd["ID"] != selected_edit_id)
                    ).any()
                    if not edit_collar_clean:
                        st.error("⚠️ يجب إدخال رقم/اسم القلادة.")
                    elif duplicate:
                        st.error(f"⚠️ يوجد رأس آخر بنفس القلادة «{edit_collar_clean}» بالفعل.")
                    else:
                        if old_mother_id != edit_mother_sel:
                            if old_mother_id:
                                remove_kid_from_mother(old_mother_id, selected_edit_id)
                            if edit_mother_sel:
                                add_kid_to_mother(edit_mother_sel, selected_edit_id)

                        st.session_state.herd.at[idx, "القلادة"] = edit_collar_clean
                        st.session_state.herd.at[idx, "الجنس"] = edit_gender
                        st.session_state.herd.at[idx, "العمر"] = edit_age
                        st.session_state.herd.at[idx, "عدد الولادات"] = edit_births
                        st.session_state.herd.at[idx, "وحدة"] = edit_unit
                        st.session_state.herd.at[idx, "الأم"] = edit_mother_sel if edit_mother_sel else ""

                        if remove_img:
                            safe_delete_image(current_img)
                            st.session_state.herd.at[idx, "صورة"] = ""
                        elif new_img:
                            safe_delete_image(current_img)
                            st.session_state.herd.at[idx, "صورة"] = save_image(new_img)

                        save_data(st.session_state.herd, DATA_FILE)
                        st.session_state.toast = "تم التعديل بنجاح! 📝"
                        st.rerun()

            if st.button("حذف الرأس نهائياً ⚠️", type="primary"):
                # نستخدم بيانات sheep_row الأصلية (المحفوظة فعلياً) وليس أي تعديل غير محفوظ بالفورم
                original_mother_id = sheep_row.get("الأم", "")
                if original_mother_id:
                    remove_kid_from_mother(original_mother_id, selected_edit_id)

                img_to_del = st.session_state.herd.at[idx, "صورة"]
                safe_delete_image(img_to_del)

                st.session_state.herd = st.session_state.herd.drop(idx).reset_index(drop=True)
                save_data(st.session_state.herd, DATA_FILE)
                st.session_state.toast = "تم الحذف بنجاح! 🗑️"
                st.rerun()
                
