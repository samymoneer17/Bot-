"""
Google OSINT Module - مستوحى من GHunt
ميزات البحث والتحقيق في حسابات Google
"""

import aiohttp
from aiohttp import ClientTimeout
import asyncio
import re
import os
from dotenv import load_dotenv
import json

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")


async def google_email_osint(email: str) -> str:
    """البحث عن معلومات حساب Google من الإيميل"""
    
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        return "❌ صيغة البريد الإلكتروني غير صحيحة"
    
    text = f"🔍 *تحليل حساب Google*\n\n"
    text += f"📧 *الإيميل:* `{email}`\n\n"
    
    is_gmail = email.lower().endswith('@gmail.com')
    text += f"📌 *نوع الحساب:* {'Gmail' if is_gmail else 'Google Workspace / حساب آخر'}\n"
    
    if is_gmail:
        username = email.split('@')[0]
        text += f"👤 *اسم المستخدم:* `{username}`\n"
        
        dot_variations = []
        clean_username = username.replace('.', '')
        text += f"🔄 *الاسم بدون نقاط:* `{clean_username}@gmail.com`\n"
        
        plus_example = f"{username}+anything@gmail.com"
        text += f"➕ *مثال Plus addressing:* `{plus_example}`\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "🔗 *روابط محتملة للحساب:*\n\n"
    
    if is_gmail:
        username = email.split('@')[0].replace('.', '')
        text += f"📺 *YouTube:* https://www.youtube.com/@{username}\n"
        text += f"📸 *Google Photos:* (يتطلب رابط مشترك)\n"
        text += f"🗺️ *Google Maps:* https://www.google.com/maps/contrib/\n"
        text += f"📝 *Blogger:* https://{username}.blogspot.com\n"
    
    text += f"\n🔍 *Google Search:* https://www.google.com/search?q=\"{email}\"\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "ℹ️ *ملاحظة:* للحصول على معلومات أعمق مثل GAIA ID والخدمات المرتبطة،\n"
    text += "يمكنك استخدام أداة GHunt على جهازك:\n"
    text += "`ghunt email " + email + "`"
    
    return text


