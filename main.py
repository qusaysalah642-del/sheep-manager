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

    .app-hero {{
        display: flex; align-items: center; gap: 18px;
        background: linear-gradient(135deg, {C_BG_PANEL} 0%, {C_BG_DEEP} 100%);
        border: 1px solid {C_BORDER};
        border-radius: 18px;
        padding: 22px 28px;
        margin-bottom: 22px;
        box-shadow: 0 6px 24px rgba(0,0,0,0.25);
    }}
    .app-hero-icon {{
        font-size: 40px; line-height: 1;
        background: linear-gradient(135deg, {C_AMBER}, {C_AMBER_DARK});
        width: 64px; height: 64px; border-radius: 16px;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0;
        box-shadow: 0 4px 14px rgba(211,161,92,0.25);
    }}
    .app-hero-title {{ font-size: 26px; font-weight: 800; margin: 0; color: {C_TEXT}; }}
    .app-hero-subtitle {{ font-size: 14px; color: {C_TEXT_MUTED}; margin-top: 2px; }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; background: transparent; }}
    .stTabs [data-baseweb="tab"] {{
        background: {C_BG_PANEL};
        border: 1px solid {C_BORDER};
        border-radius: 999px !important;
        padding: 8px 20px;
        color: {C_TEXT_MUTED};
        font-weight: 700;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {C_GREEN} 0%, {C_GREEN_DARK} 100%) !important;
        color: white !important;
        border: 1px solid {C_GREEN} !important;
    }}

    [data-testid="stExpander"] {{
        background: {C_BG_PANEL};
        border: 1px solid {C_BORDER} !important;
        border-radius: 14px !important;
        margin-bottom: 10px;
    }}
    [data-testid="stExpander"] summary {{
        font-weight: 700;
        font-size: 15px;
    }}
    [data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 14px !important;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, {C_GREEN} 0%, {C_GREEN_DARK} 100%);
        color: white; border: none; border-radius: 10px; width: 100%;
        font-weight: 700; padding: 10px 0;
        transition: filter 0.15s ease, transform 0.05s ease;
    }}
    .stButton > button:hover {{ filter: brightness(1.12); }}
    .stButton > button:active {{ transform: scale(0.98); }}
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {C_DANGER} 0%, #b8443a 100%);
    }}

    .stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] > div {{
        background: {C_BG_DEEP} !important;
        border: 1px solid {C_BORDER} !important;
        border-radius: 10px !important;
        color: {C_TEXT} !important;
    }}

    [data-testid="stMetric"] {{
        background: {C_BG_PANEL};
        border: 1px solid {C_BORDER};
        border-radius: 14px;
        padding: 10px 6px;
    }}
    [data-testid="stMetricValue"] {{ font-size: 22px !important; color: {C_AMBER} !important; font-weight: 800 !important; }}
    [data-testid="stMetricLabel"] {{ font-size: 13px !important; color: {C_TEXT_MUTED} !important; }}

    .ear-tag {{
        display: inline-flex; align-items: center; gap: 8px;
        background: linear-gradient(135deg, {C_AMBER} 0%, {C_AMBER_DARK} 100%);
        color: #24170a; font-weight: 800; font-size: 13px;
        padding: 5px 14px 5px 10px;
        border-radius: 4px 14px 14px 4px;
        margin: 2px 4px 2px 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    }}
    .ear-tag::before {{
        content: ''; width: 7px; height: 7px; border-radius: 50%;
        background: {C_BG_DEEP}; border: 2px solid rgba(0,0,0,0.2); flex-shrink: 0;
    }}
    .info-chip {{
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(255,255,255,0.05);
        border: 1px solid {C_BORDER};
        color: {C_TEXT};
        padding: 4px 12px; border-radius: 999px; font-size: 13px;
        margin: 2px 4px 2px 0;
    }}
    .chip-row {{ margin-top: 6px; margin-bottom: 4px; }}
    .muted-note {{ color: {C_TEXT_MUTED}; font-size: 13px; }}

    section[data-testid="stSidebar"] {{
        background: {C_BG_PANEL};
        border-left: 1px solid {C_BORDER};
    }}

    hr {{ border-color: {C_BORDER} !important; }}
