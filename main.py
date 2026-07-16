import streamlit as st
import pandas as pd
import json
import os
import uuid
import ast
from datetime import datetime

# ═════════════════════ إعداد الصفحة ═════════════════════

st.set_page_config(page_title="Sheep Manager Pro", page_icon="🐑", layout="wide")

# ═════════════════════ نظام الألوان (Design tokens) ═════════════════════
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

# إنشاء مجلد الصور إذا لم يكن موجوداً
if not os.path.exists("images"):
    os.makedirs("images")

# نظام الإشعارات (التوست)
if "toast" not in st.session_state:
    st.session_state.toast = None

if st.session_state.toast:
    st.toast(st.session_state.toast)
    st.session_state.toast = None

# ═════════════════════ التنسيقات المخصصة CSS ═════════════════════
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;700;800&family=Tajawal:wght@400;500;700&display=swap');

    html, body, [class*="css"] {{ font-family: 'Tajawal', sans-serif; }}
    h1, h2, h3, .app-hero-title {{ font-family: 'Cairo', sans-serif; }}

    .stApp {{ background: linear-gradient(180deg, {C_BG_DEEP} 0%, #0e2a1e 100%); color: {C_TEXT}; }}

    /* ─── الهيدر الرئيسي ─── */
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

    /* ─── تبويبات علوية بشكل كبسولات ─── */
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

    /* ─── البطاقات ─── */
    [data-testid="stExpander"] {{
        background: {C_BG_PANEL};
        border: 1px solid {C_BORDER} !important;
        border-radius: 14px !important;
        margin-bottom: 10px;
    }}
    [data-testid="stExpander"] summary {{ font-weight: 700; font-size: 15px; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 14px !important; }}

    /* ─── الأزرار ─── */
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
    .stFormSubmitButton > button {{
        background: linear-gradient(135deg, {C_AMBER} 0%, {C_AMBER_DARK} 100%) !important;
        color: #24170a !important; border: none; border-radius: 10px; font-weight: 800;
    }}

    /* ─── الحقول والمدخلات ─── */
    .stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] > div {{
        background: {C_BG_DEEP} !important;
        border: 1px solid {C_BORDER} !important;
        border-radius: 10px !important;
        color: {C_TEXT} !important;
    }}

    /* ─── المقاييس ─── */
    [data-testid="stMetric"] {{
        background: {C_BG_PANEL};
        border: 1px solid {C_BORDER};
        border-radius: 14px;
        padding: 10px 6px;
    }}
    [data-testid="stMetricValue"] {{ font-size: 22px !important; color: {C_AMBER} !important; font-weight: 800 !important; }}
    [data-testid="stMetricLabel"] {{ font-size: 13px !important; color: {C_TEXT_MUTED} !important; }}

    /* ─── شارة "تاق الأذن" ─── */
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

    /* ─── الشريط الجانبي ─── */
    section[data-testid="stSidebar"] {{
        background: {C_BG_PANEL};
        border-left: 1px solid {C_BORDER};
    }}

    hr {{ border-color: {C_BORDER} !important; }}
</style>
""", unsafe_allow_html=True)

# ═════════════════════ بانر الهيدر ═════════════════════
st.markdown("""
<div class="app-hero">
    <div class="app-hero-icon">🐑</div>
    <div>
        <p class="app-hero-title">Sheep Manager Pro</p>
        <p class="app-hero-subtitle">إدارة القطيع، التطعيمات، والسجل الطبي في مكان واحد</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ═════════════════════ إدارة البيانات ═════════════════════
DATA_FILE = "herd_data.json"
HISTORY_FILE = "medical_history.json"
BACKUP_DIR = "backups"

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
    """يحذف ملف صورة بأمان إذا كان موجوداً."""
    if path and isinstance(path, str) and os.path.exists(path):
        try:
            os.remove(path)
        except OSError as e:
            st.warning(f"تعذر حذف ملف الصورة: {e}")

def safe_literal_eval(value, default=None):
    """يحلل نصاً يمثل قائمة بايثون بأمان."""
    if default is None:
        default = []
    try:
        result = ast.literal_eval(value)
        return result if isinstance(result, list) else default
    except (ValueError, SyntaxError, TypeError):
        return default

def safe_int(value, default=0):
    """يحوّل قيمة إلى رقم صحيح بأمان."""
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (ValueError, TypeError):
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
        st.error(f"تعذرت قراءة ملف البيانات ({file}): {e}. تم تحميل قاعدة بيانات فارغة.")
        return pd.DataFrame(columns=columns)

def save_data(df, file):
    try:
        df.to_json(file, orient="records", force_ascii=False, indent=4)
    except OSError as e:
        st.error(f"فشل حفظ البيانات في {file}: {e}")

# ═════════════════════ ترحيل بيانات الأم والأبناء (للمعرفات) ═════════════════════
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

# تحميل البيانات إلى الجلسة
if "herd" not in st.session_state:
    _herd = load_data(DATA_FILE, REQUIRED_COLS)
    _herd = migrate_relations_to_ids(_herd)
    st.session_state.herd = _herd
    save_data(st.session_state.herd, DATA_FILE)
if "history" not in st.session_state:
    st.session_state.history = load_data(HISTORY_FILE, HISTORY_COLS)

# ═════════════════════ دوال مساعدة للعلاقات والعرض ═════════════════════
def get_collar_by_id(sheep_id):
    """يرجع القلادة الحالية لرأس معيّن حسب الـ ID."""
    if not sheep_id:
        return ""
    row = st.session_state.herd[st.session_state.herd["ID"] == sheep_id]
    if row.empty:
        return "(محذوف)"
    return row.iloc[0]["القلادة"]

def format_sheep_label(sheep_id):
    """يبني تسمية عرض فريدة تجمع القلادة مع جزء من المعرف."""
    row = st.session_state.herd[st.session_state.herd["ID"] == sheep_id]
    if row.empty:
        return sheep_id
    row = row.iloc[0]
    short_id = str(sheep_id)[-4:] if len(str(sheep_id)) >= 4 else str(sheep_id)
    return f"{row['القلادة']} ({row['الجنس']} #{short_id})"

def add_kid_to_mother(mother_id, kid_id):
    """يضيف معرف الابن إلى قائمة أبناء الأم."""
    m_rows = st.session_state.herd[st.session_state.herd["ID"] == mother_id]
    if m_rows.empty:
        return
    m_idx = m_rows.index[0]
    kids = safe_literal_eval(st.session_state.herd.at[m_idx, "الأبناء"])
    if kid_id not in kids:
        kids.append(kid_id)
        st.session_state.herd.at[m_idx, "الأبناء"] = str(kids)

def remove_kid_from_mother(mother_id, kid_id):
    """يحذف معرف الابن من قائمة أبناء الأم."""
    m_rows = st.session_state.herd[st.session_state.herd["ID"] == mother_id]
    if m_rows.empty:
        return
    m_idx = m_rows.index[0]
    kids = safe_literal_eval(st.session_state.herd.at[m_idx, "الأبناء"])
    if kid_id in kids:
        kids.remove(kid_id)
        st.session_state.herd.at[m_idx, "الأبناء"] = str(kids)

# ═════════════════════ دوال النسخ الاحتياطي والاستيراد ═════════════════════
def create_backup():
    """إنشاء نسخة احتياطية كاملة من جميع البيانات والصور."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_id = f"backup_{timestamp}"
    backup_path = os.path.join(BACKUP_DIR, backup_id)
    os.makedirs(backup_path, exist_ok=True)
    
    # حفظ ملفات البيانات
    for file in [DATA_FILE, HISTORY_FILE]:
        if os.path.exists(file):
            import shutil
            shutil.copy2(file, os.path.join(backup_path, os.path.basename(file)))
    
    # حفظ مجلد الصور
    images_backup_path = os.path.join(backup_path, "images")
    if os.path.exists("images"):
        import shutil
        shutil.copytree("images", images_backup_path, dirs_exist_ok=True)
    
    return backup_id, backup_path

def list_backups():
    """عرض قائمة النسخ الاحتياطية المتاحة."""
    if not os.path.exists(BACKUP_DIR):
        return []
    backups = []
    for item in os.listdir(BACKUP_DIR):
        item_path = os.path.join(BACKUP_DIR, item)
        if os.path.isdir(item_path) and item.startswith("backup_"):
            timestamp_str = item.replace("backup_", "")
            try:
                dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                backups.append({
                    "id": item,
                    "path": item_path,
                    "timestamp": dt,
                    "display": dt.strftime("%Y-%m-%d %H:%M:%S")
                })
            except ValueError:
                continue
    return sorted(backups, key=lambda x: x["timestamp"], reverse=True)

def restore_backup(backup_id):
    """استعادة نسخة احتياطية محددة."""
    backup_path = os.path.join(BACKUP_DIR, backup_id)
    if not os.path.exists(backup_path):
        st.error("النسخة الاحتياطية غير موجودة!")
        return False
    
    try:
        import shutil
        # استعادة ملفات البيانات
        for file in [DATA_FILE, HISTORY_FILE]:
            source = os.path.join(backup_path, os.path.basename(file))
            if os.path.exists(source):
                shutil.copy2(source, file)
        
        # استعادة مجلد الصور
        images_source = os.path.join(backup_path, "images")
        if os.path.exists(images_source):
            if os.path.exists("images"):
                shutil.rmtree("images")
            shutil.copytree(images_source, "images")
        
        # إعادة تحميل البيانات
        st.session_state.herd = load_data(DATA_FILE, REQUIRED_COLS)
        st.session_state.history = load_data(HISTORY_FILE, HISTORY_COLS)
        return True
    except Exception as e:
        st.error(f"فشل استعادة النسخة الاحتياطية: {e}")
        return False

# ═════════════════════ الشريط الجانبي: إحصائيات سريعة ═════════════════════
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

# ═════════════════════ واجهة التطبيق الرئيسية ═════════════════════
tab1, tab2, tab3, tab4 = st.tabs(["🏠 القطيع", "💉 إجراء", "📋 السجل", "⚙️ إدارة"])

# ─── تبويب القطيع ───
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

# ─── تبويب تسجيل إجراء ───
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
        st.warning("يجب إضافة أ
