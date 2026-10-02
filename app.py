import streamlit as st
import pandas as pd
import plotly.express as px
from tax_calculator import calculate_tax_breakdown, get_optimizer_tip

# 1. ตั้งค่าหน้าเว็บให้ดูเรียบง่าย ไม่มีอิโมจิ
st.set_page_config(
    page_title="ระบบคำนวณภาษีเงินได้บุคคลธรรมดา",
    layout="wide"
)

# 2. ปรับแต่ง CSS สีตัวอักษรให้ดูเป็นทางการ (ใช้โทนสีเขียวคล้าย KBank)
st.markdown("""
    <style>
    .stMetric label { font-weight: bold; color: #555555; }
    h1, h2, h3 { color: #00A950; } 
    </style>
""", unsafe_allow_html=True)

st.title("ระบบคำนวณและวางแผนภาษีเงินได้บุคคลธรรมดา")
st.markdown("กรอกข้อมูลรายได้และค่าลดหย่อนของคุณเพื่อประเมินภาระภาษีเบื้องต้น")

# --- แถบด้านข้าง (Sidebar) สำหรับกรอกข้อมูล ---
st.sidebar.header("ส่วนที่ 1: ข้อมูลรายได้")
salary_monthly = st.sidebar.number_input("เงินเดือน (บาท/เดือน)", min_value=0, value=50000, step=1000)
bonus_yearly = st.sidebar.number_input("โบนัสและเงินพิเศษ (บาท/ปี)", min_value=0, value=100000, step=5000)
other_income = st.sidebar.number_input("รายได้อื่นๆ (บาท/ปี)", min_value=0, value=0, step=5000)
wht_paid = st.sidebar.number_input("ภาษีหัก ณ ที่จ่ายสะสม (บาท)", min_value=0, value=15000, step=1000)

total_income = (salary_monthly * 12) + bonus_yearly + other_income
deduct_expense = min(total_income * 0.5, 100000)

st.sidebar.markdown("---")
st.sidebar.header("ส่วนที่ 2: ข้อมูลค่าลดหย่อน")
personal_deduction = 60000
sso = st.sidebar.number_input("เงินสมทบประกันสังคม", min_value=0, max_value=9000, value=9000)
thai_esg = st.sidebar.number_input("กองทุน Thai ESG", min_value=0, max_value=300000, value=0, step=5000)
rmf = st.sidebar.number_input("กองทุน RMF", min_value=0, max_value=500000, value=0, step=5000)

total_deductions = personal_deduction + sso + thai_esg + rmf

# --- การจัดแบ่งหน้าหลักด้วยระบบ Tabs ---
tab1, tab2, tab3 = st.tabs(["สรุปผลการคำนวณ", "จำลองสถานการณ์ (What-If)", "อัปโหลดเอกสาร 50 ทวิ"])

