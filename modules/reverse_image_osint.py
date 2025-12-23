#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Reverse Image Search Module
وحدة البحث العكسي عن الصور
"""

import urllib.parse
import os
import httpx

async def get_reverse_image_links(image_bytes: bytes) -> str:
    """رفع الصورة لخدمة استضافة ثم توليد روابط البحث العكسي"""
    if not image_bytes:
        return "❌ فشل الحصول على بيانات الصورة."

    try:
        # استخدام ImgBB لرفع الصورة (أو أي خدمة أخرى لا تتطلب مفتاح مؤقتاً للتجربة)
        # ملاحظة: يفضل استخدام API Key خاص بالمستخدم في الإنتاج
        api_key = os.getenv("IMGBB_API_KEY")
        if not api_key:
            return "❌ يرجى ضبط `IMGBB_API_KEY` في الإعدادات لتشغيل هذه الميزة بأمان."

        async with httpx.AsyncClient() as client:
            files = {'image': image_bytes}
            response = await client.post(
                f"https://api.imgbb.com/1/upload?key={api_key}",
                files=files
            )
            data = response.json()

        if not data.get("success"):
            return f"❌ فشل رفع الصورة: {data.get('error', {}).get('message', 'خطأ غير معروف')}"

        image_url = data["data"]["url"]
        encoded_url = urllib.parse.quote(image_url, safe='')
        
        google_url = f"https://lens.google.com/uploadbyurl?url={encoded_url}"
        yandex_url = f"https://yandex.com/images/search?rpt=imageview&url={encoded_url}"
        bing_url = f"https://www.bing.com/images/searchbyimage?cbir=sbi&imgurl={encoded_url}"
        tineye_url = f"https://tineye.com/search?url={encoded_url}"
        
        text = "🔍 *نتائج البحث العكسي الآمن:*\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "تم رفع الصورة بشكل آمن والبحث عنها في المحركات العالمية:\n\n"
        text += f"• [Google Lens]({google_url})\n"
        text += f"• [Yandex Images]({yandex_url})\n"
        text += f"• [Bing Visual Search]({bing_url})\n"
        text += f"• [TinEye Search]({tineye_url})\n"
        text += "\n✅ *تم حماية توكن البوت بنجاح.*"
        
        return text
    except Exception as e:
        return f"❌ حدث خطأ أثناء الرفع: {str(e)}"
