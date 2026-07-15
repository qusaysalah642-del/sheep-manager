import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="Sheep Manager Pro | إدارة الحلال",
    page_icon="🐑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم مخصص باللون الأخضر الغامق الفخم المتناسق مع الواجهة الداكنة
st.markdown("""
    <style>
    /* تغيير خلفية التطبيق العامة */
    .stApp {
        background-color: #0d1510; 
        color: #f1f5f9;
    }
    /* إحصائيات القطيع والمقاييس */
    div[data-testid="stMetricValue"] {
        color: #10b981 !important; 
    }
    /* القائمة الجانبية */
    .stSidebar {
        background-color: #063c2c !important; 
    }
    /* تعديل الأزرار لتناسب الهوية الخضراء */
    .stButton>button {
        background-color: #047857 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #059669 !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    /* محاذاة النصوص والاتجاهات للغة العربية */
    h1, h2, h3, p, span, label, .stSelectbox, .stTextInput {
        text-align: right;
        direction: rtl;
    }
    div[data-testid="stMarkdownContainer"] > p {
        text-align: right;
        direction: rtl;
    }
    </style>
""", unsafe_allow_html=True)

# اسم ملف قاعدة البيانات المحلي
DATA_FILE = "herd_data.json"

# دالة تحميل البيانات من الملف السحابي
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# دالة حفظ البيانات في الملف
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# تحميل البيانات عند الإقلاع
herd_list = load_data()

# الهيدر الرئيسي للتطبيق
st.markdown("<h1 style='text-align: center; color: #10b981;'>🐑 Sheep Manager Pro</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #94a3b8;'>النظام السحابي الذكي لإدارة الحلال والمواشي</h3>", unsafe_allow_html=True)
st.write("---")

# تصميم القائمة الجانبية للتنقل
st.sidebar.markdown("<h2 style='text-align: center; color: #10b981;'>قائمة التحكم</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio(
    "",
    ["📊 لوحة التحكم والإحصائيات", "➕ إضافة رأس جديد", "🔍 البحث وإدارة القطيع"],
    index=0
)

# الشاشة الأولى: الإحصائيات وجدول البيانات
if menu == "📊 لوحة التحكم والإحصائيات":
    st.markdown("### 📈 حالة القطيع الحالية")
    
    if not herd_list:
        st.info("لا توجد بيانات مسجلة حالياً. اذهب إلى قائمة 'إضافة رأس جديد' للبدء في ملء بيانات حلالك!")
    else:
        # حساب المتغيرات الأساسية وعرضها في كروت إحصائية ممتازة
        total_sheep = len(herd_list)
        df = pd.DataFrame(herd_list)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="إجمالي عدد الرؤوس", value=f"{total_sheep} رأس")
        with col2:
            healthy_count = len(df[df['status'] == 'ممتازة']) if 'status' in df.columns else 0
            st.metric(label="حالة صحية ممتازة", value=f"{healthy_count} رأس")
        with col3:
            care_count = len(df[df['status'] == 'تحتاج رعاية/علاج']) if 'status' in df.columns else 0
            st.metric(label="تحت العلاج/الرعاية", value=f"{care_count} رأس")
        
        st.write("---")
        st.markdown("### 📋 السجل التفصيلي للحلال")
        
        # تحضير الجدول للعرض باللغة العربية
        df_display = df.copy()
        df_display.columns = ["الرقم/الوسم", "السلالة/النوع", "العمر (أشهر)", "الحالة الصحية", "تاريخ الإضافة", "ملاحظات إضافية"]
        st.dataframe(df_display, use_container_width=True)

# الشاشة الثانية: إضافة رأس جديد
elif menu == "➕ إضافة رأس جديد":
    st.markdown("### ➕ تسجيل رأس جديد في السجل")
    
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sheep_id = st.text_input("رقم الوسم / الهوية (ID)", placeholder="مثال: SH-101")
            breed = st.selectbox("السلالة أو النوع", ["عواسي", "عرابي", "نجدي", "نعيمي", "مستورد", "آخر"])
        with col2:
            age = st.number_input("العمر بالشهور", min_value=1, max_value=120, value=6)
            status = st.selectbox("الحالة الصحية العامة", ["ممتازة", "جيدة", "تحتاج رعاية/علاج", "مريض"])
            
        notes = st.text_area("أية ملاحظات إضافية (التحصينات، العلاجات، المالك، إلخ...) ")
        
        submit_btn = st.form_submit_button("حفظ الرأس في النظام 💾")
        
        if submit_btn:
            if not sheep_id.strip():
                st.error("الرجاء كتابة رقم الوسم للتعريف!")
            elif any(item['id'] == sheep_id.strip() for item in herd_list):
                st.error("رقم الوسم هذا مكرر ومسجل مسبقاً! يرجى اختيار رقم فريد.")
            else:
                # إعداد الكائن الجديد
                new_entry = {
                    "id": sheep_id.strip(),
                    "breed": breed,
                    "age": int(age),
                    "status": status,
                    "date_added": datetime.now().strftime("%Y-%m-%d"),
                    "notes": notes
                }
                herd_list.append(new_entry)
                save_data(herd_list)
                st.success(f"تم تسجيل الرأس ذو الرقم ({sheep_id}) بنجاح في قاعدة البيانات السحابية! 🎉")

# الشاشة الثالثة: البحث والحذف والتعديل
elif menu == "🔍 البحث وإدارة القطيع":
    st.markdown("### 🔍 البحث السريع وإدارة البيانات")
    
    if not herd_list:
        st.info("لا توجد بيانات مسجلة للبحث فيها حالياً.")
    else:
        search = st.text_input("ابحث برقم الوسم أو السلالة", placeholder="اكتب رقم الوسم أو النوع هنا...")
        df = pd.DataFrame(herd_list)
        
        # تصفية نتائج البحث
        if search:
            filtered = df[df['id'].str.contains(search, case=False) | df['breed'].str.contains(search, case=False)]
        else:
            filtered = df
            
        st.write(f"عدد النتائج المكتشفة: {len(filtered)}")
        
        # عرض البيانات بشكل بطاقات تفصيلية قابلة للتعديل أو الحذف
        for idx, row in filtered.iterrows():
            with st.expander(f"🐑 رأس رقم: {row['id']} | النوع: {row['breed']}"):
                st.write(f"**العمر:** {row['age']} شهر تقريباً")
                st.write(f"**الحالة الصحية:** {row['status']}")
                st.write(f"**تاريخ التسجيل:** {row['date_added']}")
                st.write(f"**الملاحظات الحالية:** {row['notes'] if row['notes'] else 'لا توجد ملاحظات.'}")
                
                # خيار حذف الرأس من القطيع
                if st.button(f"حذف وإسقاط الرأس {row['id']} من السجل 🗑️", key=f"btn_del_{row['id']}"):
                    herd_list = [item for item in herd_list if item['id'] != row['id']]
                    save_data(herd_list)
                    st.success("تم حذف البيانات بنجاح! يرجى تحديث الصفحة لتحديث العرض.")
                    st.rerun()
                
