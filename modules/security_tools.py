#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ Security Tools Module
أدوات الأمان والفحص
"""

import aiohttp
import asyncio


async def cloudflare_check(url: str) -> str:
    """فحص إذا كان الموقع يستخدم CloudFlare"""
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                headers = dict(response.headers)
                
                is_cloudflare = False
                cf_headers = []
                
                for header, value in headers.items():
                    header_lower = header.lower()
                    value_lower = value.lower()
                    
                    if 'cloudflare' in value_lower:
                        is_cloudflare = True
                        cf_headers.append(f"{header}: {value}")
                    
                    if header_lower in ['cf-ray', 'cf-cache-status', 'cf-request-id']:
                        is_cloudflare = True
                        cf_headers.append(f"{header}: {value}")
                    
                    if header_lower == 'server' and 'cloudflare' in value_lower:
                        is_cloudflare = True
                        cf_headers.append(f"{header}: {value}")
                
                text = f"🛡️ *فحص CloudFlare*\n\n"
                text += f"🌐 *الموقع:* `{url}`\n\n"
                
                if is_cloudflare:
                    text += "✅ *النتيجة:* الموقع يستخدم CloudFlare\n\n"
                    text += "*الهيدرات المكتشفة:*\n"
                    for h in cf_headers[:5]:
                        text += f"  • `{h}`\n"
                else:
                    text += "❌ *النتيجة:* الموقع لا يستخدم CloudFlare"
                
                return text
                
    except asyncio.TimeoutError:
        return "❌ انتهت مهلة الاتصال"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"


async def shodan_exploits(query: str) -> str:
    """البحث عن ثغرات CVE"""
    
    base_url = "https://cvedb.shodan.io"
    
    try:
        async with aiohttp.ClientSession() as session:
            if query.upper().startswith("CVE-"):
                url = f"{base_url}/cve/{query.upper()}"
                
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        cve = await response.json()
                        
                        text = f"🛡️ *معلومات الثغرة*\n\n"
                        text += f"🆔 *CVE ID:* `{cve.get('id', query)}`\n"
                        text += f"📝 *الوصف:* {cve.get('summary', 'غير متوفر')[:500]}\n"
                        text += f"⚠️ *CVSS:* {cve.get('cvss', 'غير متوفر')}\n"
                        text += f"🔴 *الخطورة:* {cve.get('severity', 'غير متوفر')}\n"
                        
                        if cve.get('exploit'):
                            text += f"💥 *استغلال متوفر:* نعم\n"
                        
                        refs = cve.get('references', [])
                        if refs:
                            text += f"\n🔗 *المراجع:*\n"
                            for ref in refs[:3]:
                                text += f"  • {ref}\n"
                        
                        return text
                    else:
                        return f"❌ لم يتم العثور على الثغرة: {query}"
            else:
                url = f"{base_url}/cves?product={query}"
                
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        cves = data.get('cves', []) if isinstance(data, dict) else data
                        
                        if cves:
                            text = f"🛡️ *ثغرات المنتج:* `{query}`\n\n"
                            text += f"📊 *تم العثور على {len(cves)} ثغرة*\n\n"
                            
                            for cve in cves[:10]:
                                cve_id = cve.get('id') or cve.get('cve_id', 'N/A')
                                severity = cve.get('severity', 'غير معروف')
                                cvss = cve.get('cvss', 'N/A')
                                
                                text += f"• *{cve_id}*\n"
                                text += f"  الخطورة: {severity} | CVSS: {cvss}\n"
                            
                            if len(cves) > 10:
                                text += f"\n... و {len(cves) - 10} ثغرة أخرى"
                            
                            return text
                        else:
                            return f"❌ لم يتم العثور على ثغرات للمنتج: {query}"
                    else:
                        return f"❌ خطأ في البحث: {response.status}"
                        
    except asyncio.TimeoutError:
        return "❌ انتهت مهلة الاتصال"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"
