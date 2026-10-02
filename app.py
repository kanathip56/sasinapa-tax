import streamlit as st

# 1. ตั้งค่าหน้าเว็บให้คลีน ซ่อนเมนู และจัดกึ่งกลางเพื่อมือถือ
st.set_page_config(
    page_title="Sasinapa - โปรแกรมคำนวณ VAT",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. ปรับแต่ง CSS จำลองหน้าตาแบบ iTAX
st.markdown("""
    <style>
    /* ซ่อนเมนู Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* ปรับพื้นหลังแอปให้เป็นสีเทาอ่อน สบายตา */
    .stApp { background-color: #f7f9fc; }
    
    /* ตกแต่งช่องกรอกตัวเลขให้ใหญ่เหมือนเครื่องคิดเลข (iTAX Style) */
    div[data-baseweb="input"] {
        background-color: #ffffff;
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 5px;
    }
    div[data-baseweb="input"] input {
        font-size: 32px !important;
        font-weight: bold;
        text-align: right;
        color: #1e293b;
    }
    
    /* กล่องใบเสร็จสรุปผล (Receipt Card) */
    .receipt-card {
        background: #ffffff;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin-top: 10px;
        margin-bottom: 40px;
    }
    .receipt-row {
        display: flex;
        justify-content: space-between;
        font-size: 16px;
        color: #64748b;
        padding: 12px 0;
        border-bottom: 1px dashed #e2e8f0;
    }
    .receipt-row:last-child {
        border-bottom: none;
    }
    .receipt-row.total {
        font-weight: bold;
        color: #0f172a;
        font-size: 18px;
        border-bottom: 2px solid #cbd5e1;
    }
    .receipt-row.net {
        font-weight: bold;
        color: #059669; /* สีเขียว Sasinapa */
        font-size: 24px;
        padding-top: 20px;
    }
    .receipt-value {
        font-family: monospace; /* ฟอนต์ตัวเลขให้อ่านง่าย */
        font-size: 18px;
    }
    .receipt-value.net-value {
        font-size: 28px;
    }
    .receipt-value.deduct {
        color: #ef4444; /* สีแดงสำหรับยอดหัก */
    }
    
    /* Sasinapa Footer */
    .sasinapa-footer {
        background-color: #1e293b;
        color: #f8fafc;
        padding: 40px 20px;
        margin-top: 40px;
        border-radius: 16px 16px 0 0;
        font-family: sans-serif;
    }
    .sasinapa-footer h2 { color: #f8fafc; font-weight: 700; margin-bottom: 10px; }
    .sasinapa-footer h4 { color: #f8fafc; font-weight: bold; margin-top: 20px; margin-bottom: 10px; font-size: 16px; }
    .sasinapa-footer p { color: #94a3b8; font-size: 14px; line-height: 1.6; }
    .sasinapa-footer a { color: #94a3b8; text-decoration: none; display: block; margin-bottom: 8px; }
    .sasinapa-footer a:hover { color: #f8fafc; }
    </style>
""", unsafe_allow_html=True)

# ----------------- ส่วนหัว -----------------
st.markdown("<h2 style='text-align: center; color: #0f172a; font-weight: bold; margin-bottom: 5px;'>โปรแกรมคำนวณ VAT</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 30px;'>คำนวณภาษีมูลค่าเพิ่ม 7% และหัก ณ ที่จ่าย (Sasinapa)</p>", unsafe_allow_html=True)

# ----------------- ส่วนรับข้อมูล -----------------
# 1. ประเภท VAT
vat_type = st.radio("รูปแบบราคา", ["ราคานี้ยังไม่รวม VAT", "ราคานี้รวม VAT แล้ว"], horizontal=True)

# 2. ช่องกรอกเงินขนาดใหญ่ (ว่างเปล่าตอนเริ่มต้น)
amount = st.number_input("จำนวนเงิน (บาท)", min_value=0.0, value=None, placeholder="0.00", step=1000.0)
val_amount = amount if amount else 0.0

# 3. หัก ณ ที่จ่าย
wht_options = {
    "ไม่มีหัก ณ ที่จ่าย (0%)": 0,
    "ค่าขนส่ง (1%)": 1,
    "ค่าโฆษณา (2%)": 2,
    "ค่าบริการ / รับจ้าง (3%)": 3,
    "ค่าเช่า / นักแสดง (5%)": 5
}
wht_choice = st.selectbox("อัตราภาษีหัก ณ ที่จ่าย", list(wht_options.keys()), index=3) # ตั้งค่าเริ่มต้นที่ 3% เหมือน iTAX
wht_rate = wht_options[wht_choice]

# ----------------- ระบบประมวลผล & การแสดงผลแบบใบเสร็จ -----------------
if val_amount > 0:
    # คำนวณ VAT
    if vat_type == "ราคานี้ยังไม่รวม VAT":
        base = val_amount
        vat = base * 0.07
        total_with_vat = base + vat
    else: # ราคานี้รวม VAT แล้ว
        base = val_amount * 100 / 107
        vat = val_amount - base
        total_with_vat = val_amount
    
    # คำนวณหัก ณ ที่จ่าย
    wht = base * (wht_rate / 100)
    net = total_with_vat - wht

    # สร้างโครงสร้าง HTML สำหรับใบเสร็จ
    html_receipt = f"""
    <div class="receipt-card">
        <div class="receipt-row">
            <span>มูลค่าสินค้า/บริการ</span>
            <span class="receipt-value">฿ {base:,.2f}</span>
        </div>
        <div class="receipt-row">
            <span>ภาษีมูลค่าเพิ่ม (VAT 7%)</span>
            <span class="receipt-value">฿ {vat:,.2f}</span>
        </div>
        <div class="receipt-row total">
            <span>ราคารวมภาษีมูลค่าเพิ่ม</span>
            <span class="receipt-value">฿ {total_with_vat:,.2f}</span>
        </div>
        <div class="receipt-row">
            <span>หัก ณ ที่จ่าย ({wht_rate}%)</span>
            <span class="receipt-value deduct">- ฿ {wht:,.2f}</span>
        </div>
        <div class="receipt-row net">
            <span>ยอดชำระสุทธิ</span>
            <span class="receipt-value net-value">฿ {net:,.2f}</span>
        </div>
    </div>
    """
    st.markdown(html_receipt, unsafe_allow_html=True)
else:
    # กรณีที่ยังไม่ได้กรอกตัวเลข
    html_empty = """
    <div class="receipt-card" style="text-align: center; color: #94a3b8; padding: 50px 20px;">
        กรุณาระบุจำนวนเงินเพื่อดูผลการคำนวณ
    </div>
    """
    st.markdown(html_empty, unsafe_allow_html=True)

# ----------------- Footer Sasinapa -----------------
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