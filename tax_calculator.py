def calculate_tax_breakdown(total_income, expense, deductions, wht_paid=0):
    net_income = max(0, total_income - expense - deductions)
    
    brackets = [
        (150000, 0.00),
        (150000, 0.05),
        (200000, 0.10),
        (250000, 0.15),
        (250000, 0.20),
        (1000000, 0.25),
        (3000000, 0.30),
        (float('inf'), 0.35)
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
        return "ฐานภาษีปัจจุบันของคุณคือ 0% (ได้รับการยกเว้นภาษี) ยังไม่มีความจำเป็นต้องลงทุนเพื่อลดหย่อนภาษีเพิ่มเติมในขณะนี้"
    
    saved_per_10k = 10000 * (marginal_rate / 100)
    return (
        f"ฐานภาษีสูงสุดของคุณอยู่ที่ {marginal_rate}% "
        f"หากลงทุนในกองทุนลดหย่อนภาษีเพิ่มเติมทุกๆ 10,000 บาท "
        f"จะสามารถประหยัดภาษีได้ {saved_per_10k:,.0f} บาท "
        f"(คิดเป็นอัตราผลตอบแทนจากการประหยัดภาษี {marginal_rate}%)"
    )