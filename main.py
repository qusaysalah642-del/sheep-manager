import streamlit as st
import pandas as pd
import json
import os
import uuid
import ast
from datetime import datetime

# ─── إعداد الصفحة ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sheep Manager Pro", page_icon="🐑", layout="wide")

# نظام الألوان والخطوط (Design tokens)
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

    html, body, [class*="css"] {{ font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }}
    h1, h2, h3, .app-hero-title {{ font-family: 'Cairo', sans-serif; }}

    .stApp {{ background: linear-gradient(180deg, {C_BG_DEEP} 0%, #0e2a1e 100%); color: {C_TEXT}; }}

    /* ─── الهيدر الرئيسي ─── */
    .app-hero {{
        display: flex; align-items: center; gap: 18px;
        background: linear-gradient(135deg, {C_BG_PANEL} 0%, {C_BG_DEEP} 100%);
        border: 1px solid {C_BORDER}; border-radius: 18px;
        padding: 22px 28px; margin-bottom: 22px;
        box-shadow: 0 6px 24px rgba(0,0,0,0.25);
    }}
    .app-hero-icon {{
        font-size: 40px; line-height: 1;
        background: linear-gradient(135deg, {C_AMBER}, {C_AMBER_DARK});
        width: 64px; height: 64px; border-radius: 16px;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0; box-shadow: 0 4px 14px rgba(211,161,92,0.25);
    }}
    .app-hero-title {{ font-size: 26px; font-weight: 800; margin: 0; color: {C_TEXT}; }}
    .app-hero-subtitle {{ font-size: 14px; color: {C_TEXT_MUTED}; margin-top: 2px; }}

    /* ─── تبويبات علوية ─── */
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; background: transparent; justify-content: center; }}
    .stTabs [data-baseweb="tab"] {{
        background: {C_BG_PANEL}; border: 1px solid {C_BORDER};
        border-radius: 999px !important; padding: 8px 20px;
        color: {C_TEXT_MUTED}; font-weight: 700;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {C_GREEN} 0%, {C_GREEN_DARK} 100%) !important;
        color: white !important; border: 1px solid {C_GREEN} !important;
    }}

    /* ─── البطاقات ─── */
    [data-testid="stExpander"], [data-testid="stVerticalBlockBorderWrapper"] {{
        background: {C_BG_PANEL} !important;
        border: 1px solid {C_BORDER} !important;
        border-radius: 14px !important; margin-bottom: 10px;
    }}
    
    /* ─── الأزرار ─── */
    .stButton > button {{
        background: linear-gradient(135deg, {C_GREEN} 0%, {C_GREEN_DARK} 100%);
        color: white; border: none; border-radius: 10px; width: 100%;
        font-weight: 700; padding: 10px 0; transition: all 0.2s ease;
    }}
    .stButton > button:hover {{ filter: brightness(1.12); transform: translateY(-1px); }}
    
    .btn-danger > button, .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {C_DANGER} 0%, #b8443a 100%) !important;
        color: white !important;
    }}
    .stFormSubmitButton > button {{
        background: linear-gradient(135deg, {C_AMBER} 0%, {C_AMBER_DARK} 100%) !important;
        color: #24170a !important; border: none; border-radius: 10px; font-weight: 800;
    }}

    /* ─── الحقول والمدخلات ─── */
    .stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] > div {{
        background: {C_BG_DEEP} !important; border: 1px solid {C_BORDER} !important;
        border-radius: 10px !important; color: {C_TEXT} !important;
    }}

    /* ─── المقاييس ─── */
    [data-testid="stMetric"] {{
        background: {C_BG_PANEL}; border: 1px solid {C_BORDER};
        border-radius: 14px; padding: 15px; text-align: center;
    }}
    [data-testid="stMetricValue"] {{ font-size: 26px !important; color: {C_AMBER} !important; font-weight: 800 !important; }}
    [data-testid="stMetricLabel"] {{ font-size: 15px !important; color: {C_TEXT_MUTED} !important; }}

    /* ─── شارات المعلومات ─── */
    .ear-tag {{
        display: inline-flex; align-items: center; gap: 8px;
        background: linear-gradient(135deg, {C_AMBER} 0%, {C_AMBER_DARK} 100%);
        color: #24170a; font-weight: 800; font-size: 13px;
        padding: 5px 14px 5px 10px; border-radius: 4px 14px 14px 4px;
        margin: 2px 4px 2px 0; box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    }}
    .ear-tag::before {{
        content: ''; width: 7px; height: 7px; border-radius: 50%;
        background: {C_BG_DEEP}; border: 2px solid rgba(0,0,0,0.2); flex-shrink: 0;
    }}
    .info-chip {{
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(255,255,255,0.05); border: 1px solid {C_BORDER};
        color: {C_TEXT}; padding: 4px 12px; border-radius: 999px; font-size: 13px;
        margin: 2px 4px 2px 0;
    }}
    .muted-note {{ color: {C_TEXT_MUTED}; font-size: 13px; }}
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
        try: os.remove(path)
        except OSError: pass

