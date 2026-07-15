import streamlit as st
import pandas as pd
from datetime import datetime

# ─── إعداد الصفحة ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="نظام إدارة القطيع",
    page_icon="🐑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS مخصص – طابع أخضر غامق ───────────────────────────────────────────────
st.markdown("""
<style>
    /* الخلفية الرئيسية */
    .stApp {
        background-color: #0d2818;
        color: #c8e6c9;
    }

    /* الشريط الجانبي */
    section[data-testid="stSidebar"] {
        background-color: #0a2010 !important;
        border-right: 2px solid #2e7d32;
    }
    section[data-testid="stSidebar"] * {
        color: #c8e6c9 !important;
    }
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
    section[data-testid="stSidebar"] .stTextInput input,
    section[data-testid="stSidebar"] .stNumberInput input {
        background-color: #1b3a2a !important;
        border-color: #388e3c !important;
        color: #e8f5e9 !important;
    }

    /* العناوين */
    h1, h2, h3, h4 {
        color: #81c784 !important;
    }

    /* بطاقات العدادات */
    .metric-card {
        background: linear-gradient(135deg, #1b3a2a, #0d2818);
        border: 1px solid #2e7d32;
        border-radius: 12px;
        padding: 18px 22px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.5);
        margin-bottom: 10px;
    }
    .metric-label {
        font-size: 13px;
        color: #a5d6a7;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 42px;
        font-weight: 800;
        color: #66bb6a;
        line-height: 1;
    }
    .metric-value.danger { color: #ef5350; }
    .metric-value.male   { color: #42a5f5; }
    .metric-value.female { color: #f48fb1; }
    .metric-value.elite  { color: #ffd54f; }

    /* بطاقات الخانات */
    .pen-card {
        background: #122a1a;
        border: 1px solid #388e3c;
        border-top: 4px solid;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 14px;
    }
    .pen-quarantine  { border-top-color: #ef5350; }
    .pen-elite       { border-top-color: #ffd54f; }
    .pen-males       { border-top-color: #42a5f5; }
    .pen-young       { border-top-color: #ab47bc; }

    .pen-header {
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .pen-quarantine  .pen-header { color: #ef9a9a; }
    .pen-elite       .pen-header { color: #fff176; }
    .pen-males       .pen-header { color: #90caf9; }
    .pen-young       .pen-header { color: #ce93d8; }

    /* الجداول */
    .stDataFrame, [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
    }
    .stDataFrame thead th {
        background-color: #1b3a2a !important;
        color: #a5d6a7 !important;
    }
    .stDataFrame tbody tr:nth-child(even) td {
        background-color: #162c1e !important;
    }
    .stDataFrame tbody tr:hover td {
        background-color: #1e4d2b !important;
    }

    /* أزرار */
    .stButton > button {
        background: linear-gradient(135deg, #2e7d32, #1b5e20);
        color: #e8f5e9;
        border: 1px solid #4caf50;
        border-radius: 8px;
        font-weight: 700;
        font-size: 15px;
        padding: 10px 0;
        width: 100%;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #388e3c, #2e7d32);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(46,125,50,0.5);
    }

    /* تذييل */
    footer { visibility: hidden; }

    /* فاصل */
    hr { border-color: #2e7d32; opacity: 0.4; }

    /* عنوان الموقع */
    .main-title {
        text-align: center;
        padding: 20px 0 10px;
        font-size: 30px;
        font-weight: 800;
        color: #a5d6a7;
        letter-spacing: 1px;
    }
    .sub-title {
        text-align: center;
        color: #66bb6a;
        font-size: 14px;
        margin-bottom: 20px;
    }

    /* input labels */
    .stSelectbox label, .stNumberInput label,
    .stTextInput label, .stRadio label {
        color: #a5d6a7 !important;
        font-weight: 600 !important;
    }

    /* selectbox dropdown */
    div[data-baseweb="select"] > div {
        background-color: #1b3a2a !important;
        border-color: #388e3c !important;
        color: #e8f5e9 !important;
    }
    div[data-baseweb="select"] span {
        color: #e8f5e9 !important;
    }
    div[data-baseweb="popover"] ul {
        background-color: #1b3a2a !important;
    }
    div[data-baseweb="popover"] li {
        color: #e8f5e9 !important;
    }
    div[data-baseweb="popover"] li:hover {
        background-color: #2e7d32 !important;
    }

    /* number/text inputs */
    input[type="number"], input[type="text"] {
        background-color: #1b3a2a !important;
        border-color: #388e3c !important;
        color: #e8f5e9 !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── البيانات في الجلسة ───────────────────────────────────────────────────────
if "herd" not in st.session_state:
    st.session_state.herd = pd.DataFrame(columns=[
        "رقم القلادة", "الجنس", "العمر (أشهر)",
        "عدد الولادات", "الحالة الصحية", "عدد المواليد المنتجة",
        "تاريخ الإضافة"
    ])

# ─── دالة تصنيف الرأس ────────────────────────────────────────────────────────
def classify(row):
    """تُرجع اسم الخانة المناسبة للرأس."""
    if row["الحالة الصحية"] != "سليم":
        return "عزل صحي"
    if row["الجنس"] == "أنثى (نعجة)" and row["عدد الولادات"] >= 3:
        return "أمهات النخبة"
    if row["الجنس"] in ("ذكر (كبش)", "ذكر (فحل)"):
        return "كباش وفحول"
    return "بكاري وطليان"

# ─── الشريط الجانبي – إضافة رأس جديد ────────────────────────────────────────
with st.sidebar:
    st.markdown("## ➕ إضافة رأس جديد")
    st.markdown("---")

    collar   = st.text_input("🏷️ رقم القلادة", placeholder="مثال: SH-1042")
    gender   = st.selectbox("⚧ الجنس", [
        "أنثى (نعجة)", "ذكر (كبش)", "ذكر (فحل)", "أنثى صغيرة (طلية)", "ذكر صغير (بكري)"
    ])
    age      = st.number_input("📅 العمر (بالأشهر)", min_value=0, max_value=240, value=12, step=1)
    births   = st.number_input("🍼 عدد الولادات", min_value=0, max_value=30, value=0, step=1)
    health   = st.selectbox("🩺 الحالة الصحية", [
        "سليم", "مريض", "في فترة تعافي", "مشتبه به"
    ])
    offspring = st.number_input("🐑 عدد المواليد المنتجة", min_value=0, max_value=60, value=0, step=1)

    st.markdown("---")
    if st.button("✅ إضافة إلى القطيع"):
        if not collar.strip():
            st.error("⚠️ يرجى إدخال رقم القلادة")
        elif collar.strip() in st.session_state.herd["رقم القلادة"].values:
            st.warning("⚠️ رقم القلادة موجود مسبقاً")
        else:
            new_row = {
                "رقم القلادة": collar.strip(),
                "الجنس": gender,
                "العمر (أشهر)": age,
                "عدد الولادات": births,
                "الحالة الصحية": health,
                "عدد المواليد المنتجة": offspring,
                "تاريخ الإضافة": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.herd = pd.concat(
                [st.session_state.herd, pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.success(f"✅ تمت إضافة القلادة {collar.strip()} بنجاح")
            st.rerun()

    # حذف رأس
    if not st.session_state.herd.empty:
        st.markdown("---")
        st.markdown("### 🗑️ حذف رأس من القطيع")
        collars_list = st.session_state.herd["رقم القلادة"].tolist()
        del_collar   = st.selectbox("اختر القلادة للحذف", collars_list)
        if st.button("❌ حذف"):
            st.session_state.herd = st.session_state.herd[
                st.session_state.herd["رقم القلادة"] != del_collar
            ].reset_index(drop=True)
            st.success(f"تم حذف القلادة {del_collar}")
            st.rerun()

# ─── الجزء الرئيسي ───────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🐑 نظام إدارة وفرز القطيع</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">فرز ذكي تلقائي · إدارة شاملة للأغنام والمواشي</div>', unsafe_allow_html=True)

df = st.session_state.herd.copy()

# ─── حساب الخانات ────────────────────────────────────────────────────────────
if not df.empty:
    df["الخانة"] = df.apply(classify, axis=1)
    quarantine = df[df["الخانة"] == "عزل صحي"]
    elite      = df[df["الخانة"] == "أمهات النخبة"]
    males      = df[df["الخانة"] == "كباش وفحول"]
    young      = df[df["الخانة"] == "بكاري وطليان"]
    total      = len(df)
    male_cnt   = len(df[df["الجنس"].str.contains("ذكر")])
    female_cnt = len(df[df["الجنس"].str.contains("أنثى")])
    sick_cnt   = len(df[df["الحالة الصحية"] != "سليم"])
else:
    quarantine = elite = males = young = pd.DataFrame()
    total = male_cnt = female_cnt = sick_cnt = 0

# ─── العدادات الذكية ─────────────────────────────────────────────────────────
st.markdown("### 📊 العدادات الذكية")
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">إجمالي الحلال</div>
        <div class="metric-value">{total}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">الذكور</div>
        <div class="metric-value male">{male_cnt}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">الإناث</div>
        <div class="metric-value female">{female_cnt}</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">الحالات المرضية</div>
        <div class="metric-value danger">{sick_cnt}</div>
    </div>""", unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">أمهات النخبة</div>
        <div class="metric-value elite">{len(elite)}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─── الخانات الأربعة ─────────────────────────────────────────────────────────
st.markdown("### 🏠 الخانات الأربعة – الفرز التلقائي")

col_a, col_b = st.columns(2)

# ── خانة 1: عزل صحي ──────────────────────────────────────────────────────────
with col_a:
    st.markdown(f"""
    <div class="pen-card pen-quarantine">
        <div class="pen-header">🔴 خانة العزل الصحي &nbsp;·&nbsp; {len(quarantine)} رأس</div>
    </div>""", unsafe_allow_html=True)
    if quarantine.empty:
        st.info("لا توجد حالات عزل صحي حالياً ✅")
    else:
        st.dataframe(
            quarantine.drop(columns=["الخانة"]),
            use_container_width=True,
            hide_index=True
        )

# ── خانة 2: أمهات النخبة ─────────────────────────────────────────────────────
with col_b:
    st.markdown(f"""
    <div class="pen-card pen-elite">
        <div class="pen-header">⭐ خانة الأمهات النخبة &nbsp;·&nbsp; {len(elite)} رأس</div>
    </div>""", unsafe_allow_html=True)
    if elite.empty:
        st.info("لا توجد أمهات نخبة بعد (نعاج ولدت 3 مرات فأكثر)")
    else:
        st.dataframe(
            elite.drop(columns=["الخانة"]),
            use_container_width=True,
            hide_index=True
        )

col_c, col_d = st.columns(2)

# ── خانة 3: كباش وفحول ───────────────────────────────────────────────────────
with col_c:
    st.markdown(f"""
    <div class="pen-card pen-males">
        <div class="pen-header">🔵 خانة الكباش والفحول &nbsp;·&nbsp; {len(males)} رأس</div>
    </div>""", unsafe_allow_html=True)
    if males.empty:
        st.info("لا يوجد كباش أو فحول مسجلون بعد")
    else:
        st.dataframe(
            males.drop(columns=["الخانة"]),
            use_container_width=True,
            hide_index=True
        )

# ── خانة 4: بكاري وطليان ─────────────────────────────────────────────────────
with col_d:
    st.markdown(f"""
    <div class="pen-card pen-young">
        <div class="pen-header">🟣 خانة البكاري والطليان &nbsp;·&nbsp; {len(young)} رأس</div>
    </div>""", unsafe_allow_html=True)
    if young.empty:
        st.info("لا يوجد صغار مسجلون بعد")
    else:
        st.dataframe(
            young.drop(columns=["الخانة"]),
            use_container_width=True,
            hide_index=True
        )

# ─── عرض القطيع الكامل ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📋 سجل القطيع الكامل")

if df.empty:
    st.markdown("""
    <div style="text-align:center; padding:40px; color:#66bb6a; font-size:18px;">
        🐑 القطيع فارغ – استخدم القائمة الجانبية لإضافة رؤوس جديدة
    </div>
    """, unsafe_allow_html=True)
else:
    # تلوين الخانات في الجدول
    def style_pen(val):
        colors = {
            "عزل صحي":     "background-color:#3e1a1a; color:#ef9a9a",
            "أمهات النخبة": "background-color:#3e3400; color:#fff176",
            "كباش وفحول":  "background-color:#0d2340; color:#90caf9",
            "بكاري وطليان":"background-color:#2a1a3e; color:#ce93d8",
        }
        return colors.get(val, "")

    styled_df = df.copy()
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "الخانة": st.column_config.Column(width="medium"),
        }
        )
    
