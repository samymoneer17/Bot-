#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🆔 National ID Analysis Module
تحليل الرقم القومي المصري
"""

GOVERNORATES = {
    "01": "القاهرة",
    "02": "الإسكندرية",
    "03": "بورسعيد",
    "04": "السويس",
    "11": "دمياط",
    "12": "الدقهلية",
    "13": "الشرقية",
    "14": "القليوبية",
    "15": "كفر الشيخ",
    "16": "الغربية",
    "17": "المنوفية",
    "18": "البحيرة",
    "19": "الإسماعيلية",
    "21": "الجيزة",
    "22": "بني سويف",
    "23": "الفيوم",
    "24": "المنيا",
    "25": "أسيوط",
    "26": "سوهاج",
    "27": "قنا",
    "28": "أسوان",
    "29": "الأقصر",
    "31": "البحر الأحمر",
    "32": "الوادي الجديد",
    "33": "مطروح",
    "34": "شمال سيناء",
    "35": "جنوب سيناء",
    "88": "خارج الجمهورية",
}


def analyze_egyptian_id(nid: str) -> str:
    """تحليل الرقم القومي المصري"""
    
    nid = nid.strip()
    
    if not nid.isdigit():
        return "❌ الرقم القومي يجب أن يحتوي على أرقام فقط"
    
    if len(nid) != 14:
        return f"❌ الرقم القومي يجب أن يتكون من 14 رقم\nالطول الحالي: {len(nid)}"
    
    text = f"🆔 *تحليل الرقم القومي*\n\n"
    text += f"📍 *الرقم:* `{nid}`\n\n"
    
    century = nid[0]
    if century == "2":
        century_text = "1900-1999"
        birth_century = 1900
    elif century == "3":
        century_text = "2000-2099"
        birth_century = 2000
    else:
        return "❌ رقم القرن غير صالح"
    
    birth_year = birth_century + int(nid[1:3])
    birth_month = nid[3:5]
    birth_day = nid[5:7]
    
    try:
        month_int = int(birth_month)
        day_int = int(birth_day)
        
        if month_int < 1 or month_int > 12:
            return "❌ شهر الميلاد غير صالح"
        if day_int < 1 or day_int > 31:
            return "❌ يوم الميلاد غير صالح"
    except:
        return "❌ تاريخ الميلاد غير صالح"
    
    birth_date = f"{birth_day}/{birth_month}/{birth_year}"
    text += f"📅 *تاريخ الميلاد:* {birth_date}\n"
    
    gov_code = nid[7:9]
    governorate = GOVERNORATES.get(gov_code, "غير معروف")
    text += f"🏛️ *المحافظة:* {governorate} ({gov_code})\n"
    
    serial = nid[9:13]
    text += f"🔢 *الرقم التسلسلي:* {serial}\n"
    
    gender_digit = int(nid[12])
    gender = "ذكر" if gender_digit % 2 == 1 else "أنثى"
    text += f"⚧️ *الجنس:* {gender}\n"
    
    check_digit = nid[13]
    text += f"✅ *رقم التحقق:* {check_digit}\n"
    
    from datetime import datetime
    current_year = datetime.now().year
    age = current_year - birth_year
    text += f"\n🎂 *العمر التقريبي:* {age} سنة"
    
    return text
