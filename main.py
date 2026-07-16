import streamlit as st
import pandas as pd
import json
import os
import uuid
import ast

# ─── إعداد الصفحة ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sheep Manager Pro", page_icon="🐑", layout="wide")

# CSS المخصص (كامل)
st.markdown("""<style>
    .stApp { background: #0b1f16; color: #eef6f0; }
    .stTabs [data-baseweb="tab"] { background: #123326; color: #93b3a1; border-radius: 10px; margin: 2px; }
    .stTabs [aria-selected="true"] { background: #2f6b48 !important; color: white !important; }
    .stButton > button { background: #2f6b48; color: white; border-radius: 8px; width: 100%; }
    [data-testid="stExpander"] { background: #123326; border: 1px solid #16402f; border-radius: 10px; }
</style>""", unsafe_allow_html=True)

# ─── الإعدادات والدوال المساعدة ───────────────────────────────────────────────
DATA_FILE = "herd_data.json"
HISTORY_FILE = "medical_history.json"
REQUIRED_COLS = ["ID", "القلادة", "الجنس", "العمر", "وحدة", "عدد الولادات", "صورة", "اللقاحات", "الجرعات", "آخر تغطيس", "الأم", "الأبناء"]
HISTORY_COLS = ["ID", "التاريخ", "الإجراء", "العلاج", "الأغنام", "صورة"]

if not os.path.exists("images"): os.makedirs("images")

def load_data(file, cols):
    if not os.path.exists(file): return pd.DataFrame(columns=cols)
    with open(file, "r", encoding="utf-8") as f: return pd.DataFrame(json.load(f))

def save_data(df, file):
    df.to_json(file, orient="records", force_ascii=False, indent=4)

def get_collar_name(sheep_id):
    row = st.session_state.herd[st.session_state.herd["ID"] == sheep_id]
    return row.iloc[0]["القلادة"] if not row.empty else "غير معروف"

# تهيئة الحالة
if "herd" not in st.session_state: st.session_state.herd = load_data(DATA_FILE, REQUIRED_COLS)
if "history" not in st.session_state: st.session_state.history = load_data(HISTORY_FILE, HISTORY_COLS)

# ─── واجهة التطبيق ───────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 القطيع", "💉 إجراء", "📋 السجل", "⚙️ إدارة", "💾 نسخة احتياطية"])

with tab1:
    st.subheader("🐏 عرض القطيع")
    t1, t2, t3 = st.tabs(["ذكور", "إناث", "صغار"])
    with t1:
        for _, row in st.session_state.herd[st.session_state.herd["الجنس"] == "ذكر"].iterrows():
            st.write(f"🏷️ {row['القلادة']} (عمر: {row['العمر']})")
    with t2:
        for _, row in st.session_state.herd[st.session_state.herd["الجنس"] == "أنثى"].iterrows():
            st.write(f"🏷️ {row['القلادة']} (عمر: {row['العمر']})")
    with t3:
        for _, row in st.session_state.herd[st.session_state.herd["العمر"] < 6].iterrows():
            st.write(f"🏷️ {row['القلادة']} (صغير)")

with tab2:
    st.subheader("💉 تسجيل إجراء طبي")
    with st.form("medical_form"):
        selected = st.multiselect("اختر الأغنام", st.session_state.herd["ID"].tolist(), format_func=get_collar_name)
        action = st.selectbox("الإجراء", ["تطعيم", "جرعة", "تغطيس"])
        treat = st.text_input("العلاج")
        if st.form_submit_button("حفظ"):
            new_row = {"ID": str(uuid.uuid4()), "التاريخ": str(datetime.now().date()), "الإجراء": action, "العلاج": treat, "الأغنام": str(selected), "صورة": ""}
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.history, HISTORY_FILE)
            st.rerun()

with tab3:
    st.subheader("📋 السجل الطبي")
    if not st.session_state.history.empty:
        df_view = st.session_state.history.copy()
        # تحويل كودات الأغنام إلى أسماء
        def resolve_sheep(val):
            try:
                ids = ast.literal_eval(val)
                return ", ".join([get_collar_name(i) for i in ids])
            except: return val
        df_view["الأغنام"] = df_view["الأغنام"].apply(resolve_sheep)
        st.table(df_view[["التاريخ", "الإجراء", "العلاج", "الأغنام"]])

with tab4:
    st.subheader("⚙️ إدارة القطيع")
    c1, c2, c3 = st.columns(3)
    
    with c1: # إضافة
        st.markdown("#### ➕ إضافة")
        with st.form("add_sheep"):
            n = st.text_input("اسم القلادة")
            g = st.selectbox("الجنس", ["ذكر", "أنثى"])
            if st.form_submit_button("حفظ"):
                st.session_state.herd = pd.concat([st.session_state.herd, pd.DataFrame([{"ID": str(uuid.uuid4()), "القلادة": n, "الجنس": g, "العمر": 0, "وحدة": "شهر", "الأبناء": "[]"}])], ignore_index=True)
                save_data(st.session_state.herd, DATA_FILE)
                st.rerun()
    
    with c2: # تعديل
        st.markdown("#### ✏️ تعديل")
        sid = st.selectbox("اختر للتعديل", st.session_state.herd["ID"].tolist(), format_func=get_collar_name)
        row = st.session_state.herd[st.session_state.herd["ID"] == sid].iloc[0]
        with st.form("edit_form"):
            new_name = st.text_input("اسم جديد", value=row["القلادة"])
            if st.form_submit_button("تحديث"):
                idx = st.session_state.herd[st.session_state.herd["ID"] == sid].index[0]
                st.session_state.herd.at[idx, "القلادة"] = new_name
                save_data(st.session_state.herd, DATA_FILE)
                st.rerun()

    with c3: # حذف
        st.markdown("#### 🗑️ حذف")
        del_id = st.selectbox("اختر للحذف", st.session_state.herd["ID"].tolist(), format_func=get_collar_name)
        if st.button("حذف نهائي"):
            st.session_state.herd = st.session_state.herd[st.session_state.herd["ID"] != del_id]
            save_data(st.session_state.herd, DATA_FILE)
            st.rerun()

with tab5:
    st.subheader("💾 النسخ الاحتياطي")
    if st.button("تحميل نسخة احتياطية"):
        st.write("تم تجهيز البيانات للتحميل...") # هنا يمكن إضا
فة كود التنزيل
