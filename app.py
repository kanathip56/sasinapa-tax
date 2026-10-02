import streamlit as st
import pandas as pd
from tax_calculator import calculate_tax_breakdown, get_optimizer_tip

# 1. ตั้งค่าหน้าเว็บให้รองรับทั้ง PC และ Mobile
st.set_page_config(
    page_title="Sasinapa Tax - วางแผนภาษี",
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. ปรับแต่ง CSS ให้คลีนแบบ Finnomena / iTAX
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    div[data-baseweb="input"] { border-radius: 8px; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
        font-size: 16px;
    }
    
    /* สไตล์สำหรับการ์ดประกัน */
    .ins-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    .ins-title { font-size: 20px; font-weight: bold; color: #0f172a; margin-bottom: 5px;}
    .ins-company { font-size: 14px; color: #64748b; margin-bottom: 15px; }
    .ins-highlight { color: #059669; font-weight: bold; }
    .ins-btn {
        background-color: #0f172a;
        color: white;
        padding: 10px 15px;
        text-align: center;
        border-radius: 8px;
        text-decoration: none;
        display: block;
        margin-top: 10px;
        font-weight: bold;
    }
    .ins-btn:hover { background-color: #334155; color: white; }
    </style>
""", unsafe_allow_html=True)

# ----------------- ส่วนหัว -----------------
st.title("ระบบคำนวณและวางแผนภาษี Sasinapa")
st.markdown("เครื่องมือประเมินภาษีแบบครบวงจร พร้อมเลือกซื้อประกันเพื่อลดหย่อนภาษี")
st.divider()

# ----------------- สร้างเมนูหลัก 4 แท็บ -----------------
main_tab1, main_tab2, main_tab3, main_tab4 = st.tabs([
    "🧮 คำนวณภาษีบุคคลธรรมดา", 
    "🏢 ประเมินภาษีธุรกิจ (SME)", 
    "🛒 ช็อปปิ้งประกันลดหย่อน",
    "📚 แหล่งความรู้ & ลิงก์"
])

# ==========================================
# แท็บที่ 1: ภาษีบุคคลธรรมดา
# ==========================================
with main_tab1:
    col_input, col_result = st.columns([1, 1.2], gap="large")

    with col_input:
        st.subheader("1. ข้อมูลรายได้ (บาท)")
        salary = st.number_input("เงินเดือนรวมทั้งปี", min_value=0, value=None, placeholder="เช่น 600000", step=10000)
        bonus = st.number_input("โบนัสและเงินพิเศษ", min_value=0, value=None, placeholder="เช่น 50000", step=5000)
        other_inc = st.number_input("รายได้อื่นๆ", min_value=0, value=None, placeholder="0", step=5000)
        wht = st.number_input("ภาษีหัก ณ ที่จ่ายสะสม", min_value=0, value=None, placeholder="0", step=1000)

        st.markdown("---")
        st.subheader("2. ข้อมูลค่าลดหย่อน (บาท)")
        sso = st.number_input("ประกันสังคม (สูงสุด 9,000)", min_value=0, max_value=9000, value=None, placeholder="0")
        thaiesg = st.number_input("กองทุน Thai ESG", min_value=0, max_value=300000, value=None, placeholder="0")
        rmf = st.number_input("กองทุน RMF", min_value=0, max_value=500000, value=None, placeholder="0")

    total_income = (salary or 0) + (bonus or 0) + (other_inc or 0)
    wht_paid = (wht or 0)
    deduct_expense = min(total_income * 0.5, 100000)
    total_deductions = 60000 + (sso or 0) + (thaiesg or 0) + (rmf or 0)

    with col_result:
        st.subheader("สรุปภาระภาษีของคุณ")
        if total_income > 0:
            result = calculate_tax_breakdown(total_income, deduct_expense, total_deductions, wht_paid)
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
                
            st.info(get_optimizer_tip(result["highest_rate_percent"]))
            
            sub_tab1, sub_tab2 = st.tabs(["รายละเอียดการคำนวณ", "จำลองลดหย่อนเพิ่ม (What-If)"])
            with sub_tab1:
                df = pd.DataFrame({
                    "รายการ": ["เงินได้พึงประเมิน", "หัก ค่าใช้จ่าย", "หัก ค่าลดหย่อนรวม", "เงินได้สุทธิ", "ภาษีที่คำนวณได้", "หัก ภาษีที่จ่ายล่วงหน้า", "สรุปยอดสุทธิ"],
                    "จำนวนเงิน (บาท)": [
                        f"{total_income:,.2f}", f"{deduct_expense:,.2f}", f"{total_deductions:,.2f}", 
                        f"{result['net_income']:,.2f}", f"{result['tax_total']:,.2f}", f"{wht_paid:,.2f}", 
                        f"{abs(diff):,.2f} ({'จ่ายเพิ่ม' if diff > 0 else 'ได้คืน'})"
                    ]
                })
                st.dataframe(df, use_container_width=True, hide_index=True)
                
            with sub_tab2:
                sim_thaiesg = st.slider("สมมติว่าซื้อ Thai ESG เพิ่ม (บาท)", 0, 300000, 0, step=5000)
                if sim_thaiesg > 0:
                    sim_deduct = total_deductions + sim_thaiesg
                    sim_result = calculate_tax_breakdown(total_income, deduct_expense, sim_deduct, wht_paid)
                    sim_diff = sim_result['tax_difference']
                    st.success(f"คุณจะประหยัดภาษีเพิ่มขึ้น: {result['tax_difference'] - sim_diff:,.0f} บาท")
        else:
            st.caption("กรุณาระบุรายได้ เพื่อดูผลการประเมินภาษี")

# ==========================================
# แท็บที่ 2: ภาษีธุรกิจ (SME)
# ==========================================
with main_tab2:
    st.subheader("🏢 ประเมินภาษีเงินได้นิติบุคคล (สำหรับ SME)")
    st.markdown("เงื่อนไข SME: ทุนจดทะเบียนไม่เกิน 5 ล้านบาท และรายได้ทั้งปีไม่เกิน 30 ล้านบาท")
    c_input, c_result = st.columns([1, 1.2], gap="large")
    with c_input:
        net_profit = st.number_input("กำไรสุทธิประจำปี (บาท)", min_value=0, value=None, placeholder="เช่น 1500000", step=100000)
        profit = net_profit if net_profit else 0
    with c_result:
        if profit <= 300000:
            corp_tax, rate_text = 0, "ยกเว้นภาษี"
        elif profit <= 3000000:
            corp_tax, rate_text = (profit - 300000) * 0.15, "15%"
        else:
            corp_tax, rate_text = ((3000000 - 300000) * 0.15) + ((profit - 3000000) * 0.20), "20%"
            
        if profit > 0:
            st.metric("ฐานอัตราภาษีของคุณ", rate_text)
            st.metric("ภาษีธุรกิจที่ต้องชำระ", f"{corp_tax:,.2f} บาท")
        else:
            st.caption("กรุณาระบุกำไรสุทธิ เพื่อดูผลประเมิน")

# ==========================================
# แท็บที่ 3: ช็อปปิ้งประกัน (Shop iTAX Style)
# ==========================================
with main_tab3:
    st.subheader("ค้นหาแผนประกันลดหย่อนภาษีที่เหมาะกับคุณ")
    
    col_filter, col_items = st.columns([1, 2.5], gap="large")
    
    # ด้านซ้าย: ตัวกรอง (Filters)
    with col_filter:
        st.markdown("#### ตัวกรอง (Filters)")
        ins_gender = st.radio("เพศ", ["ชาย", "หญิง"], horizontal=True)
        ins_age = st.number_input("อายุ", min_value=1, max_value=80, value=35)
        ins_budget = st.number_input("งบประมาณเบี้ยประกัน (บาท/ปี)", value=50000, step=5000)
        ins_type = st.selectbox("เป้าหมายหลัก", ["เน้นออมเงิน (สะสมทรัพย์)", "เน้นความคุ้มครอง", "ลดหย่อนหลังเกษียณ (บำนาญ)"])
        ins_period = st.selectbox("ระยะเวลาชำระเบี้ย", ["จ่ายสั้น (1-5 ปี)", "จ่ายปานกลาง (6-10 ปี)", "จ่ายระยะยาว (10 ปีขึ้นไป)"])
        
        st.button("ค้นหาแผนประกัน", use_container_width=True, type="primary")

    # ด้านขวา: แสดงการ์ดผลลัพธ์ประกัน (Mock Data)
    with col_items:
        st.markdown("#### ผลการค้นหา (แนะนำสำหรับคุณ)")
        
        # ตัวอย่างแผนที่ 1
        html_card1 = f"""
        <div class="ins-card">
            <div class="ins-title">Sasinapa SaveMax 10/5 ⭐️</div>
            <div class="ins-company">โดย บริษัท ศศินภา ประกันชีวิต จำกัด (มหาชน)</div>
            <p>✔ จ่ายเบี้ยสั้นเพียง <b>5 ปี</b> คุ้มครองยาว <b>10 ปี</b><br>
            ✔ รับเงินคืนทุกปี ปีละ <span class="ins-highlight">5%</span><br>
            ✔ ลดหย่อนภาษีได้สูงสุด 100,000 บาท/ปี</p>
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed #e2e8f0; padding-top: 10px;">
                <div>
                    <span style="font-size: 12px; color: #64748b;">เบี้ยประกันอ้างอิง</span><br>
                    <span style="font-size: 20px; font-weight: bold;">฿ {ins_budget:,.0f} <span style="font-size: 14px; font-weight: normal;">/ ปี</span></span>
                </div>
                <a href="#" class="ins-btn">ดูรายละเอียด</a>
            </div>
        </div>
        """
        st.markdown(html_card1, unsafe_allow_html=True)

        # ตัวอย่างแผนที่ 2
        html_card2 = f"""
        <div class="ins-card">
            <div class="ins-title">Sasinapa Pension 85/5 (บำนาญลดหย่อนได้)</div>
            <div class="ins-company">โดย บริษัท ศศินภา ประกันชีวิต จำกัด (มหาชน)</div>
            <p>✔ จ่ายเบี้ยเพียง <b>5 ปี</b> รับบำนาญยาวถึงอายุ <b>85 ปี</b><br>
            ✔ เหมาะสำหรับวางแผนเกษียณ รับบำนาญ <span class="ins-highlight">15%</span> ต่อปี<br>
            ✔ ลดหย่อนภาษี (หมวดบำนาญ) ได้สูงสุด 200,000 บาท/ปี</p>
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed #e2e8f0; padding-top: 10px;">
                <div>
                    <span style="font-size: 12px; color: #64748b;">เบี้ยประกันอ้างอิง</span><br>
                    <span style="font-size: 20px; font-weight: bold;">฿ {ins_budget:,.0f} <span style="font-size: 14px; font-weight: normal;">/ ปี</span></span>
                </div>
                <a href="#" class="ins-btn">ดูรายละเอียด</a>
            </div>
        </div>
        """
        st.markdown(html_card2, unsafe_allow_html=True)

# ==========================================
# แท็บที่ 4: แหล่งความรู้
# ==========================================
with main_tab4:
    st.markdown("#### ตัวช่วยและแหล่งความรู้ในการบริหารภาษี")
    with st.expander("📈 หุ้น (Stocks) และภาษี"):
        st.write("- กำไรจากการขายหุ้น (Capital Gain): ยกเว้นภาษีในตลาด SET\n- เงินปันผล (Dividend): หัก ณ ที่จ่าย 10% (ขอเครดิตภาษีคืนได้)")
    with st.expander("🥇 ทองคำ (Gold)"):
        st.write("- ทองคำแท่ง/รูปพรรณ: กำไรจากการขายส่วนตัวยกเว้นภาษี")
    with st.expander("📊 กองทุนรวม (Mutual Funds)"):
        st.write("- Thai ESG / RMF / SSF สำหรับลดหย่อนภาษี")
    with st.expander("📰 อัปเดตข่าวภาษีและลิงก์อื่นๆ"):
        st.write("- [ยื่นแบบภาษีออนไลน์ กรมสรรพากร](https://efiling.rd.go.th/)\n- [ตรวจสอบ e-Tax Invoice](https://etax.rd.go.th/)")

st.divider()

# ----------------- Footer Sasinapa -----------------
st.markdown("#### Sasinapa")
f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
with f_col1:
    st.markdown("<span style='color: #6c757d; font-size: 14px;'>Sasinapa เกิดจากความเชื่อว่าผู้เสียภาษี คือฮีโร่ตัวจริงของประเทศนี้ เราจึงพัฒนาเทคโนโลยีที่ทำให้ภาษีเป็นเรื่องง่ายที่สุดสำหรับทุกคน เพราะนี่คือสิ่งที่ผู้เสียภาษีสมควรได้รับ</span>", unsafe_allow_html=True)
with f_col2:
    st.markdown("**บุคคลธรรมดา**\n<br><span style='color: #6c757d; font-size: 14px;'>คำนวณภาษี / วางแผนภาษี<br>บัญชีธนาคารเพื่อ e-commerce</span>", unsafe_allow_html=True)
with f_col3:
    st.markdown("**ลดหย่อนภาษี**\n<br><span style='color: #6c757d; font-size: 14px;'>ประกันชีวิต<br>กองทุน RMF / Thai ESG</span>", unsafe_allow_html=True)