</style>
""", unsafe_allow_html=True)

# ─── بانر الهيدر ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-hero">
    <div class="app-hero-icon">🐑</div>
    <div>
        <p class="app-hero-title">Sheep Manager Pro</p>
        <p class="app-hero-subtitle">إدارة القطيع، التطعيمات، والسجل الطبي في مكان واحد</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── إدارة البيانات ────────────────────────────────────────────────────────
DATA_FILE = "herd_data.json"
HISTORY_FILE = "medical_history.json"
REQUIRED_COLS = ["ID", "القلادة", "الجنس", "العمر", "وحدة", "عدد الولادات", "صورة", "اللقاحات", "الجرعات", "آخر تغطيس", "الأم", "الأبناء"]
HISTORY_COLS = ["ID", "التاريخ", "الإجراء", "العلاج", "الأغنام", "صورة"]


def save_image(uploaded_file):
    if uploaded_file is not None:
        file_path = f"images/{uuid.uuid4()}.jpg"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return ""


def safe_delete_image(path):
    if path and isinstance(path, str) and os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


def safe_literal_eval(value, default=None):
    if default is None:
        default = []
    try:
        result = ast.literal_eval(value)
        return result if isinstance(result, list) else default
    except:
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
    except:
        return pd.DataFrame(columns=columns)


def save_data(df, file):
    try:
        df.to_json(file, orient="records", force_ascii=False, indent=4)
    except:
        pass


def migrate_relations_to_ids(df):
    if df.empty:
        return df
    id_set = set(df["ID"].astype(str))
    collar_to_id = {}
    for _, r in df.iterrows():
        collar_to_id.setdefault(r["القلادة"], r["ID"])

    def resolve_one(value):
        if not value:
            return ""
        if value in id_set:
            return value
        if value in collar_to_id:
            return collar_to_id[value]
        return ""

    def resolve_list(value):
        kids = safe_literal_eval(value)
        resolved = []
        for k in kids:
            if k in id_set:
                resolved.append(k)
            elif k in collar_to_id:
                resolved.append(collar_to_id[k])
        return str(resolved)

    df["الأم"] = df["الأم"].apply(resolve_one)
    df["الأبناء"] = df["الأبناء"].apply(resolve_list)
    return df


if "herd" not in st.session_state:
    _herd = load_data(DATA_FILE, REQUIRED_COLS)
    _herd = migrate_relations_to_ids(_herd)
    st.session_state.herd = _herd
    save_data(st.session_state.herd, DATA_FILE)
if "history" not in st.session_state:
    st.session_state.history = load_data(HISTORY_FILE, HISTORY_COLS)


# ─── دوال مساعدة ─────────────────────────────────────────────────────────────
def get_collar_by_id(sheep_id):
    if not sheep_id:
        return ""
    row = st.session_state.herd[st.session_state.herd["ID"] == sheep_id]
    if row.empty:
        return "(محذوف)"
    return row.iloc[0]["القلادة"]


def format_sheep_label(sheep_id):
    row = st.session_state.herd[st.session_state.herd["ID"] == sheep_id]
    if row.empty:
        return sheep_id
    row = row.iloc[0]
    short_id = str(sheep_id)[-4:] if len(str(sheep_id)) >= 4 else str(sheep_id)
    return f"{row['القلادة']} ({row['الجنس']} #{short_id})"


def add_kid_to_mother(mother_id, kid_id):
    m_rows = st.session_state.herd[st.session_state.herd["ID"] == mother_id]
    if m_rows.empty:
        return
    m_idx = m_rows.index[0]
    kids = safe_literal_eval(st.session_state.herd.at[m_idx, "الأبناء"])
    if kid_id not in kids:
        kids.append(kid_id)
        st.session_state.herd.at[m_idx, "الأبناء"] = str(kids)


def remove_kid_from_mother(mother_id, kid_id):
    m_rows = st.session_state.herd[st.session_state.herd["ID"] == mother_id]
    if m_rows.empty:
        return
    m_idx = m_rows.index[0]
    kids = safe_literal_eval(st.session_state.herd.at[m_idx, "الأبناء"])
    if kid_id in kids:
        kids.remove(kid_id)
        st.session_state.herd.at[m_idx, "الأبناء"] = str(kids)


# ─── الشريط الجانبي ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🐑 نظرة سريعة")
    _herd_snap = st.session_state.herd
    if not _herd_snap.empty:
        _total = len(_herd_snap)
        _females = len(_herd_snap[_herd_snap["الجنس"].isin(["أنثى", "أنثى صغيرة"])])
        _males = len(_herd_snap[_herd_snap["الجنس"].isin(["ذكر", "ذكر صغير"])])
        st.markdown(f"""
        <div class="info-chip">📦 الإجمالي: <b>{_total}</b></div><br>
        <div class="info-chip">♀️ إناث: <b>{_females}</b></div><br>
        <div class="info-chip">♂️ ذكور: <b>{_males}</b></div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<p class="muted-note">لا توجد بيانات بعد</p>', unsafe_allow_html=True)

    st.divider()
    _hist_snap = st.session_state.history
    st.markdown(f'<p class="muted-note">📋 عدد الإجراءات المسجلة: <b>{len(_hist_snap)}</b></p>', unsafe_allow_html=True)

