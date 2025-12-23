#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📧 Email OSINT Module
أدوات فحص البريد الإلكتروني المحسنة
"""

import os
import re
import asyncio
import aiohttp
from aiohttp import ClientTimeout
import importlib.util

HIBP_API_KEY = os.getenv('HIBP_API_KEY', '')


def is_holehe_available():
    """التحقق من توفر مكتبة holehe"""
    return importlib.util.find_spec("holehe") is not None


def _get_holehe_functions():
    """تحميل جميع وظائف holehe بشكل صحيح"""
    import pkgutil
    import importlib
    import holehe.modules
    from holehe.core import import_submodules
    
    import_submodules(holehe.modules)
    
    all_funcs = []
    for importer, modname, ispkg in pkgutil.walk_packages(
        path=holehe.modules.__path__, 
        prefix='holehe.modules.'
    ):
        try:
            mod = importlib.import_module(modname)
            for name in dir(mod):
                obj = getattr(mod, name)
                if callable(obj) and not name.startswith('_'):
                    if hasattr(obj, '__module__') and 'holehe.modules' in str(obj.__module__):
                        if asyncio.iscoroutinefunction(obj):
                            all_funcs.append(obj)
        except:
            pass
    
    return all_funcs


async def email_check(email: str) -> str:
    """فحص الإيميل باستخدام Holehe المحسن"""
    
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        return "❌ صيغة البريد الإلكتروني غير صحيحة"
    
    if not is_holehe_available():
        return await email_check_manual(email)
    
    try:
        import httpx
        
        holehe_funcs = _get_holehe_functions()
        
        found_sites = []
        checked = 0
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            for func in holehe_funcs:
                try:
                    out = []
                    await func(email, client, out)
                    checked += 1
                    
                    for result in out:
                        if result.get('exists') == True:
                            site_name = result.get('name', func.__name__)
                            found_sites.append(site_name)
                except Exception:
                    continue
        
        if found_sites:
            text = f"📧 *فحص الإيميل:* `{email}`\n\n"
            text += f"✅ *تم العثور في {len(found_sites)} منصة من {checked}:*\n\n"
            
            for site in found_sites[:25]:
                text += f"• {site}\n"
            
            if len(found_sites) > 25:
                text += f"\n... و {len(found_sites) - 25} منصة أخرى"
        else:
            text = f"📧 *فحص الإيميل:* `{email}`\n\n"
            text += f"❌ لم يتم العثور على الإيميل في {checked} منصة"
        
        return text
        
    except Exception as e:
        return await email_check_manual(email)


async def email_check_manual(email: str) -> str:
    """فحص يدوي للإيميل في المنصات الشائعة"""
    
    text = f"📧 *فحص الإيميل:* `{email}`\n\n"
    
    platforms = {
        'Google': f'https://accounts.google.com/_/signin/sl/lookup?hl=en&_reqid=0&email={email}',
        'Microsoft': f'https://login.live.com/GetCredentialType.srf',
        'Twitter': f'https://api.twitter.com/i/users/email_available.json?email={email}',
    }
    
    found = []
    
    async with aiohttp.ClientSession() as session:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        try:
            gravatar_hash = __import__('hashlib').md5(email.lower().encode()).hexdigest()
            gravatar_url = f"https://www.gravatar.com/avatar/{gravatar_hash}?d=404"
            
            async with session.get(gravatar_url, headers=headers, timeout=ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    found.append("Gravatar")
        except:
            pass
        
        try:
            github_url = f"https://api.github.com/search/users?q={email}+in:email"
            async with session.get(github_url, headers=headers, timeout=ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('total_count', 0) > 0:
                        found.append("GitHub")
        except:
            pass
    
    if found:
        text += f"✅ *تم العثور في {len(found)} منصة:*\n\n"
        for platform in found:
            text += f"• {platform}\n"
    else:
        text += "ℹ️ *ملاحظة:* للفحص الشامل، تأكد من تثبيت مكتبة holehe\n"
        text += f"\n🔗 يمكنك التحقق يدوياً:\n"
        text += f"• https://haveibeenpwned.com/\n"
        text += f"• https://epieos.com/\n"
    
    return text


async def breach_check(email: str) -> str:
    """فحص التسريبات للإيميل"""
    
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        return "❌ صيغة البريد الإلكتروني غير صحيحة"
    
    text = f"🔓 *فحص التسريبات:* `{email}`\n\n"
    
    if HIBP_API_KEY:
        try:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            headers = {
                "User-Agent": "OSINT-Hunter-Bot",
                "hibp-api-key": HIBP_API_KEY
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        breaches = await response.json()
                        text += f"⚠️ *تم العثور على {len(breaches)} تسريب:*\n\n"
                        
                        for breach in breaches[:15]:
                            name = breach.get('Name', 'غير معروف')
                            date = breach.get('BreachDate', 'غير معروف')
                            count = breach.get('PwnCount', 0)
                            
                            text += f"• *{name}*\n"
                            text += f"  📅 {date} | 👥 {count:,} حساب\n\n"
                        
                        if len(breaches) > 15:
                            text += f"... و {len(breaches) - 15} تسريب آخر"
                        
                        return text
                    elif response.status == 404:
                        text += "✅ *أخبار جيدة!*\n"
                        text += "لم يتم العثور على هذا الإيميل في أي تسريبات معروفة."
                        return text
                    elif response.status == 401:
                        text += "❌ مفتاح HIBP API غير صالح\n"
                    else:
                        text += f"⚠️ حالة غير متوقعة: {response.status}\n"
        except Exception as e:
            text += f"❌ خطأ في الاتصال: {str(e)}\n"
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://leakcheck.io/api/public?check={email}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            async with session.get(url, headers=headers, timeout=ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('found'):
                        sources = data.get('sources', [])
                        text += f"⚠️ *تم العثور على تسريبات في {len(sources)} مصدر*\n\n"
                        
                        for source in sources[:10]:
                            text += f"• {source.get('name', 'غير معروف')}\n"
                        return text
    except:
        pass
    
    if not HIBP_API_KEY:
        text += "ℹ️ *ملاحظة:* للنتائج الكاملة، أضف مفتاح HIBP_API_KEY\n\n"
        text += "🔗 *تحقق يدوياً:*\n"
        text += "• https://haveibeenpwned.com/\n"
        text += "• https://leakcheck.io/\n"
        text += "• https://dehashed.com/\n"
    
    return text


async def holehe_only_used(email: str) -> str:
    """فحص الإيميل وإظهار المنصات المستخدمة فقط (Holehe Only Used) - متوازي وسريع"""
    
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        return "❌ صيغة البريد الإلكتروني غير صحيحة"
    
    if not is_holehe_available():
        return """❌ *مكتبة Holehe غير متوفرة*