async def youtube_channel_osint(channel_input: str) -> str:
    """تحليل قناة يوتيوب - بحث عن معلومات القناة"""
    
    if not RAPIDAPI_KEY:
        return "❌ مفتاح RapidAPI غير متوفر\nيرجى إضافة RAPIDAPI_KEY في الإعدادات"
    
    channel_id = None
    username = None
    
    if 'youtube.com' in channel_input or 'youtu.be' in channel_input:
        if '/channel/' in channel_input:
            match = re.search(r'/channel/([a-zA-Z0-9_-]+)', channel_input)
            if match:
                channel_id = match.group(1)
        elif '/@' in channel_input:
            match = re.search(r'/@([a-zA-Z0-9_-]+)', channel_input)
            if match:
                username = match.group(1)
        elif '/user/' in channel_input:
            match = re.search(r'/user/([a-zA-Z0-9_-]+)', channel_input)
            if match:
                username = match.group(1)
        elif '/c/' in channel_input:
            match = re.search(r'/c/([a-zA-Z0-9_-]+)', channel_input)
            if match:
                username = match.group(1)
    else:
        if channel_input.startswith('UC') and len(channel_input) == 24:
            channel_id = channel_input
        else:
            username = channel_input
    
    api_host = "youtube-v31.p.rapidapi.com"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": api_host
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            if channel_id:
                url = f"https://{api_host}/channels"
                params = {"part": "snippet,statistics,brandingSettings", "id": channel_id}
            else:
                url = f"https://{api_host}/search"
                params = {"q": username, "part": "snippet", "type": "channel", "maxResults": 1}
            
            async with session.get(url, headers=headers, params=params, timeout=ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    items = data.get('items', [])
                    if not items:
                        return f"❌ لم يتم العثور على قناة: `{channel_input}`"
                    
                    if not channel_id:
                        channel_id = items[0].get('snippet', {}).get('channelId') or items[0].get('id', {}).get('channelId')
                        
                        url = f"https://{api_host}/channels"
                        params = {"part": "snippet,statistics,brandingSettings", "id": channel_id}
                        
                        async with session.get(url, headers=headers, params=params, timeout=ClientTimeout(total=30)) as resp2:
                            if resp2.status == 200:
                                data = await resp2.json()
                                items = data.get('items', [])
                    
                    if items:
                        channel = items[0]
                        snippet = channel.get('snippet', {})
                        stats = channel.get('statistics', {})
                        branding = channel.get('brandingSettings', {}).get('channel', {})
                        
                        text = f"📺 *تحليل قناة YouTube*\n\n"
                        text += f"🆔 *Channel ID:* `{channel.get('id', 'غير معروف')}`\n"
                        text += f"📛 *اسم القناة:* {snippet.get('title', 'غير معروف')}\n"
                        
                        if snippet.get('customUrl'):
                            text += f"🔗 *الرابط المخصص:* youtube.com/{snippet.get('customUrl')}\n"
                        
                        text += f"\n📊 *الإحصائيات:*\n"
                        text += f"  👥 المشتركين: {format_number(stats.get('subscriberCount', 0))}\n"
                        text += f"  📹 عدد الفيديوهات: {format_number(stats.get('videoCount', 0))}\n"
                        text += f"  👁️ إجمالي المشاهدات: {format_number(stats.get('viewCount', 0))}\n"
                        
                        if snippet.get('publishedAt'):
                            created = snippet.get('publishedAt', '')[:10]
                            text += f"\n📅 *تاريخ الإنشاء:* {created}\n"
                        
                        if snippet.get('country'):
                            text += f"🌍 *البلد:* {snippet.get('country')}\n"
                        
                        if snippet.get('description'):
                            desc = snippet.get('description', '')[:200]
                            text += f"\n📝 *الوصف:*\n{desc}...\n"
                        
                        if branding.get('keywords'):
                            text += f"\n🏷️ *الكلمات المفتاحية:* {branding.get('keywords')[:100]}...\n"
                        
                        text += f"\n🔗 *رابط القناة:*\nhttps://www.youtube.com/channel/{channel.get('id')}"
                        
                        return text
                    else:
                        return f"❌ لم يتم العثور على معلومات القناة"
                else:
                    return f"❌ خطأ في الاتصال: {response.status}"
                    
    except asyncio.TimeoutError:
        return "❌ انتهت مهلة الاتصال"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"


async def google_drive_osint(drive_url: str) -> str:
    """تحليل رابط Google Drive للملفات المشتركة"""
    
    file_id = None
    
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]+)',
        r'/document/d/([a-zA-Z0-9_-]+)',
        r'/spreadsheets/d/([a-zA-Z0-9_-]+)',
        r'/presentation/d/([a-zA-Z0-9_-]+)',
        r'/folders/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, drive_url)
        if match:
            file_id = match.group(1)
            break
    
    if not file_id:
        if len(drive_url) > 20 and re.match(r'^[a-zA-Z0-9_-]+$', drive_url):
            file_id = drive_url
        else:
            return "❌ لم يتم التعرف على رابط Google Drive\nيرجى إدخال رابط صالح"
    
    text = f"📁 *تحليل رابط Google Drive*\n\n"
    text += f"🆔 *File/Folder ID:* `{file_id}`\n\n"
    
    if '/document/' in drive_url or 'docs.google.com' in drive_url:
        file_type = "📄 Google Docs"
    elif '/spreadsheets/' in drive_url or 'sheets.google.com' in drive_url:
        file_type = "📊 Google Sheets"
    elif '/presentation/' in drive_url or 'slides.google.com' in drive_url:
        file_type = "📽️ Google Slides"
    elif '/folders/' in drive_url:
        file_type = "📂 Google Drive Folder"
    elif '/file/' in drive_url:
        file_type = "📎 Google Drive File"
    else:
        file_type = "📁 Google Drive Item"
    
    text += f"📌 *نوع الملف:* {file_type}\n\n"
    
    text += "🔗 *روابط مفيدة:*\n"
    text += f"  • *عرض:* https://drive.google.com/file/d/{file_id}/view\n"
    text += f"  • *تحميل:* https://drive.google.com/uc?id={file_id}&export=download\n"
    text += f"  • *معاينة:* https://drive.google.com/file/d/{file_id}/preview\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "ℹ️ *ملاحظة:* لاستخراج معلومات المالك والبيانات الوصفية،\n"
    text += "استخدم أداة GHunt على جهازك:\n"
    text += f"`ghunt drive {drive_url}`"
    
    return text


