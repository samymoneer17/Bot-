#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛰️ Advanced IP Geolocation Module
وحدة تحديد الموقع الجغرافي المتقدمة لعنوان IP
"""

import httpx
import logging

logger = logging.getLogger(__name__)

async def ip_geo_lookup(ip: str) -> str:
    """تحديد الموقع الجغرافي لعنوان IP"""
    try:
        # Using ip-api.com (free for non-commercial)
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting,query"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
        if data.get("status") == "fail":
            return f"❌ فشل فحص IP: {data.get('message')}"
            
        text = f"🛰️ *نتائج تحديد موقع IP:* `{ip}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"🌍 *الدولة:* {data.get('country')} ({data.get('countryCode')})\n"
        text += f"📍 *المدينة:* {data.get('city')}, {data.get('regionName')}\n"
        text += f"📮 *الرمز البريدي:* {data.get('zip')}\n"
        text += f"🕒 *التوقيت:* {data.get('timezone')}\n"
        text += f"🏢 *المزود (ISP):* {data.get('isp')}\n"
        text += f"🛡️ *المنظمة:* {data.get('org')}\n"
        text += f"🌐 *ASN:* {data.get('as')}\n"
        
        # Flags
        proxy = "نعم ✅" if data.get("proxy") else "لا ❌"
        hosting = "نعم ✅" if data.get("hosting") else "لا ❌"
        mobile = "نعم ✅" if data.get("mobile") else "لا ❌"
        
        text += f"\n🛡️ *تفاصيل الأمان:*\n"
        text += f"• بروكسي/VPN: {proxy}\n"
        text += f"• سيرفر استضافة: {hosting}\n"
        text += f"• اتصال موبايل: {mobile}\n"
        
        lat = data.get('lat')
        lon = data.get('lon')
        text += f"\n📍 [عرض على خريطة Google](https://www.google.com/maps/search/?api=1&query={lat},{lon})\n"
        
        return text
    except Exception as e:
        logger.error(f"Error in ip_geo_lookup: {e}")
        return f"❌ خطأ أثناء تحديد موقع IP: {str(e)}"