# ─── التبويبات الرئيسية ────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 القطيع", "💉 إجراء", "📋 السجل", "⚙️ إدارة", "💾 النسخة الاحتياطية"])

# ─── تبويب القطيع ───────────────────────────────────────────────────────────
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
        st.info("لا توجد أغنام مسجلة بعد.")

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
                    gender_icon = "♀️" if "أنثى" in str(row.get('الجنس', '')) else "♂️"
                    st.markdown(f"""
                    <div class="chip-row">
                        <span class="ear-tag">{gender_icon} {row.get('الجنس', 'غير معروف')}</span>
                        <span class="info-chip">🗓️ {row.get('العمر', 0)} {unit}</span>
                        <span class="info-chip">🐑 {row.get('عدد الولادات', 0)} ولادة</span>
                    </div>
                    """, unsafe_allow_html=True)

                    if row.get('الأم'):
                        st.markdown(f'<p class="muted-note">👩 <b>الأم:</b> {get_collar_by_id(row["الأم"])}</p>', unsafe_allow_html=True)
                    if kids_ids:
                        kids_html = "".join(
                            f'<p class="muted-note" style="margin:2px 0;">{i}. {get_collar_by_id(k)}</p>'
                            for i, k in enumerate(kids_ids, 1)
                        )
                        st.markdown(f'<p class="muted-note"><b>👶 الأبناء:</b></p>{kids_html}', unsafe_allow_html=True)

# ─── تبويب إجراء ────────────────────────────────────────────────────────────
with tab2:
    st.subheader("💉 تسجيل إجراء طبي")
    if not st.session_state.herd.empty:
        with st.container(border=True):
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
            if st.button("💾 حفظ الإجراء"):
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

# ─── تبويب السجل ────────────────────────────────────────────────────────────
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

                        if new_img is not None:
                            old_img_path = st.session_state.history.at[idx, "صورة"]
                            safe_delete_image(old_img_path)
                            st.session_state.history.at[idx, "صورة"] = save_image(new_img)

                        save_data(st.session_state.history, HISTORY_FILE)
                        st.session_state.toast = "تم تحديث الإجراء! ✨"
                        st.rerun()
    else:
        st.info("لا يوجد سجل طبي بعد.")

# ─── تبويب الإدارة ─────────────────────────────────────────────────────────
with tab4:
    st.header("⚙️ لوحة الإدارة")
    
    admin_tab1, admin_tab2, admin_tab3 = st.tabs(["➕ إضافة", "✏️ تعديل", "🗑️ حذف"])

    # ─── الإضافة ───
    with admin_tab1:
        st.subheader("➕ إضافة رأس جديد للقطيع")
        
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("رقم القلادة 🏷️", placeholder="مثلاً: 4521")
                gender = st.selectbox("الجنس", ["أنثى", "ذكر", "أنثى صغيرة", "ذكر صغير"])
            with col2:
                age = st.number_input("العمر", min_value=0, step=1)
                unit = st.selectbox("وحدة العمر", ["شهر", "سنة"])
                births = st.number_input("عدد الولادات", min_value=0, step=1, value=0)

            mother_id = st.selectbox(
                "الأم (اختياري)",
                options=[""] + st.session_state.herd["ID"].tolist(),
                format_func=lambda x: "لا يوجد" if x == "" else format_sheep_label(x)
            )

            uploaded_file = st.file_uploader("صورة للرأس", type=['jpg', 'png'])
            
            if st.button("✅ حفظ الرأس الجديد"):
                if not name:
                    st.warning("⚠️ يجب إدخال رقم القلادة.")
                else:
                    new_id = str(uuid.uuid4())
    