async def wifi_geolocate(bssid: str) -> str:
    """تحديد الموقع الجغرافي من BSSID الخاص بشبكة WiFi"""
    
    bssid = bssid.upper().replace('-', ':')
    
    bssid_regex = r'^([0-9A-F]{2}:){5}[0-9A-F]{2}$'
    if not re.match(bssid_regex, bssid):
        return "❌ صيغة BSSID غير صحيحة\nالصيغة الصحيحة: XX:XX:XX:XX:XX:XX"
    
    text = f"📡 *تحديد موقع WiFi*\n\n"
    text += f"🔍 *BSSID:* `{bssid}`\n\n"
    
    vendor_prefix = bssid[:8]
    text += f"🏭 *Vendor Prefix:* `{vendor_prefix}`\n"
    
    text += "\n🔗 *خدمات البحث عن الموقع:*\n\n"
    text += f"1️⃣ *WiGLE:*\nhttps://wigle.net/search?netid={bssid}\n\n"
    text += f"2️⃣ *OpenWiFiMap:*\nhttps://openwifimap.net/\n\n"
    text += f"3️⃣ *MAC Vendor Lookup:*\nhttps://macvendors.com/?q={vendor_prefix}\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "ℹ️ *ملاحظة:* لتحديد الموقع الدقيق باستخدام Google API،\n"
    text += "استخدم أداة GHunt على جهازك:\n"
    text += f"`ghunt geolocate {bssid}`"
    
    return text


async def google_search_dork(query: str, dork_type: str = "general") -> str:
    """بحث Google المتقدم (Google Dorking)"""
    
    dorks = {
        "email": f'"{query}" site:linkedin.com OR site:facebook.com OR site:twitter.com',
        "documents": f'"{query}" filetype:pdf OR filetype:doc OR filetype:xls',
        "social": f'"{query}" site:facebook.com OR site:instagram.com OR site:twitter.com OR site:linkedin.com',
        "leaks": f'"{query}" site:pastebin.com OR site:ghostbin.com OR site:hastebin.com',
        "general": f'"{query}"'
    }
    
    search_query = dorks.get(dork_type, dorks["general"])
    encoded_query = search_query.replace(' ', '+').replace('"', '%22')
    
    text = f"🔍 *Google Dorking*\n\n"
    text += f"🎯 *الهدف:* `{query}`\n"
    text += f"📂 *نوع البحث:* {dork_type}\n\n"
    
    text += "🔗 *روابط البحث:*\n\n"
    
    text += f"1️⃣ *بحث عام:*\nhttps://www.google.com/search?q=\"{query}\"\n\n"
    text += f"2️⃣ *بحث الصور:*\nhttps://www.google.com/search?tbm=isch&q=\"{query}\"\n\n"
    text += f"3️⃣ *بحث المستندات:*\nhttps://www.google.com/search?q=\"{query}\"+filetype:pdf+OR+filetype:doc\n\n"
    text += f"4️⃣ *السوشيال ميديا:*\nhttps://www.google.com/search?q=\"{query}\"+site:linkedin.com+OR+site:facebook.com\n\n"
    text += f"5️⃣ *التسريبات:*\nhttps://www.google.com/search?q=\"{query}\"+site:pastebin.com\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "💡 *نصائح Google Dorking:*\n"
    text += "• `site:` للبحث في موقع محدد\n"
    text += "• `filetype:` للبحث عن نوع ملف\n"
    text += "• `inurl:` للبحث في الروابط\n"
    text += "• `intitle:` للبحث في عناوين الصفحات"
    
    return text


def format_number(num):
    """تنسيق الأرقام الكبيرة"""
    try:
        num = int(num)
        if num >= 1000000000:
            return f"{num/1000000000:.1f}B"
        elif num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        return str(num)
    except:
        return str(num)
