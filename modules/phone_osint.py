#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Phone OSINT Module
أدوات البحث المحسنة عن أرقام الهواتف
"""

import os
import re
import aiohttp
import asyncio
import phonenumbers
from phonenumbers import geocoder, carrier, timezone

RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '')
APILAYER_KEY = os.getenv('APILAYER_KEY', '')
NUMVERIFY_KEY = os.getenv('NUMVERIFY_KEY', '')


def clean_phone(phone: str) -> str:
    """تنظيف رقم الهاتف"""
    cleaned = re.sub(r'[^\d+]', '', phone)
    if not cleaned.startswith('+') and len(cleaned) > 10:
        cleaned = '+' + cleaned
    return cleaned


def detect_country(phone: str) -> dict:
    """تحديد الدولة من رقم الهاتف"""
    
    country_codes = {
        '+20': {'name': 'مصر', 'code': 'EG', 'flag': '🇪🇬'},
        '+966': {'name': 'السعودية', 'code': 'SA', 'flag': '🇸🇦'},
        '+971': {'name': 'الإمارات', 'code': 'AE', 'flag': '🇦🇪'},
        '+962': {'name': 'الأردن', 'code': 'JO', 'flag': '🇯🇴'},
        '+961': {'name': 'لبنان', 'code': 'LB', 'flag': '🇱🇧'},
        '+963': {'name': 'سوريا', 'code': 'SY', 'flag': '🇸🇾'},
        '+964': {'name': 'العراق', 'code': 'IQ', 'flag': '🇮🇶'},
        '+965': {'name': 'الكويت', 'code': 'KW', 'flag': '🇰🇼'},
        '+968': {'name': 'عمان', 'code': 'OM', 'flag': '🇴🇲'},
        '+974': {'name': 'قطر', 'code': 'QA', 'flag': '🇶🇦'},
        '+973': {'name': 'البحرين', 'code': 'BH', 'flag': '🇧🇭'},
        '+212': {'name': 'المغرب', 'code': 'MA', 'flag': '🇲🇦'},
        '+213': {'name': 'الجزائر', 'code': 'DZ', 'flag': '🇩🇿'},
        '+216': {'name': 'تونس', 'code': 'TN', 'flag': '🇹🇳'},
        '+218': {'name': 'ليبيا', 'code': 'LY', 'flag': '🇱🇾'},
        '+249': {'name': 'السودان', 'code': 'SD', 'flag': '🇸🇩'},
        '+1': {'name': 'أمريكا/كندا', 'code': 'US', 'flag': '🇺🇸'},
        '+44': {'name': 'بريطانيا', 'code': 'GB', 'flag': '🇬🇧'},
        '+33': {'name': 'فرنسا', 'code': 'FR', 'flag': '🇫🇷'},
        '+49': {'name': 'ألمانيا', 'code': 'DE', 'flag': '🇩🇪'},
        '+90': {'name': 'تركيا', 'code': 'TR', 'flag': '🇹🇷'},
        '+7': {'name': 'روسيا', 'code': 'RU', 'flag': '🇷🇺'},
        '+86': {'name': 'الصين', 'code': 'CN', 'flag': '🇨🇳'},
        '+91': {'name': 'الهند', 'code': 'IN', 'flag': '🇮🇳'},
    }
    
    clean = clean_phone(phone)
    
    for code, info in sorted(country_codes.items(), key=lambda x: -len(x[0])):
        if clean.startswith(code):
            return info
    
    return {'name': 'غير معروف', 'code': 'XX', 'flag': '🏳️'}


async def phone_search(phone: str) -> str:
    """البحث الشامل عن رقم هاتف"""
    
    phone = clean_phone(phone)
    country = detect_country(phone)
    
    text = f"📱 *البحث عن الرقم:* `{phone}`\n\n"
    text += f"{country['flag']} *الدولة:* {country['name']}\n\n"
    
    if RAPIDAPI_KEY:
        url = "https://phone-number-analyzer.p.rapidapi.com/phone-number-in-google-search"
        
        payload = {"number": phone, "region": country['code'].lower()}
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "phone-number-analyzer.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "OK":
                            results = data.get("result", [])
                            if results:
                                text += f"🔍 *نتائج البحث ({len(results)}):*\n\n"
                                for i, item in enumerate(results[:5], 1):
                                    title = item.get("title", "بدون عنوان")
                                    link = item.get("url", "")
                                    text += f"*{i}.* {title}\n🔗 {link}\n\n"
                            else:
                                text += "ℹ️ لم يتم العثور على نتائج في جوجل\n"
        except Exception as e:
            text += f"⚠️ خطأ في البحث: {str(e)}\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "*أوامر إضافية:*\n"
    text += f"• `/verify {phone}` - التحقق من صحة الرقم\n"
    text += f"• `/whatsapp {phone}` - معلومات واتساب\n"
    text += f"• `/ignorant {phone}` - فحص في المنصات\n"
    
    return text


async def whatsapp_osint(phone: str) -> str:
    """جلب معلومات واتساب المحسنة"""
    
    original_phone = phone
    phone = clean_phone(phone).replace('+', '')
    
    text = f"📱 *معلومات واتساب:* `{phone}`\n\n"
    
    try:
        parsed = phonenumbers.parse('+' + phone, None)
        is_valid = phonenumbers.is_valid_number(parsed)
        is_mobile = phonenumbers.number_type(parsed) == 1
        
        country_code = phonenumbers.region_code_for_number(parsed)
        country_name = geocoder.description_for_number(parsed, 'ar')
        if not country_name:
            country_name = geocoder.description_for_number(parsed, 'en')
        carrier_name = carrier.name_for_number(parsed, 'ar')
        if not carrier_name:
            carrier_name = carrier.name_for_number(parsed, 'en')
        
        text += f"📊 *تحليل الرقم:*\n"
        text += f"{'✅' if is_valid else '❌'} الرقم {'صالح' if is_valid else 'غير صالح'}\n"
        text += f"{'📱' if is_mobile else '☎️'} نوع الخط: {'موبايل' if is_mobile else 'ثابت'}\n"
        
        if is_mobile:
            text += f"✅ *يمكن استخدامه مع واتساب*\n\n"
        else:
            text += f"⚠️ *الأرقام الثابتة لا تدعم واتساب عادة*\n\n"
        
        text += f"🌍 *الدولة:* {country_name if country_name else 'غير معروف'}\n"
        text += f"🏳️ *كود الدولة:* {country_code if country_code else 'غير معروف'}\n"
        text += f"📶 *المزود:* {carrier_name if carrier_name else 'غير معروف'}\n\n"
        
    except Exception as e:
        text += f"⚠️ لم يتم التعرف على الرقم\n\n"
    
    if RAPIDAPI_KEY:
        try:
            bizos_url = "https://whatsapp-osint.p.rapidapi.com/bizos"
            bizos_headers = {
                "Content-Type": "application/json",
                "x-rapidapi-key": RAPIDAPI_KEY,
                "x-rapidapi-host": "whatsapp-osint.p.rapidapi.com"
            }
            bizos_payload = {"phone": phone}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(bizos_url, json=bizos_payload, headers=bizos_headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if isinstance(data, list) and len(data) > 0:
                            data = data[0]
                        
                        if isinstance(data, dict) and data:
                            text += "📲 *معلومات واتساب OSINT:*\n"
                            
                            is_business = data.get('isBusiness')
                            if is_business:
                                if is_business == "Not a Business Account":
                                    text += f"💼 *نوع الحساب:* حساب شخصي (ليس تجاري)\n"
                                else:
                                    text += f"💼 *نوع الحساب:* حساب تجاري\n"
                            
                            verified_name = data.get('verifiedName')
                            if verified_name and verified_name != 'null':
                                text += f"✅ *الاسم الموثق:* {verified_name}\n"
                            
                            for key, value in data.items():
                                if value and value not in [None, '', [], {}, 'null'] and key not in ['query', 'isBusiness', 'verifiedName']:
                                    if key in ['exists', 'registered', 'isRegistered', 'onWhatsapp']:
                                        text += f"✅ *مسجل:* {'نعم' if value else 'لا'}\n"
                                    elif key in ['name', 'pushname', 'displayName']:
                                        text += f"👤 *الاسم:* {value}\n"
                                    elif key in ['status', 'about', 'status_text']:
                                        text += f"📝 *الحالة:* {value}\n"
                                    elif key in ['profile_pic', 'picture', 'photo', 'profilePic', 'avatar']:
                                        text += f"🖼 *صورة البروفايل:* {value}\n"
                                    elif key in ['business_name', 'businessName']:
                                        text += f"🏢 *اسم النشاط:* {value}\n"
                                    elif key in ['business_description', 'description']:
                                        text += f"📋 *الوصف:* {value}\n"
                                    elif key in ['category', 'business_category']:
                                        text += f"📂 *التصنيف:* {value}\n"
                                    elif key in ['address', 'location']:
                                        text += f"📍 *العنوان:* {value}\n"
                                    elif key in ['email']:
                                        text += f"📧 *الإيميل:* {value}\n"
                                    elif key in ['website', 'websites', 'url']:
                                        if isinstance(value, list):
                                            value = ', '.join(str(v) for v in value)
                                        text += f"🌐 *الموقع:* {value}\n"
                                    elif key in ['last_seen', 'lastSeen']:
                                        text += f"🕐 *آخر ظهور:* {value}\n"
                                    elif key not in ['phone', 'number', 'jid', 'message', 'success', 'error', 'code']:
                                        if isinstance(value, (str, int, float, bool)):
                                            text += f"ℹ️ *{key}:* {value}\n"
                            
                            text += "\n"
                    elif response.status == 403:
                        text += "⚠️ الـ API غير مفعل - تحتاج الاشتراك في RapidAPI\n\n"
                    elif response.status == 429:
                        text += "⚠️ تم تجاوز الحد المسموح من الطلبات\n\n"
                    else:
                        resp_text = await response.text()
                        text += f"⚠️ خطأ ({response.status}): {resp_text[:100]}\n\n"
        except Exception as e:
            text += f"⚠️ خطأ في WhatsApp OSINT: {str(e)}\n\n"
        
        apis = [
            {
                'host': 'whatsapp-data1.p.rapidapi.com',
                'url': f'https://whatsapp-data1.p.rapidapi.com/number/{phone}'
            },
            {
                'host': 'whatsapp-profile.p.rapidapi.com',
                'url': f'https://whatsapp-profile.p.rapidapi.com/get-profile?phone={phone}'
            }
        ]
        
        for api in apis:
            try:
                headers = {
                    "x-rapidapi-key": RAPIDAPI_KEY,
                    "x-rapidapi-host": api['host']
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(api['url'], headers=headers, timeout=30) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if isinstance(data, dict):
                                exists = data.get('exists', data.get('status') == 'success')
                                text += f"✅ *الحالة:* {'مسجل في واتساب' if exists else 'غير مسجل'}\n"
                                
                                if data.get('name'):
                                    text += f"👤 *الاسم:* {data.get('name')}\n"
                                
                                if data.get('status'):
                                    text += f"📝 *الحالة:* {data.get('status')}\n"
                                
                                if data.get('profile_pic') or data.get('picture'):
                                    pic = data.get('profile_pic') or data.get('picture')
                                    text += f"🖼 *صورة البروفايل:* {pic}\n"
                                
                                if data.get('is_business') or data.get('isBusiness'):
                                    text += f"💼 *حساب تجاري:* نعم\n"
                                    
                                    if data.get('business_name'):
                                        text += f"🏢 *اسم النشاط:* {data.get('business_name')}\n"
                                    if data.get('business_description'):
                                        text += f"📋 *الوصف:* {data.get('business_description')}\n"
                                
                                if data.get('about'):
                                    text += f"ℹ️ *نبذة:* {data.get('about')}\n"
                                
                                return text
            except:
                continue
    
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "🔗 *للتحقق يدوياً:*\n"
    text += f"• افتح واتساب وابحث عن: `+{phone}`\n"
    text += f"• أو استخدم الرابط: wa.me/{phone}\n"
    
    return text


async def phone_verify(phone: str) -> str:
    """التحقق المحسن من صحة رقم الهاتف باستخدام مكتبة phonenumbers"""
    
    phone = clean_phone(phone)
    country = detect_country(phone)
    
    text = f"📱 *التحقق من الرقم:* `{phone}`\n\n"
    text += f"{country['flag']} *الدولة المتوقعة:* {country['name']}\n\n"
    
    try:
        parsed = phonenumbers.parse(phone, None)
        
        is_valid = phonenumbers.is_valid_number(parsed)
        is_possible = phonenumbers.is_possible_number(parsed)
        
        if is_valid:
            text += f"✅ *الرقم صالح*\n\n"
        elif is_possible:
            text += f"⚠️ *الرقم محتمل صحته*\n\n"
        else:
            text += f"❌ *الرقم غير صالح*\n\n"
        
        country_code = phonenumbers.region_code_for_number(parsed)
        country_name = geocoder.description_for_number(parsed, 'ar')
        if not country_name:
            country_name = geocoder.description_for_number(parsed, 'en')
        
        carrier_name = carrier.name_for_number(parsed, 'ar')
        if not carrier_name:
            carrier_name = carrier.name_for_number(parsed, 'en')
        
        timezones = timezone.time_zones_for_number(parsed)
        
        international_format = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        national_format = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
        e164_format = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        
        number_type = phonenumbers.number_type(parsed)
        type_names = {
            0: "خط ثابت",
            1: "موبايل",
            2: "ثابت أو موبايل",
            3: "رقم مجاني",
            4: "رقم مدفوع",
            5: "مكالمات مشتركة",
            6: "VoIP",
            7: "رقم شخصي",
            8: "بيجر",
            9: "UAN",
            10: "غير معروف"
        }
        line_type = type_names.get(number_type, "غير معروف")
        
        text += f"🌍 *الدولة:* {country_name if country_name else 'غير معروف'}\n"
        text += f"🏳️ *كود الدولة:* {country_code if country_code else 'غير معروف'}\n"
        text += f"📞 *الصيغة الدولية:* `{international_format}`\n"
        text += f"📱 *الصيغة المحلية:* `{national_format}`\n"
        text += f"🔢 *صيغة E164:* `{e164_format}`\n"
        text += f"📶 *المزود:* {carrier_name if carrier_name else 'غير معروف'}\n"
        text += f"📱 *نوع الخط:* {line_type}\n"
        
        if timezones:
            text += f"🕐 *المنطقة الزمنية:* {', '.join(timezones)}\n"
        
        text += f"\n✅ *صالح:* {'نعم' if is_valid else 'لا'}\n"
        text += f"📊 *محتمل:* {'نعم' if is_possible else 'لا'}\n"
        
    except phonenumbers.phonenumberutil.NumberParseException as e:
        text += f"❌ *خطأ في تحليل الرقم:* {str(e)}\n"
        text += "\n💡 تأكد من إدخال الرقم بالصيغة الدولية (مثال: +201234567890)\n"
    except Exception as e:
        text += f"⚠️ *خطأ:* {str(e)}\n"
    
    return text


async def ignorant_check(phone: str) -> str:
    """فحص رقم الهاتف في المنصات المختلفة (مستوحى من Ignorant)"""
    
    phone = clean_phone(phone).replace('+', '')
    
    text = f"📱 *فحص الرقم في المنصات:* `{phone}`\n\n"
    
    platforms_found = []
    platforms_not_found = []
    
    async with aiohttp.ClientSession() as session:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            snapchat_url = f"https://accounts.snapchat.com/accounts/signup"
            async with session.post(snapchat_url, 
                                   data={'phone': phone}, 
                                   headers=headers, 
                                   timeout=10) as resp:
                if resp.status == 200:
                    result = await resp.text()
                    if 'phone_number_taken' in result.lower():
                        platforms_found.append("Snapchat")
                    else:
                        platforms_not_found.append("Snapchat")
        except:
            pass
        
        try:
            amazon_url = "https://www.amazon.com/ap/forgotpassword"
            async with session.post(amazon_url,
                                   data={'email': phone},
                                   headers=headers,
                                   timeout=10) as resp:
                if resp.status == 200:
                    result = await resp.text()
                    if 'We cannot find an account' not in result:
                        platforms_found.append("Amazon")
                    else:
                        platforms_not_found.append("Amazon")
        except:
            pass
    
    if platforms_found:
        text += f"✅ *تم العثور في ({len(platforms_found)}):*\n"
        for p in platforms_found:
            text += f"• {p}\n"
        text += "\n"
    
    if platforms_not_found:
        text += f"❌ *غير موجود في ({len(platforms_not_found)}):*\n"
        for p in platforms_not_found:
            text += f"• {p}\n"
    
    text += "\n💡 *منصات للفحص اليدوي:*\n"
    text += "• Instagram (استرداد كلمة المرور)\n"
    text += "• Twitter/X\n"
    text += "• Facebook\n"
    text += "• Telegram\n"
    text += "• Signal\n"
    
    return text


async def phone_reputation(phone: str) -> str:
    """فحص سمعة رقم الهاتف"""
    
    phone = clean_phone(phone)
    
    text = f"🛡️ *فحص سمعة الرقم:* `{phone}`\n\n"
    
    spam_indicators = []
    
    if phone.endswith('0000') or phone.endswith('1234'):
        spam_indicators.append("نمط رقم مشبوه")
    
    if len(spam_indicators) > 0:
        text += "⚠️ *مؤشرات تحذيرية:*\n"
        for indicator in spam_indicators:
            text += f"• {indicator}\n"
    else:
        text += "✅ لم يتم العثور على مؤشرات سلبية\n"
    
    text += "\n🔗 *للفحص المتقدم:*\n"
    text += f"• https://www.truecaller.com/\n"
    text += f"• https://www.whocalledme.com/\n"
    text += f"• https://www.scamcallfighters.com/\n"
    
    return text