def safe_literal_eval(value, default=None):
    if default is None: default = []
    try:
        result = ast.literal_eval(value)
        return result if isinstance(result, list) else default
    except (ValueError, SyntaxError, TypeError): return default

def load_data(file, columns):
    if not os.path.exists(file): return pd.DataFrame(columns=columns)
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        for col in columns:
            if col not in df.columns:
                if col in ["الأبناء", "اللقاحات", "الجرعات"]: df[col] = "[]"
                elif col == "وحدة": df[col] = "شهر"
                else: df[col] = ""
        return df
    except Exception as e:
        return pd.DataFrame(columns=columns)

def save_data(df, file):
    try: df.to_json(file, orient="records", force_ascii=False, indent=4)
    except Exception as e: st.error(f"⚠️ فشل حفظ البيانات: {e}")

def migrate_relations_to_ids(df):
    if df.empty: return df
    id_set = set(df["ID"].astype(str))
    collar_to_id = {r["القلادة"]: r["ID"] for _, r in df.iterrows()}
    def resolve_one(value):
        if not value: return ""
        return value if value in id_set else collar_to_id.get(value, "")
    def resolve_list(value):
        kids = safe_literal_eval(value)
        return str([k if k in id_set else collar_to_id.get(k) for k in kids if k in id_set or k in collar_to_id])
    df["الأم"] = df["الأم"].apply(resolve_one)
    df["الأبناء"] = df["الأبناء"].apply(resolve_list)
    return df

if "herd" not in st.session_state:
    st.session_state.herd = migrate_relations_to_ids(load_data(DATA_FILE, REQUIRED_COLS))
    save_data(st.session_state.herd, DATA_FILE)
if "history" not in st.session_state:
    st.session_state.history = load_data(HISTORY_FILE, HISTORY_COLS)

def get_collar_by_id(sheep_id):
    if not sheep_id: return ""
    row = st.session_state.herd[st.session_state.herd["ID"] == sheep_id]
    return row.iloc[0]["القلادة"] if not row.empty else "(محذوف)"

def format_sheep_label(sheep_id):
    row = st.session_state.herd[st.session_state.herd["ID"] == sheep_id]
    if row.empty: return sheep_id
    r = row.iloc[0]
    return f"{r['القلادة']} ({r['الجنس']})"

def add_kid_to_mother(mother_id, kid_id):
    m_rows = st.session_state.herd[st.session_state.herd["ID"] == mother_id]
    if not m_rows.empty:
        idx = m_rows.index[0]
        kids = safe_literal_eval(st.session_state.herd.at[idx, "الأبناء"])
        if kid_id not in kids:
            kids.append(kid_id)
            st.session_state.herd.at[idx, "الأبناء"] = str(kids)

def remove_kid_from_mother(mother_id, kid_id):
    m_rows = st.session_state.herd[st.session_state.herd["ID"] == mother_id]
    if not m_rows.empty:
        idx = m_rows.index[0]
        kids = safe_literal_eval(st.session_state.herd.at[idx, "الأبناء"])
        if kid_id in kids:
            kids.remove(kid_id)
            st.session_state.herd.at[idx, "الأبناء"] = str(kids)

