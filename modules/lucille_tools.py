#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔮 Lucille Data Extraction & Analysis Tools
أدوات لوسيل لاستخراج وتحليل البيانات
"""

import aiohttp
import asyncio
import re
import hashlib
import json


async def email_extract(domain: str) -> str:
    """استخراج الإيميلات من موقع"""
    try:
        text = f"📧 *استخراج الإيميلات:* `{domain}`\n\n"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://{domain}", timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Email regex
                    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                    emails = set(re.findall(email_pattern, html))
                    
                    if emails:
                        text += f"✅ *عدد الإيميلات:* {len(emails)}\n\n"
                        for email in list(emails)[:20]:
                            text += f"  • {email}\n"
                        
                        if len(emails) > 20:
                            text += f"\n_... و {len(emails) - 20} إيميل آخر_"
                    else:
                        text += "❌ لم يتم استخراج إيميلات"
                    
                    return text
                else:
                    return f"❌ خطأ: {response.status}"
    except Exception as e:
        return f"❌ خطأ: {str(e)[:100]}"


async def phone_extract(domain: str) -> str:
    """استخراج أرقام الهواتف من الموقع"""
    try:
        text = f"📱 *استخراج الأرقام:* `{domain}`\n\n"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://{domain}", timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Phone regex (various formats)
                    phone_patterns = [
                        r'\+\d{1,3}\s?\d{6,14}',
                        r'\d{3}[-.]?\d{3}[-.]?\d{4}',
                        r'(00|\\+)\d{1,3}\s\d{6,14}',
                    ]
                    
                    phones = set()
                    for pattern in phone_patterns:
                        phones.update(re.findall(pattern, html))
                    
                    if phones:
                        text += f"✅ *عدد الأرقام:* {len(phones)}\n\n"
                        for phone in list(phones)[:20]:
                            text += f"  • {phone}\n"
                        
                        if len(phones) > 20:
                            text += f"\n_... و {len(phones) - 20} رقم آخر_"
                    else:
                        text += "❌ لم يتم استخراج أرقام"
                    
                    return text
                else:
                    return f"❌ خطأ: {response.status}"
    except Exception as e:
        return f"❌ خطأ: {str(e)[:100]}"


async def sitemap_analysis(domain: str) -> str:
    """تحليل ملف Sitemap"""
    try:
        text = f"🗺️ *تحليل Sitemap:* `{domain}`\n\n"
        
        sitemap_urls = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemap1.xml',
            '/sitemap.xml.gz',
        ]
        
        async with aiohttp.ClientSession() as session:
            for sitemap_url in sitemap_urls:
                try:
                    async with session.get(f"https://{domain}{sitemap_url}", timeout=10) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            # Extract URLs
                            urls = re.findall(r'<loc>(.*?)</loc>', content)
                            
                            text += f"✅ *وجدت:* {len(urls)} رابط\n\n"
                            text += "*أمثلة:*\n"
                            
                            for url in urls[:10]:
                                text += f"  • {url}\n"
                            
                            if len(urls) > 10:
                                text += f"\n_... و {len(urls) - 10} رابط آخر_"
                            
                            return text
                except:
                    pass
        
        return "❌ لم يتم العثور على sitemap"
    except Exception as e:
        return f"❌ خطأ: {str(e)[:100]}"


async def security_txt(domain: str) -> str:
    """فحص ملف security.txt"""
    try:
        text = f"🔒 *فحص security.txt:* `{domain}`\n\n"
        
        paths = [
            '/.well-known/security.txt',
            '/security.txt',
        ]
        
        async with aiohttp.ClientSession() as session:
            for path in paths:
                try:
                    async with session.get(f"https://{domain}{path}", timeout=10) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            text += f"✅ *وجد على:* `{path}`\n\n"
                            text += "```\n"
                            text += content[:500]
                            text += "\n```"
                            
                            return text
                except:
                    pass
        
        return "❌ لم يتم العثور على security.txt"
    except Exception as e:
        return f"❌ خطأ: {str(e)[:100]}"


async def hash_md5(text_to_hash: str) -> str:
    """تشفير MD5/SHA1/SHA256"""
    try:
        md5 = hashlib.md5(text_to_hash.encode()).hexdigest()
        sha1 = hashlib.sha1(text_to_hash.encode()).hexdigest()
        sha256 = hashlib.sha256(text_to_hash.encode()).hexdigest()
        
        result = f"🔐 *تشفير البيانات*\n\n"
        result += f"📝 *النص:* `{text_to_hash}`\n\n"
        result += f"*MD5:*\n`{md5}`\n\n"
        result += f"*SHA1:*\n`{sha1}`\n\n"
        result += f"*SHA256:*\n`{sha256}`"
        
        return result
    except Exception as e:
        return f"❌ خطأ: {str(e)}"


async def hash_decode(hash_value: str) -> str:
    """فك تشفير MD5 (مكتبة محلية + APIs)"""
    try:
        # قاموس كلمات المرور الشائعة مع MD5
        common_hashes = {
            "5f4dcc3b5aa765d61d8327deb882cf99": "123456",
            "5f4dcc3b5aa765d61d8327deb882cf99": "123456",
            "81dc9bdb52d04dc20036dbd8313ed055": "1234",
            "c4ca4238a0b923820dcc509a6f75849b": "1",
            "c81e728d9d4c2f636f067f89cc14862c": "2",
            "eccbc87e4b5ce2fe28308fd9f2a7baf3": "3",
            "a87ff679a2f3e71d9181a67b7542122c": "4",
            "e4d909c290d0fb1ca068ffaddf22cbd0": "5",
            "1679091c5a880faf6fb5e6087eb1b2dc": "6",
            "6512bd43d9caa6e02c990b0a82652dca": "7",
            "c9f0f895fb98ab9159f51fd0297e236d": "8",
            "45c48cce2e2d7fbdea1afc51c7c6ad26": "9",
            "d41d8cd98f00b204e9800998ecf8427e": "",
            "098f6bcd4621d373cade4e832627b4f6": "test",
            "900150983cd24fb0d6963f7d28e17f72": "password",
            "5ebf245a441a51cd520541b4910b3b56": "admin",
            "0192023a7bbd73250516f069df18b500": "password123",
            "bacb1a3726814d27e6f4a4a714e4a5f8": "admin123",
            "6c7ccc38eaae1869b2a2a0efc69bee00": "123123",
            "827ccb0eea8a706c4c34a16891f84e7b": "12345",
        }
        
        text = f"🔓 *فك التشفير:* `{hash_value[:32]}...`\n\n"
        
        # 1️⃣ البحث في القاموس المحلي أولاً
        if hash_value.lower() in common_hashes:
            return text + f"✅ *النتيجة:* `{common_hashes[hash_value.lower()]}`\n\n_وجدت في القاموس المحلي_"
        
        # 2️⃣ جرب APIs الخارجية
        found = False
        results = []
        
        apis = [
            f"https://api.md5.gromweb.com/?md5={hash_value}&full=true",
            f"https://www.md5online.com/api/query",  # يتطلب POST
        ]
        
        async with aiohttp.ClientSession() as session:
            # جرب API الأول
            try:
                async with session.get(apis[0], timeout=5) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            if data.get('result'):
                                text += f"✅ *النتيجة:* `{data['result']}`"
                                return text
                        except:
                            pass
            except:
                pass
        
        # 3️⃣ إذا لم نجد النتيجة، اقترح خدمات
        text += "ℹ️ *النتيجة غير موجودة في القاعدة المتاحة*\n\n"
        text += "*الخدمات الموثوقة:*\n"
        text += "• [CrackStation](https://crackstation.net)\n"
        text += "• [MD5Online](https://www.md5online.com)\n"
        text += "• [HashKiller](https://www.hashkiller.com)\n"
        text += "• [Reverse MD5](https://md5.gromweb.com)\n\n"
        text += "💡 *ملاحظة:* MD5 غير قابل للعكس رياضياً، لكن يمكن البحث في قواعس البيانات"
        
        return text
    except Exception as e:
        return f"❌ خطأ: {str(e)[:100]}"


async def reverse_dns_lookup(ip: str) -> str:
    """البحث DNS العكسي"""
    try:
        import socket
        
        text = f"🔄 *DNS عكسي:* `{ip}`\n\n"
        
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            text += f"✅ *الاسم:* {hostname}\n"
        except socket.herror:
            text += "❌ لم يتم العثور على اسم مضيف\n"
        
        return text
    except Exception as e:
        return f"❌ خطأ: {str(e)[:100]}"
