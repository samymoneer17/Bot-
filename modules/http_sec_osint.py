#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔒 HTTP Security Check Module
وحدة فحص أمان روابط HTTP والتأكد من بروتوكولات التشفير
"""

import httpx
import logging

logger = logging.getLogger(__name__)

async def http_security_check(url: str) -> str:
    """فحص أمان رابط HTTP"""
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            response = await client.get(url)
            
        text = f"🔒 *نتائج فحص أمان HTTP:* `{url}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━\n"
        
        # SSL Check
        is_https = url.startswith('https://')
        text += f"• *التشفير (HTTPS):* {'✅ مدعوم' if is_https else '❌ غير مشفر (HTTP)'}\n"
        
        # Status Code
        text += f"• *كود الحالة:* `{response.status_code}`\n"
        
        # Security Headers
        headers = response.headers
        sec_headers = {
            "Strict-Transport-Security": "HSTS",
            "Content-Security-Policy": "CSP",
            "X-Frame-Options": "X-Frame",
            "X-Content-Type-Options": "No-Sniff",
            "Referrer-Policy": "Referrer"
        }
        
        text += "\n🛡️ *رؤوس الأمان (Security Headers):*\n"
        for header, label in sec_headers.items():
            status = "✅" if header in headers else "❌"
            text += f"• {label}: {status}\n"
            
        # Server Info
        server = headers.get("Server", "غير معروف")
        text += f"\n🖥️ *معلومات السيرفر:* `{server}`\n"
        
        return text
    except Exception as e:
        logger.error(f"Error in http_security_check: {e}")
        return f"❌ خطأ أثناء فحص أمان HTTP: {str(e)}"
