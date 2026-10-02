# tax_calculator.py

def calculate_tax_breakdown(total_income, expense, deductions, wht_paid=0):
    net_income = max(0, total_income - expense - deductions)
    
    # ขั้นบันไดภาษีเงินได้บุคคลธรรมดาของไทย
    brackets = [
        (150000, 0.00),   # 0 - 150,000 : ยกเว้น
        (150000, 0.05),   # 150,001 - 300,000 : 5%
        (200000, 0.10),   # 300,001 - 500,000 : 10%
        (250000, 0.15),   # 500,001 - 750,000 : 15%
        (250000, 0.20),   # 750,001 - 1,000,000 : 20%
        (1000000, 0.25),  # 1,000,001 - 2,000,000 : 25%
        (3000000, 0.30),  # 2,000,001 - 5,000,000 : 30%
        (float('inf'), 0.35) # เกิน 5,000,000 : 35%
    ]
    
    tax_total = 0.0
    remaining_income = net_income
    highest_rate = 0.0
    
    for bracket_size, rate in brackets:
        if remaining_income <= 0:
            break
        taxable_amount = min(remaining_income, bracket_size)
        if taxable_amount > 0:
            highest_rate = rate
        tax_total += taxable_amount * rate
        remaining_income -= bracket_size
        
    tax_difference = tax_total - wht_paid
    
    return {
        "net_income": net_income,
        "tax_total": tax_total,
        "highest_rate_percent": int(highest_rate * 100),
        "tax_difference": tax_difference
    }

def get_optimizer_tip(marginal_rate):
    if marginal_rate == 0:
        return "ฐานภาษีปัจจุบันของคุณคือ 0% (ได้รับการยกเว้นภาษี) ยังไม่จำเป็นต้องซื้อกองทุน Thai ESG หรือ RMF เพิ่มเพื่อลดภาษี"
    
    saved_per_10k = 10000 * (marginal_rate / 100)
    return (
        f"ฐานภาษีสูงสุดของคุณอยู่ที่ **{marginal_rate}%** "
        f"ทุกๆ การซื้อกองทุนลดหย่อน (Thai ESG / RMF) เพิ่ม 10,000 บาท "
        f"คุณจะประหยัดภาษีและได้เงินคืนทันที **{saved_per_10k:,.0f} บาท** "
        f"(Instant Tax ROI: {marginal_rate}%)"
    )