ℹ️ هذه الأداة تتطلب مكتبة holehe للعمل.
استخدم `/email` للفحص البديل."""
    
    try:
        import httpx
        
        holehe_funcs = _get_holehe_functions()
        
        found_sites = []
        not_found_count = 0
        error_count = 0
        checked = 0
        
        semaphore = asyncio.Semaphore(20)
        
        async def check_single(func, client):
            nonlocal checked, not_found_count, error_count
            async with semaphore:
                try:
                    out = []
                    await asyncio.wait_for(func(email, client, out), timeout=10.0)
                    checked += 1
                    
                    results = []
                    for result in out:
                        if result.get('exists') == True:
                            site_name = result.get('name', func.__name__)
                            results.append({
                                'name': site_name,
                                'recovery': result.get('emailrecovery', None),
                                'phoneNumber': result.get('phoneNumber', None)
                            })
                        elif result.get('exists') == False:
                            not_found_count += 1
                    return results
                except asyncio.TimeoutError:
                    error_count += 1
                    return []
                except Exception:
                    error_count += 1
                    return []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            tasks = [check_single(func, client) for func in holehe_funcs]
            results = await asyncio.gather(*tasks)
            
            for result_list in results:
                found_sites.extend(result_list)
        
        text = f"🔍 *Holehe Only Used - المنصات المستخدمة*\n"
        text += f"📧 الإيميل: `{email}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        if found_sites:
            text += f"✅ *تم العثور على {len(found_sites)} منصة مستخدمة:*\n\n"
            
            for i, site in enumerate(found_sites, 1):
                text += f"*{i}.* {site['name']}"
                if site.get('recovery'):
                    text += f"\n   🔑 Recovery: `{site['recovery']}`"
                if site.get('phoneNumber'):
                    text += f"\n   📱 Phone: `{site['phoneNumber']}`"
                text += "\n\n"
            
            text += "━━━━━━━━━━━━━━━━━━━━━━\n"
            text += f"📊 *الإحصائيات:*\n"
            text += f"• ✅ موجود في: {len(found_sites)} منصة\n"
            text += f"• ❌ غير موجود: {not_found_count} منصة\n"
            text += f"• ⚠️ أخطاء: {error_count}\n"
            text += f"• 🔍 إجمالي الفحص: {checked} منصة"
        else:
            text += f"❌ *لم يتم العثور على الإيميل في أي منصة*\n\n"
            text += f"📊 تم فحص {checked} منصة"
        
        return text
        
    except Exception as e:
        return f"❌ خطأ في الفحص: {str(e)}"


async def email_domain_info(email: str) -> str:
    """جلب معلومات دومين الإيميل"""
    
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        return "❌ صيغة البريد الإلكتروني غير صحيحة"
    
    domain = email.split('@')[1]
    
    text = f"🌐 *معلومات الدومين:* `{domain}`\n\n"
    
    popular_domains = {
        'gmail.com': ('Google Gmail', '🔵'),
        'yahoo.com': ('Yahoo Mail', '🟣'),
        'hotmail.com': ('Microsoft Hotmail', '🔷'),
        'outlook.com': ('Microsoft Outlook', '🔷'),
        'live.com': ('Microsoft Live', '🔷'),
        'icloud.com': ('Apple iCloud', '⚪'),
        'protonmail.com': ('ProtonMail (مشفر)', '🟢'),
        'proton.me': ('Proton Mail (مشفر)', '🟢'),
        'tutanota.com': ('Tutanota (مشفر)', '🔴'),
        'yandex.com': ('Yandex Mail', '🔴'),
        'mail.ru': ('Mail.ru', '🔵'),
        'aol.com': ('AOL Mail', '🔵'),
        'zoho.com': ('Zoho Mail', '🟡'),
    }
    
    if domain.lower() in popular_domains:
        name, emoji = popular_domains[domain.lower()]
        text += f"{emoji} *المزود:* {name}\n"
        text += f"✅ *دومين موثوق*\n"
    else:
        text += f"🏢 *دومين خاص/مؤسسة*\n"
        text += f"📧 *الدومين:* {domain}\n"
    
    try:
        import socket
        mx_records = []
        try:
            answers = socket.getaddrinfo(domain, None)
            text += f"✅ *الدومين نشط*\n"
        except:
            text += f"❌ *الدومين غير نشط*\n"
    except:
        pass
    
    return text
