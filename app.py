import streamlit as st
import pandas as pd
from tax_calculator import calculate_tax_breakdown, get_optimizer_tip

# 1. ตั้งค่าหน้าเว็บให้รองรับทั้ง PC และ Mobile
st.set_page_config(
    page_title="Sasinapa Tax - วางแผนภาษี",
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. ปรับแต่ง CSS ให้คลีนแบบ Finnomena
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    div[data-baseweb="input"] {
        border-radius: 8px;
    }
    
    /* ตกแต่งแท็บหลักให้ดูโดดเด่น */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
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
    </style>
""", unsafe_allow_html=True)

# ----------------- ส่วนหัว -----------------
st.title("ระบบคำนวณและวางแผนภาษี Sasinapa")
st.markdown("เครื่องมือประเมินภาษีแบบครบวงจร พร้อมแหล่งความรู้เรื่องการลงทุนเพื่อลดหย่อนภาษี")
st.divider()

# ----------------- สร้างเมนูหลัก 3 แท็บ -----------------
main_tab1, main_tab2, main_tab3 = st.tabs([
    "🧮 คำนวณภาษีบุคคลธรรมดา", 
    "🏢 ประเมินภาษีธุรกิจ (SME)", 
    "📚 แหล่งความรู้ & ตัวช่วยลดหย่อน"
])

# ==========================================
# แท็บที่ 1: ภาษีบุคคลธรรมดา (ฟังก์ชันเดิมที่สมบูรณ์แล้ว)
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

    # ประมวลผล
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
        # คำนวณภาษี SME: กำไร 0-3 แสน = ยกเว้น | 3 แสน-3 ล้าน = 15% | เกิน 3 ล้าน = 20%
        if profit <= 300000:
            corp_tax = 0
            rate_text = "ยกเว้นภาษี"
        elif profit <= 3000000:
            corp_tax = (profit - 300000) * 0.15
            rate_text = "15%"
        else:
            corp_tax = ((3000000 - 300000) * 0.15) + ((profit - 3000000) * 0.20)
            rate_text = "20%"
            
        if profit > 0:
            st.metric("ฐานอัตราภาษีของคุณ", rate_text)
            st.metric("ภาษีธุรกิจที่ต้องชำระ", f"{corp_tax:,.2f} บาท")
            st.info("💡 ข้อแนะนำ: การจดทะเบียนเป็นบริษัทช่วยประหยัดภาษีได้มากกว่าบุคคลธรรมดา หากคุณมีกำไรสุทธิเกิน 1 ล้านบาทขึ้นไป")
        else:
            st.caption("กรุณาระบุกำไรสุทธิ เพื่อดูผลประเมิน")

# ==========================================
# แท็บที่ 3: แหล่งความรู้, ข่าวสาร และลิงก์
# ==========================================
with main_tab3:
    st.markdown("#### ตัวช่วยและแหล่งความรู้ในการบริหารภาษี")
    
    with st.expander("📈 หุ้น (Stocks) และภาษี"):
        st.write("""
        - **กำไรจากการขายหุ้น (Capital Gain):** ยกเว้นภาษี หากลงทุนในตลาดหลักทรัพย์แห่งประเทศไทย (SET)
        - **เงินปันผล (Dividend):** ถูกหักภาษี ณ ที่จ่าย 10% (แต่สามารถเลือกนำไปคำนวณรวมปลายปีเพื่อขอ **เครดิตภาษีเงินปันผล** คืนได้ หากฐานภาษีของคุณต่ำ)
        - 🌐 [อ่านเพิ่มเติม: ความรู้เรื่องภาษีหุ้นจาก SET](https://www.set.or.th/)
        """)

    with st.expander("🥇 ทองคำ (Gold)"):
        st.write("""
        - **ทองคำแท่ง/รูปพรรณ:** กำไรจากการขาย "ทองคำจริง" ที่ซื้อไว้เก็งกำไรส่วนตัว **ได้รับการยกเว้นภาษีเงินได้**
        - **กองทุนทองคำ (Gold Mutual Fund):** กำไรจากการขายคืนหน่วยลงทุนจะได้รับการยกเว้นภาษี แต่เงินปันผลจากกองทุนจะถูกหัก 10%
        - 🌐 [เช็คราคาทองคำวันนี้: สมาคมค้าทองคำ](https://www.goldtraders.or.th/)
        """)

    with st.expander("📊 กองทุนรวม (Mutual Funds) สำหรับลดหย่อนภาษี"):
        st.write("""
        - **Thai ESG (กองทุนเพื่อความยั่งยืน):** ลดหย่อนได้สูงสุด 30% ของรายได้ แต่ไม่เกิน 300,000 บาท (ถือครอง 5 ปี นับจากวันที่ซื้อ)
        - **RMF (กองทุนเพื่อการเลี้ยงชีพ):** ลดหย่อนได้สูงสุด 30% ของรายได้ แต่ไม่เกิน 500,000 บาท (ถือจนถึงอายุ 55 ปี)
        - **SSF (กองทุนรวมเพื่อการออม):** ลดหย่อนได้สูงสุด 30% ของรายได้ แต่ไม่เกิน 200,000 บาท (ถือครอง 10 ปีเต็ม)
        - *หมายเหตุ: RMF + SSF + กบข. + ประกันบำนาญ รวมกันต้องไม่เกิน 500,000 บาท*
        - 🌐 [แนะนำกองทุน: Finnomena](https://www.finnomena.com/)
        """)

    with st.expander("🛡️ ประกันชีวิตและสุขภาพ"):
        st.write("""
        - **ประกันชีวิตทั่วไป:** ลดหย่อนได้ตามจริง สูงสุดไม่เกิน 100,000 บาท
        - **ประกันสุขภาพ:** ลดหย่อนได้สูงสุด 25,000 บาท (แต่เมื่อรวมกับประกันชีวิตทั่วไปต้องไม่เกิน 100,000 บาท)
        - **ประกันบำนาญ:** ลดหย่อนได้ 15% ของรายได้ สูงสุด 200,000 บาท
        - 🌐 [ตรวจสอบข้อมูลบริษัทประกัน: คปภ. (OIC)](https://www.oic.or.th/)
        """)
        
    with st.expander("📰 อัปเดตข่าวภาษีและลิงก์อื่นๆ ที่เป็นประโยชน์"):
        st.write("""
        - [ยื่นแบบภาษีออนไลน์ (e-Filing) กรมสรรพากร](https://efiling.rd.go.th/)
        - [ตรวจสอบรายชื่อผู้ประกอบการ e-Tax Invoice](https://etax.rd.go.th/)
        - [อ่านบทความภาษีเข้าใจง่ายจาก iTAX](https://www.itax.in.th/media/)
        - [ติดตามข่าวสารการลงทุน: กรุงเทพธุรกิจ](https://www.bangkokbiznews.com/)
        """)

st.divider()

# ----------------- Footer Sasinapa -----------------
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