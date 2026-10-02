import streamlit as st
import pandas as pd
import plotly.express as px
from tax_calculator import calculate_tax_breakdown, get_optimizer_tip

# 1. ตั้งค่าหน้าเว็บ ซ่อน Sidebar และตั้งเป็นแบบ Centered เพื่อให้อ่านง่ายบนมือถือ
st.set_page_config(
    page_title="Sasinapa - ระบบคำนวณภาษี",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. ปรับแต่ง CSS ลบเมนูรกๆ ออก, ทำ Footer แบบ iTAX, และปรับฟอนต์ให้คลีน
st.markdown("""
    <style>
    /* ซ่อนเมนูแฮมเบอร์เกอร์และ Footer ของ Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ปรับแต่งช่องกรอกข้อมูลให้ใหญ่และกดง่ายบนมือถือ */
    div[data-baseweb="input"] {
        border-radius: 8px;
    }
    
    /* สไตล์สำหรับ Footer แบบ Sasinapa (อ้างอิงจากต้นฉบับสีเขียวเข้ม) */
    .sasinapa-footer {
        background-color: #2E4B40;
        color: #FFFFFF;
        padding: 40px 20px;
        margin-top: 60px;
        border-radius: 10px 10px 0 0;
        font-family: sans-serif;
    }
    .sasinapa-footer h2 {
        color: #FFFFFF;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .sasinapa-footer h4 {
        color: #FFFFFF;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        font-size: 16px;
    }
    .sasinapa-footer p {
        color: #B0C4B1;
        font-size: 14px;
        line-height: 1.6;
    }
    .sasinapa-footer a {
        color: #B0C4B1;
        text-decoration: none;
        display: block;
        margin-bottom: 8px;
    }
    .sasinapa-footer a:hover {
        color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- ส่วนหัวของเว็บ -----------------
st.title("ระบบคำนวณภาษี Sasinapa")
st.markdown("กรอกตัวเลขรายได้ของคุณ ระบบจะคำนวณภาษีให้ทันที (ไม่ต้องมีตัวเลขตั้งต้น พิมพ์ง่ายบนมือถือ)")

# ----------------- ย้ายช่องกรอกข้อมูลมาไว้ตรงกลาง (ไม่ใช้ Sidebar) -----------------
st.subheader("1. ข้อมูลรายได้ (บาท)")
# ใช้ value=None และ placeholder เพื่อให้ช่องว่างเปล่าตอนเริ่ม พิมพ์บนมือถือได้เลยไม่ต้องกดลบ
salary_input = st.number_input("เงินเดือนรวมทั้งปี", min_value=0, value=None, placeholder="เช่น 600000", step=10000)
bonus_input = st.number_input("โบนัสและเงินพิเศษ", min_value=0, value=None, placeholder="เช่น 50000", step=5000)
other_input = st.number_input("รายได้อื่นๆ", min_value=0, value=None, placeholder="0", step=5000)
wht_input = st.number_input("ภาษีหัก ณ ที่จ่ายสะสม (ถ้ามี)", min_value=0, value=None, placeholder="0", step=1000)

# แปลงค่า None เป็น 0 เพื่อนำไปคำนวณ
salary_yearly = salary_input if salary_input else 0
bonus_yearly = bonus_input if bonus_input else 0
other_income = other_input if other_input else 0
wht_paid = wht_input if wht_input else 0

total_income = salary_yearly + bonus_yearly + other_income
deduct_expense = min(total_income * 0.5, 100000)

st.markdown("---")
st.subheader("2. ข้อมูลค่าลดหย่อน (บาท)")
personal_deduction = 60000
sso_input = st.number_input("เงินสมทบประกันสังคม", min_value=0, max_value=9000, value=None, placeholder="สูงสุด 9000")
thaiesg_input = st.number_input("กองทุน Thai ESG", min_value=0, max_value=300000, value=None, placeholder="0")
rmf_input = st.number_input("กองทุน RMF", min_value=0, max_value=500000, value=None, placeholder="0")

sso = sso_input if sso_input else 0
thai_esg = thaiesg_input if thaiesg_input else 0
rmf = rmf_input if rmf_input else 0

total_deductions = personal_deduction + sso + thai_esg + rmf

# ----------------- ส่วนแสดงผล -----------------
st.markdown("---")
st.subheader("📊 ภาระภาษีเบื้องต้น")

# เรียกใช้ฟังก์ชันคำนวณ
result = calculate_tax_breakdown(total_income, deduct_expense, total_deductions, wht_paid)

# แสดงผลแบบกล่องขนาดใหญ่
col1, col2 = st.columns(2)
col1.metric("รายได้รวมทั้งปี", f"{total_income:,.0f} บาท")
col2.metric("เงินได้สุทธิ", f"{result['net_income']:,.0f} บาท")

col3, col4 = st.columns(2)
col3.metric("อัตราภาษีสูงสุด", f"{result['highest_rate_percent']}%")

diff = result["tax_difference"]
if diff > 0:
    col4.metric("ภาษีที่ต้องชำระเพิ่ม", f"{diff:,.0f} บาท")
else:
    col4.metric("ภาษีที่ได้รับคืน", f"{abs(diff):,.0f} บาท")

st.info(get_optimizer_tip(result["highest_rate_percent"]))

# ----------------- Footer แบบ Sasinapa -----------------
footer_html = """
<div class="sasinapa-footer">
    <div style="display: flex; flex-wrap: wrap; gap: 30px;">
        <div style="flex: 2; min-width: 250px;">
            <h2>Sasinapa</h2>
            <p>Sasinapa เกิดจากความเชื่อว่าผู้เสียภาษี คือฮีโร่ตัวจริงของประเทศนี้ เราจึงพัฒนาเทคโนโลยีที่ทำให้ภาษีเป็นเรื่องง่ายที่สุดสำหรับทุกคน เพราะนี่คือสิ่งที่ผู้เสียภาษีสมควรได้รับ</p>
        </div>
        <div style="flex: 1; min-width: 150px;">
            <h4>บุคคลธรรมดา</h4>
            <a href="#">คำนวณภาษี / วางแผนภาษี</a>
            <a href="#">บัญชีธนาคารเพื่อ e-commerce</a>
            
            <h4>บริษัท / ห้างหุ้นส่วน</h4>
            <a href="#">จดทะเบียนบริษัท</a>
            <a href="#">โปรแกรมเงินเดือน</a>
        </div>
        <div style="flex: 1; min-width: 150px;">
            <h4>ลดหย่อนภาษี</h4>
            <a href="#">ประกันชีวิต</a>
            <a href="#">ประกันออมทรัพย์</a>
            <a href="#">ประกันสุขภาพ</a>
            <a href="#">กองทุน RMF / Thai ESG</a>
        </div>
    </div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)