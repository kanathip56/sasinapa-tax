# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from tax_calculator import calculate_tax_breakdown, get_optimizer_tip

st.set_page_config(
    page_title="SmartTax TH - ระบบวางแผนภาษีอัจฉริยะ",
    page_icon="💸",
    layout="wide"
)

st.title("💸 SmartTax TH: ระบบคำนวณและวางแผนภาษีบุคคลธรรมดา")
st.caption("ระบบคำนวณและจำลองผลตอบแทนการลดหย่อนภาษีอัตโนมัติ")

# --- แถบด้านข้างสำหรับกรอกข้อมูล ---
st.sidebar.header("📝 1. ข้อมูลรายได้ (Income)")
salary_monthly = st.sidebar.number_input("เงินเดือน (บาท/เดือน):", min_value=0, value=45000, step=1000)
bonus_yearly = st.sidebar.number_input("โบนัสทั้งปี (บาท):", min_value=0, value=50000, step=5000)
other_income = st.sidebar.number_input("รายได้เสริม / ฟรีแลนซ์ (บาท):", min_value=0, value=0, step=2000)
wht_paid = st.sidebar.number_input("ภาษีหัก ณ ที่จ่ายสะสม (บาท):", min_value=0, value=12000, step=500)

total_income = (salary_monthly * 12) + bonus_yearly + other_income
deduct_expense = min(total_income * 0.5, 100000)  # หักค่าใช้จ่าย 50% สูงสุด 100,000

st.sidebar.header("🎯 2. ข้อมูลลดหย่อน (Deductions)")
personal_deduction = 60000
sso = st.sidebar.number_input("ประกันสังคมทั้งปี (สูงสุด 9,000):", min_value=0, max_value=9000, value=9000)
thai_esg = st.sidebar.number_input("กองทุน Thai ESG (สูงสุด 300,000):", min_value=0, max_value=300000, value=20000, step=5000)
rmf = st.sidebar.number_input("กองทุน RMF (สูงสุด 500,000):", min_value=0, max_value=500000, value=10000, step=5000)

total_deductions = personal_deduction + sso + thai_esg + rmf

# คำนวณ
result = calculate_tax_breakdown(total_income, deduct_expense, total_deductions, wht_paid)

# --- ส่วน Dashboard ด้านขวา ---
st.subheader("📊 สรุปภาพรวมภาษีของคุณ")
col1, col2, col3, col4 = st.columns(4)

col1.metric("รายได้รวมทั้งปี", f"{total_income:,.0f} ฿")
col2.metric("เงินได้สุทธิ (หลังหักลดหย่อน)", f"{result['net_income']:,.0f} ฿")
col3.metric("ฐานภาษีสูงสุดของคุณ", f"{result['highest_rate_percent']}%")

diff = result["tax_difference"]
if diff > 0:
    col4.metric("ภาษีที่ต้องชำระเพิ่ม", f"{diff:,.0f} ฿", delta="-ต้องจ่ายเพิ่ม", delta_color="inverse")
else:
    col4.metric("เงินภาษีที่จะได้รับคืน", f"{abs(diff):,.0f} ฿", delta="+ได้เงินคืน", delta_color="normal")

st.divider()

# กล่องคำแนะนำ Optimizer
st.subheader("💡 คำแนะนำการวางแผนภาษี (Tax Optimization Advisor)")
st.info(get_optimizer_tip(result["highest_rate_percent"]))

# ชาร์ตและตาราง
chart_col, table_col = st.columns([1, 1])

with chart_col:
    st.write("**สัดส่วนโครงสร้างรายได้**")
    chart_data = pd.DataFrame({
        "หมวดหมู่": ["ค่าใช้จ่ายที่หักได้", "ค่าลดหย่อนรวม", "เงินได้สุทธิ"],
        "จำนวนเงิน": [deduct_expense, total_deductions, result["net_income"]]
    })
    fig = px.pie(chart_data, values="จำนวนเงิน", names="หมวดหมู่", hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
    st.plotly_chart(fig, use_container_width=True)

with table_col:
    st.write("**ตารางแจกแจงสำหรับกรอกแบบ ภ.ง.ด.91**")
    summary_table = pd.DataFrame({
        "หัวข้อ": [
            "เงินได้พึงประเมินทั้งหมด",
            "หัก: ค่าใช้จ่ายตามกฎหมาย",
            "หัก: ค่าลดหย่อนรวม",
            "เงินได้สุทธิที่นำไปคำนวณ",
            "ภาษีคำนวณทั้งสิ้น",
            "หัก: ภาษีที่จ่ายล่วงหน้าแล้ว",
            "สรุปยอดสุทธิ"
        ],
        "จำนวนเงิน (บาท)": [
            f"{total_income:,.2f}",
            f"{deduct_expense:,.2f}",
            f"{total_deductions:,.2f}",
            f"{result['net_income']:,.2f}",
            f"{result['tax_total']:,.2f}",
            f"{wht_paid:,.2f}",
            f"{'ต้องจ่ายเพิ่ม ' + f'{diff:,.2f}' if diff > 0 else 'ได้คืน ' + f'{abs(diff):,.2f}'}"
        ]
    })
    st.dataframe(summary_table, use_container_width=True, hide_index=True)