#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔗 URL Tools Module
وحدة أدوات الروابط وكشف الروابط المختصرة
"""

import httpx
import logging

logger = logging.getLogger(__name__)

async def unshorten_url(url: str) -> str:
    """كشف الرابط الحقيقي المختصر وفحصه أمنياً"""
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
        
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.head(url)
            final_url = str(response.url)
            status_code = response.status_code
            
            # محاولة جلب بعض المعلومات الأمنية البسيطة
            headers = response.headers
            server = headers.get("Server", "غير معروف")
            content_type = headers.get("Content-Type", "غير معروف")
            
            text = "🔗 *نتائج كشف الرابط المختصر:*\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━\n"
            text += f"📍 *الرابط الحقيقي:* `{final_url}`\n\n"
            
            text += "📊 *معلومات تقنية:*\n"
            text += f"• كود الاستجابة: `{status_code}`\n"
            text += f"• السيرفر: `{server}`\n"
            text += f"• نوع المحتوى: `{content_type}`\n"
            
            # فحص أمني بسيط (يمكن توسيعه لاحقاً)
            is_suspicious = False
            suspicious_keywords = ["login", "verify", "secure", "bank", "update", "account"]
            if any(keyword in final_url.lower() for keyword in suspicious_keywords):
                is_suspicious = True
                
            if is_suspicious:
                text += "\n⚠️ *تنبيه أمني:* الرابط يحتوي على كلمات قد تشير إلى محاولة احتيال (Phishing). يرجى الحذر!"
            
            text += f"\n🔍 [فحص الرابط في VirusTotal](https://www.virustotal.com/gui/search/{final_url.replace('/', '%2F')})"
            
            return text
            
    except Exception as e:
        logger.error(f"Error unshortening URL: {e}")
        return f"❌ فشل كشف الرابط: {str(e)}"