# TAB 1: สรุปผลหลัก
with tab1:
    result = calculate_tax_breakdown(total_income, deduct_expense, total_deductions, wht_paid)

    st.subheader("ผลการประเมินภาษี")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("รายได้รวมทั้งปี", f"{total_income:,.0f} บาท")
    col2.metric("เงินได้สุทธิ", f"{result['net_income']:,.0f} บาท")
    col3.metric("อัตราภาษีสูงสุด", f"{result['highest_rate_percent']}%")

    diff = result["tax_difference"]
    if diff > 0:
        col4.metric("ภาษีที่ต้องชำระเพิ่ม", f"{diff:,.0f} บาท")
    else:
        col4.metric("ภาษีที่ได้รับคืน", f"{abs(diff):,.0f} บาท")

    st.markdown("---")
    st.subheader("ข้อเสนอแนะเพื่อการวางแผนภาษี")
    st.info(get_optimizer_tip(result["highest_rate_percent"]))

    # กราฟและตาราง (เปลี่ยนโทนสีเป็นสีเขียวเรียบหรู)
    chart_col, table_col = st.columns([1, 1])

    with chart_col:
        chart_data = pd.DataFrame({
            "รายการ": ["ค่าใช้จ่ายตามกฎหมาย", "ค่าลดหย่อน", "เงินได้สุทธิ"],
            "จำนวนเงิน": [deduct_expense, total_deductions, result["net_income"]]
        })
        # โทนสีเขียว 3 ระดับ
        fig = px.pie(chart_data, values="จำนวนเงิน", names="รายการ", hole=0.5,
                     color_discrete_sequence=['#A5D6A7', '#4CAF50', '#1B5E20'])
        fig.update_layout(margin=dict(t=20, b=20, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    with table_col:
        summary_table = pd.DataFrame({
            "รายการ": [
                "เงินได้พึงประเมิน",
                "หัก ค่าใช้จ่าย",
                "หัก ค่าลดหย่อน",
                "เงินได้สุทธิ",
                "ภาษีที่คำนวณได้",
                "หัก ภาษีที่จ่ายล่วงหน้า",
                "สรุปยอดภาษีสุทธิ"
            ],
            "จำนวนเงิน (บาท)": [
                f"{total_income:,.2f}",
                f"{deduct_expense:,.2f}",
                f"{total_deductions:,.2f}",
                f"{result['net_income']:,.2f}",
                f"{result['tax_total']:,.2f}",
                f"{wht_paid:,.2f}",
                f"{abs(diff):,.2f} ({'ชำระเพิ่ม' if diff > 0 else 'ได้รับคืน'})"
            ]
        })
        st.table(summary_table)

        # ปุ่มดาวน์โหลดไฟล์ CSV
        csv = summary_table.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="ดาวน์โหลดรายงานสรุป (CSV)",
            data=csv,
            file_name="tax_summary.csv",
            mime="text/csv"
        )

# TAB 2: เครื่องมือจำลองสถานการณ์
with tab2:
    st.subheader("จำลองสถานการณ์วางแผนภาษี")
    st.markdown("ทดลองปรับตัวเลขการลงทุนเพื่อดูความเปลี่ยนแปลงของภาษี โดยไม่กระทบกับข้อมูลหลัก")

    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        sim_thaiesg = st.slider("สมมติว่าซื้อกองทุน Thai ESG เพิ่ม (บาท)", 0, 300000, 0, step=5000)
    with sim_col2:
        sim_rmf = st.slider("สมมติว่าซื้อกองทุน RMF เพิ่ม (บาท)", 0, 500000, 0, step=5000)

    sim_deductions = total_deductions + sim_thaiesg + sim_rmf
    sim_result = calculate_tax_breakdown(total_income, deduct_expense, sim_deductions, wht_paid)

    sim_diff = sim_result['tax_difference']
    original_diff = result['tax_difference']
    tax_saved = original_diff - sim_diff

    st.markdown(f"**ผลการจำลอง:** หากคุณลงทุนเพิ่มเติมจำนวน {sim_thaiesg + sim_rmf:,.0f} บาท")
    st.success(f"จะสามารถประหยัดภาษีได้เพิ่มขึ้น: {tax_saved:,.0f} บาท")
    st.markdown(f"**ภาระภาษีสุทธิในสถานการณ์จำลอง:** {'ชำระเพิ่ม' if sim_diff > 0 else 'ได้รับคืน'} {abs(sim_diff):,.0f} บาท")

# TAB 3: อัปโหลดเอกสาร
with tab3:
    st.subheader("ระบบอัปโหลดเอกสารประกอบ (50 ทวิ)")
    st.markdown("อัปโหลดหนังสือรับรองการหักภาษี ณ ที่จ่าย เพื่อเก็บบันทึกหรือเตรียมดึงข้อมูลอัตโนมัติ")
    
    uploaded_file = st.file_uploader("ลากและวางไฟล์ หรือคลิกเพื่อเลือกไฟล์ (รองรับ PDF, JPG, PNG)", type=['pdf', 'jpg', 'png'])

    if uploaded_file is not None:
        st.success(f"อัปโหลดไฟล์ '{uploaded_file.name}' เสร็จสมบูรณ์")