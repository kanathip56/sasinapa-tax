import streamlit as st
import pandas as pd
from tax_calculator import calculate_tax_breakdown, get_optimizer_tip

# 1. ตั้งค่าหน้าเว็บให้รองรับทั้ง PC (แนวกว้าง) และ Mobile (พับอัตโนมัติ)
st.set_page_config(
    page_title="Sasinapa Tax - วางแผนภาษี",
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. ปรับแต่ง CSS ให้ดูสะอาดตา (สไตล์คล้าย Finnomena)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ปรับช่องกรอกข้อมูลให้คลีน */
    div[data-baseweb="input"] {
        border-radius: 8px;
    }
    
    /* กรอบล้อมรอบส่วนแสดงผล */
    .result-container {
        padding: 20px;
        background-color: #F8F9FA;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- ส่วนหัว -----------------
st.title("ระบบคำนวณและวางแผนภาษี Sasinapa")
st.markdown("ประเมินภาระภาษีเงินได้บุคคลธรรมดา พร้อมคำแนะนำการลดหย่อนที่คุ้มค่าที่สุด")
st.divider()

# ----------------- จัดโครงสร้างแบบ 2 คอลัมน์ (ซ้ายกรอกข้อมูล / ขวาแสดงผล) -----------------
# บนคอมพิวเตอร์จะแบ่ง 40% : 60% ส่วนบนมือถือจะเรียงต่อกันอัตโนมัติ
col_input, col_result = st.columns([1, 1.2], gap="large")

with col_input:
    st.subheader("1. ข้อมูลรายได้ (บาท)")
    # ใช้ value=None เพื่อไม่ให้มีตัวเลขตั้งต้น
    salary = st.number_input("เงินเดือนรวมทั้งปี", min_value=0, value=None, placeholder="เช่น 600000", step=10000)
    bonus = st.number_input("โบนัสและเงินพิเศษ", min_value=0, value=None, placeholder="เช่น 50000", step=5000)
    other_inc = st.number_input("รายได้อื่นๆ", min_value=0, value=None, placeholder="0", step=5000)
    wht = st.number_input("ภาษีหัก ณ ที่จ่ายสะสม", min_value=0, value=None, placeholder="0", step=1000)

    st.markdown("---")
    st.subheader("2. ข้อมูลค่าลดหย่อน (บาท)")
    sso = st.number_input("ประกันสังคม (สูงสุด 9,000)", min_value=0, max_value=9000, value=None, placeholder="0")
    thaiesg = st.number_input("กองทุน Thai ESG", min_value=0, max_value=300000, value=None, placeholder="0")
    rmf = st.number_input("กองทุน RMF", min_value=0, max_value=500000, value=None, placeholder="0")

# ----------------- ระบบประมวลผล -----------------
# แปลงค่า None เป็น 0 เพื่อคำนวณ
total_income = (salary or 0) + (bonus or 0) + (other_inc or 0)
wht_paid = (wht or 0)
deduct_expense = min(total_income * 0.5, 100000)
total_deductions = 60000 + (sso or 0) + (thaiesg or 0) + (rmf or 0)

with col_result:
    st.subheader("สรุปภาระภาษีของคุณ")
    
    if total_income > 0:
        # เรียกใช้ฟังก์ชันจาก tax_calculator.py
        result = calculate_tax_breakdown(total_income, deduct_expense, total_deductions, wht_paid)
        
        # กล่องแสดงตัวเลขขนาดใหญ่
        mc1, mc2 = st.columns(2)
        mc1.metric("รายได้รวมทั้งปี", f"{total_income:,.0f} บาท")
        mc2.metric("เงินได้สุทธิ", f"{result['net_income']:,.0f} บาท")
        
        mc3, mc4 = st.columns(2)
        mc3.metric("อัตราภาษีสูงสุด", f"{result['highest_rate_percent']}%")
        
        diff = result["tax_difference"]
        if diff > 0:
            mc4.metric("ภาษีที่ต้องชำระเพิ่ม", f"{diff:,.0f} บาท")
        else:
            mc4.metric("ภาษีที่ได้รับคืน", f"{abs(diff):,.0f} บาท")
            
        # คำแนะนำ Optimizer
        st.info(get_optimizer_tip(result["highest_rate_percent"]))
        
        # ฟังก์ชันแบ่งแท็บแบบ Finnomena
        tab1, tab2 = st.tabs(["รายละเอียดการคำนวณ", "จำลองลดหย่อนเพิ่ม (What-If)"])
        
        with tab1:
            df = pd.DataFrame({
                "รายการ": ["เงินได้พึงประเมิน", "หัก ค่าใช้จ่าย", "หัก ค่าลดหย่อนรวม", "เงินได้สุทธิ", "ภาษีที่คำนวณได้", "หัก ภาษีที่จ่ายล่วงหน้า", "สรุปยอดสุทธิ"],
                "จำนวนเงิน (บาท)": [
                    f"{total_income:,.2f}", 
                    f"{deduct_expense:,.2f}", 
                    f"{total_deductions:,.2f}", 
                    f"{result['net_income']:,.2f}", 
                    f"{result['tax_total']:,.2f}", 
                    f"{wht_paid:,.2f}", 
                    f"{abs(diff):,.2f} ({'จ่ายเพิ่ม' if diff > 0 else 'ได้คืน'})"
                ]
            })
            st.dataframe(df, use_container_width=True, hide_index=True)
            
        with tab2:
            st.markdown("ทดลองจำลองการลงทุนเพิ่ม เพื่อดูยอดภาษีที่จะประหยัดได้")
            sim_thaiesg = st.slider("สมมติว่าซื้อ Thai ESG เพิ่ม (บาท)", 0, 300000, 0, step=5000)
            
            if sim_thaiesg > 0:
                sim_deduct = total_deductions + sim_thaiesg
                sim_result = calculate_tax_breakdown(total_income, deduct_expense, sim_deduct, wht_paid)
                sim_diff = sim_result['tax_difference']
                saved = result['tax_difference'] - sim_diff
                
                st.success(f"คุณจะประหยัดภาษีเพิ่มขึ้น: {saved:,.0f} บาท")
                st.metric("ภาระภาษีสุทธิใหม่", f"{abs(sim_diff):,.0f} บาท", f"{'ต้องจ่ายเพิ่ม' if sim_diff > 0 else 'ได้รับคืน'}")
            else:
                st.caption("เลื่อนสไลเดอร์เพื่อดูการเปลี่ยนแปลงของภาษี")

    else:
        st.caption("กรุณาระบุรายได้ทางด้านซ้าย (หรือด้านบนหากใช้มือถือ) เพื่อดูผลการประเมินภาษี")

st.divider()

# ----------------- Footer Sasinapa (เขียนด้วย Native Streamlit ป้องกันหน้าเว็บพัง) -----------------
st.markdown("#### Sasinapa")
f_col1, f_col2, f_col3 = st.columns([2, 1, 1])

with f_col1:
    st.markdown("<span style='color: #6c757d; font-size: 14px;'>Sasinapa เกิดจากความเชื่อว่าผู้เสียภาษี คือฮีโร่ตัวจริงของประเทศนี้ เราจึงพัฒนาเทคโนโลยีที่ทำให้ภาษีเป็นเรื่องง่ายที่สุดสำหรับทุกคน เพราะนี่คือสิ่งที่ผู้เสียภาษีสมควรได้รับ</span>", unsafe_allow_html=True)

with f_col2:
    st.markdown("**บุคคลธรรมดา**")
    st.markdown("<span style='color: #6c757d; font-size: 14px;'>คำนวณภาษี / วางแผนภาษี<br><br>บัญชีธนาคารเพื่อ e-commerce</span>", unsafe_allow_html=True)
    st.markdown("<br>**บริษัท / ห้างหุ้นส่วน**", unsafe_allow_html=True)
    st.markdown("<span style='color: #6c757d; font-size: 14px;'>จดทะเบียนบริษัท<br><br>โปรแกรมเงินเดือน</span>", unsafe_allow_html=True)

with f_col3:
    st.markdown("**ลดหย่อนภาษี**")
    st.markdown("<span style='color: #6c757d; font-size: 14px;'>ประกันชีวิต<br><br>ประกันออมทรัพย์<br><br>ประกันสุขภาพ<br><br>กองทุน RMF / Thai ESG</span>", unsafe_allow_html=True)