# ─── الشريط الجانبي ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🐑 نظرة سريعة")
    _herd = st.session_state.herd
    if not _herd.empty:
        st.markdown(f"""
        <div class="info-chip" style="width:100%; margin-bottom:8px;">📦 الإجمالي: <b>{len(_herd)}</b></div>
        <div class="info-chip" style="width:100%; margin-bottom:8px;">♀️ إناث: <b>{len(_herd[_herd["الجنس"].isin(["أنثى", "أنثى صغيرة"])])}</b></div>
        <div class="info-chip" style="width:100%;">♂️ ذكور: <b>{len(_herd[_herd["الجنس"].isin(["ذكر", "ذكر صغير"])])}</b></div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<p class="muted-note">لا توجد بيانات بعد</p>', unsafe_allow_html=True)
    st.divider()
    st.markdown(f'<p class="muted-note">📋 الإجراءات المسجلة: <b>{len(st.session_state.history)}</b></p>', unsafe_allow_html=True)

# ─── واجهة التطبيق ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 القطيع", "💉 إجراء", "📋 السجل", "➕ إدارة", "⚙️ الإعدادات"])

# --- التبويب الأول: القطيع ---
with tab1:
    st.subheader("📊 إحصائيات القطيع")
    df = st.session_state.herd
    if not df.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🐑 العدد الكلي", len(df))
        c2.metric("♀️ إناث", len(df[df["الجنس"].isin(["أنثى", "أنثى صغيرة"])]))
        c3.metric("♂️ ذكور", len(df[df["الجنس"].isin(["ذكر", "ذكر صغير"])]))
        c4.metric("👶 صغار", len(df[df["الجنس"].str.contains("صغير", na=False)]))
        
        st.divider()
        for _, row in df.iterrows():
            kids_ids = safe_literal_eval(row.get('الأبناء', '[]'))
            with st.expander(f"🏷️ قلادة: {row['القلادة']} | {row['الجنس']}"):
                col_img, col_info = st.columns([1, 3])
                with col_img:
                    if row.get('صورة') and os.path.exists(row['صورة']):
                        st.image(row['صورة'], use_container_width=True)
                with col_info:
                    g_icon = "♀️" if "أنثى" in str(row.get('الجنس', '')) else "♂️"
                    st.markdown(f"""
                    <div style="margin-bottom: 10px;">
                        <span class="ear-tag">{g_icon} {row.get('الجنس', 'غير معروف')}</span>
                        <span class="info-chip">🗓️ {row.get('العمر', 0)} {row.get('وحدة', 'شهر')}</span>
                        <span class="info-chip">🐑 {row.get('عدد الولادات', 0)} ولادة</span>
                    </div>
                    """, unsafe_allow_html=True)
                    if row.get('الأم'):
                        st.markdown(f'<p class="muted-note">👩 <b>الأم:</b> {get_collar_by_id(row["الأم"])}</p>', unsafe_allow_html=True)
                    if kids_ids:
                        kids_html = "".join(f'<span class="info-chip">{get_collar_by_id(k)}</span>' for k in kids_ids)
                        st.markdown(f'<p class="muted-note" style="margin-bottom:4px;"><b>👶 الأبناء:</b><br>{kids_html}</p>', unsafe_allow_html=True)
    else:
        st.info("لا توجد أغنام مسجلة بعد. أضف رأساً جديداً من تبويب «إدارة».")

# --- التبويب الثاني: الإجراءات ---
with tab2:
    st.subheader("💉 تسجيل إجراء طبي")
    if not st.session_state.herd.empty:
        with st.container(border=True):
            herd_ids = st.session_state.herd["ID"].tolist()
            selected_ids = st.multiselect("اختر الأغنام:", herd_ids, format_func=format_sheep_label)
            c1, c2, c3 = st.columns(3)
            with c1: action_type = st.radio("نوع الإجراء:", ["تطعيم", "جرعة طفيلية", "تغطيس"])
            with c2:
                tr_opts = ['إيفومك', 'معوي/دموي', 'طاعون', 'جدري', 'حمى قلاعية'] if action_type == "تطعيم" else (['جرعة كبدية', 'جرعة معوية'] if action_type == "جرعة طفيلية" else ['تغطيس شامل'])
                treatment = st.selectbox("العلاج:", tr_opts)
            with c3:
                date = str(st.date_input("التاريخ:"))
            img_file = st.file_uploader("صورة التوثيق (اختياري)", type=['jpg', 'png'])
            
            if st.button("💾 حفظ الإجراء"):
                if not selected_ids: st.warning("⚠️ الرجاء اختيار رأس واحد على الأقل.")
                else:
                    selected_collars = [get_collar_by_id(sid) for sid in selected_ids]
                    new_hist = pd.DataFrame([{
                        "ID": str(uuid.uuid4()), "التاريخ": date, "الإجراء": action_type,
                        "العلاج": treatment, "الأغنام": ", ".join(selected_collars),
                        "صورة": save_image(img_file)
                    }])
                    st.session_state.history = pd.concat([st.session_state.history, new_hist], ignore_index=True)
                    save_data(st.session_state.history, HISTORY_FILE)
                    st.session_state.toast = "تمت إضافة الإجراء بنجاح! ✅"
                    st.rerun()
    else:
        st.warning("يجب إضافة أغنام أولاً.")

# --- التبويب الثالث: السجل الطبي ---
with tab3:
    st.subheader("📋 السجل الطبي")
    if not st.session_state.history.empty:
        for idx, row in st.session_state.history.iterrows():
            with st.expander(f"🗓️ {row['التاريخ']} - {row['الإجراء']} ({row['العلاج']})"):
                if row.get('صورة') and os.path.exists(row['صورة']):
                    st.image(row['صورة'], width=150)
                st.write(f"**الأغنام:** {row['الأغنام']}")
                
                with st.form(f"edit_hist_{idx}"):
                    c1, c2 = st.columns(2)
                    action_opts = ["تطعيم", "جرعة طفيلية", "تغطيس"]
                    act_idx = action_opts.index(row['الإجراء']) if row['الإجراء'] in action_opts else 0
                    with c1: selected_action = st.selectbox("الإجراء", action_opts, index=act_idx)
                    
                    tr_opts = ['إيفومك', 'معوي/دموي', 'طاعون', 'جدري', 'حمى قلاعية'] if selected_action == "تطعيم" else (['جرعة كبدية', 'جرعة معوية'] if selected_action == "جرعة طفيلية" else ['تغطيس شامل'])
                    tr_idx = tr_opts.index(row['العلاج']) if row['العلاج'] in tr_opts else 0
                    with c2: new_treat = st.selectbox("العلاج", tr_opts, index=tr_idx)
                    
                    new_date = st.date_input("التاريخ", value=pd.to_datetime(row['التاريخ']))
                    remove_hist_img = st.checkbox("🗑️ حذف الصورة الحالية") if row.get('صورة') and os.path.exists(row['صورة']) else False
                    new_img = st.file_uploader("تحديث صورة التوثيق", type=['jpg', 'png'])
                    
                    if st.form_submit_button("حفظ التعديلات"):
                        st.session_state.history.at[idx, "التاريخ"] = str(new_date)
                        st.session_state.history.at[idx, "الإجراء"] = selected_action
                        st.session_state.history.at[idx, "العلاج"] = new_treat
                        if remove_hist_img:
                            safe_delete_image(row['صورة'])
                            st.session_state.history.at[idx, "صورة"] = ""
                        if new_img:
                            if row['صورة']: safe_delete_image(row['صورة'])
                            st.session_state.history.at[idx, "صورة"] = save_image(new_img)
                        save_data(st.session_state.history, HISTORY_FILE)
                        st.session_state.toast = "تم تحديث السجل! ✅"
                        st.rerun()
                
                if st.button("❌ حذف السجل", key=f"del_hist_{idx}"):
                    if row['صورة']: safe_delete_image(row['صورة'])
                    st.session_state.history = st.session_state.history.drop(idx).reset_index(drop=True)
                    save_data(st.session_state.history, HISTORY_FILE)
                    st.session_state.toast = "تم حذف السجل! 🗑️"
                    st.rerun()
    else:
        st.info("لا توجد سجلات طبية بعد.")

# --- التبويب الرابع: الإدارة (تم إضافته من الصفر) ---
with tab4:
    st.subheader("➕ إدارة القطيع")
    
    with st.expander("✨ إضافة رأس جديد", expanded=True):
        with st.form("add_sheep_form"):
            c1, c2 = st.columns(2)
            with c1: collar = st.text_input("القلادة / الرقم")
            with c2: gender = st.selectbox("الجنس", ["أنثى", "ذكر", "أنثى صغيرة", "ذكر صغير"])
            
            c3, c4 = st.columns(2)
            with c3: age = st.number_input("العمر", min_value=0, value=0)
            with c4: age_unit = st.selectbox("وحدة العمر", ["شهر", "سنة"])
            
            births = st.number_input("عدد الولادات", min_value=0, value=0) if "أنثى" in gender else 0
            
            females_only = st.session_state.herd[st.session_state.herd["الجنس"].isin(["أنثى", "أنثى صغيرة"])]
            mother_options = [None] + females_only["ID"].tolist()
            mother_id = st.selectbox("الأم (اختياري)", mother_options, format_func=lambda x: "لا يوجد" if x is None else format_sheep_label(x))
            
            img_file = st.file_uploader("صورة (اختياري)", type=['jpg', 'png'])
            
            if st.form_submit_button("إضافة للقطيع 🐑"):
                if not collar: st.error("الرجاء إدخال رقم القلادة.")
                else:
                    new_id = str(uuid.uuid4())
                    new_sheep = pd.DataFrame([{
                        "ID": new_id, "القلادة": collar, "الجنس": gender, "العمر": age,
                        "وحدة": age_unit, "عدد الولادات": births, "صورة": save_image(img_file),
                        "اللقاحات": "[]", "الجرعات": "[]", "آخر تغطيس": "",
                        "الأم": mother_id if mother_id else "", "الأبناء": "[]"
                    }])
                    st.session_state.herd = pd.concat([st.session_state.herd, new_sheep], ignore_index=True)
                    if mother_id: add_kid_to_mother(mother_id, new_id)
                    save_data(st.session_state.herd, DATA_FILE)
                    st.session_state.toast = "تمت الإضافة بنجاح! ✅"
                    st.rerun()

    st.markdown("### ✏️ تعديل أو حذف")
    if not st.session_state.herd.empty:
        edit_id = st.selectbox("اختر الرأس للتعديل/الحذف:", st.session_state.herd["ID"].tolist(), format_func=format_sheep_label)
        if edit_id:
            row_idx = st.session_state.herd.index[st.session_state.herd["ID"] == edit_id][0]
            row_data = st.session_state.herd.iloc[row_idx]
       
