#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦅 Argus Advanced Web Reconnaissance Tools
أدوات استطلاع الويب المتقدمة
"""

import aiohttp
import asyncio
import re
from datetime import datetime


async def dns_records(domain: str) -> str:
    """فحص سجلات DNS التفصيلية"""
    try:
        url = f"https://dns.google/resolve?name={domain}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    text = f"📋 *سجلات DNS:* `{domain}`\n\n"
                    
                    if 'Answer' in data:
                        for record in data['Answer'][:10]:
                            text += f"• {record.get('name', domain)}\n"
                            text += f"  Type: {record.get('type', 'A')}\n"
                            text += f"  Data: {record.get('data', 'N/A')}\n\n"
                    else:
                        text += "❌ لم يتم العثور على سجلات"
                    
                    return text
                else:
                    return f"❌ خطأ: {response.status}"
    except Exception as e:
        return f"❌ خطأ: {str(e)[:100]}"


async def ssl_expiry(domain: str) -> str:
    """فحص شهادة SSL وتاريخ انتهائها"""
    try:
        import ssl
        import socket
        
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                text = f"🔐 *معلومات SSL:* `{domain}`\n\n"
                
                if cert:
                    issued = cert.get('notBefore', 'N/A')
                    expires = cert.get('notAfter', 'N/A')
                    subject = dict(x[0] for x in cert.get('subject', []))
                    
                    text += f"📝 *الموضوع:* {subject.get('commonName', 'N/A')}\n"
                    text += f"📅 *صادرة في:* {issued}\n"
                    text += f"⏰ *تنتهي في:* {expires}\n"
                    
                    return text
                else:
                    return "❌ لم يتم الحصول على شهادة SSL"
    except Exception as e:
        return f"❌ خطأ في فحص SSL: {str(e)[:80]}"


async def server_info(domain: str) -> str:
    """معلومات السيرفر والـ Headers"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(f"https://{domain}", timeout=10, allow_redirects=True) as response:
                text = f"🖥 *معلومات السيرفر:* `{domain}`\n\n"
                
                headers = response.headers
                
                if 'Server' in headers:
                    text += f"🔧 *السيرفر:* {headers['Server']}\n"
                
                if 'X-Powered-By' in headers:
                    text += f"⚙️ *تقنية:* {headers['X-Powered-By']}\n"
                
                if 'X-AspNet-Version' in headers:
                    text += f"🔷 *ASP.NET:* {headers['X-AspNet-Version']}\n"
                
                text += f"\n📊 *الحالة:* {response.status}\n"
                
                return text
    except Exception as e:
        return f"❌ خطأ: {str(e)[:100]}"


async def reverse_ip(ip: str) -> str:
    """البحث العكسي عن النطاقات على نفس IP"""
    try:
        url = f"https://api.abuseipdb.com/api/v2/reverse-ip-lookup"
        # Fallback without API key
        text = f"🔄 *البحث العكسي:* `{ip}`\n\n"
        text += "⚠️ يتطلب API Key للحصول على النتائج الكاملة\n"
        text += f"يمكن استخدام مواقع مثل:\n"
        text += f"• whatismyipaddress.com\n"
        text += f"• ipqualityscore.com\n"
        return text
    except Exception as e:
        return f"❌ خطأ: {str(e)[:100]}"


async def cdn_detection(domain: str) -> str:
    """اكتشاف CDN المستخدم"""
    try:
        import socket
        
        text = f"🌐 *اكتشاف CDN:* `{domain}`\n\n"
        
        # Check IP
        try:
            ip = socket.gethostbyname(domain)
            text += f"🔗 *IP:* {ip}\n\n"
        except:
            pass
        
        # Known CDN IPs/patterns
        cdns = {
            'cloudflare': ['104.16', '104.17', '104.18'],
            'fastly': ['23.235', '43.249'],
            'akamai': ['2.16', '2.17'],
            'aws': ['52.', '54.'],
        }
        
        text += "🔍 *الخدمات المحتملة:*\n"
        text += "استخدم أدوات مثل: whatsmydns.net\n"
        
        return text
    except Exception as e:
        return f"❌ خطأ: {str(e)[:100]}"


async def tech_stack(domain: str) -> str:
    """تقنيات الموقع المستخدمة"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://{domain}", timeout=10) as response:
                text = f"🛠 *التقنيات:* `{domain}`\n\n"
                
                html = await response.text()
                
                # Detect common technologies
                techs = {
                    'WordPress': 'wp-content',
                    'Joomla': 'components/com_',
                    'Drupal': '/sites/all/',
                    'jQuery': 'jquery',
                    'Bootstrap': 'bootstrap',
                    'React': 'react',
                    'Vue': 'vue',
                    'Angular': 'angular',
                }
                
                detected = []
                for tech, pattern in techs.items():
                    if pattern.lower() in html.lower():
                        detected.append(tech)
                
                if detected:
                    text += "*مكتشفة:*\n"
                    for tech in detected:
                        text += f"  ✓ {tech}\n"
                else:
                    text += "لم يتم اكتشاف تقنيات معروفة\n"
                
                return text
    except Exception as e:
        return f"❌ خطأ: {str(e)[:100]}"


async def cms_detect(domain: str) -> str:
    """اكتشاف نوع CMS"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://{domain}/wp-admin", timeout=5) as response:
                if response.status == 200 or response.status == 302:
                    return f"✅ *CMS:* WordPress\n\nالموقع يستخدم WordPress CMS"
        
        # Check other CMS
        cms_urls = {
            'Joomla': '/administrator',
            'Drupal': '/admin',
            'Magento': '/admin',
        }
        
        for cms, url in cms_urls.items():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://{domain}{url}", timeout=5) as resp:
                        if resp.status == 200:
                            return f"✅ *CMS:* {cms}"
            except:
                pass
        
        return "❌ لم يتم اكتشاف CMS معروف"
    except Exception as e:
        return f"❌ خطأ: {str(e)[:100]}"


async def subdomain_enum(domain: str) -> str:
    """عد وإحصاء Subdomains"""
    try:
        # Using public API
        url = f"https://crt.sh/?q={domain}&output=json"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    subdomains = set()
                    
                    for cert in data:
                        names = cert.get('name_value', '')
                        for name in names.split('\n'):
                            if domain in name:
                                subdomains.add(name.strip())
                    
                    text = f"📊 *تعداد Subdomains:* `{domain}`\n\n"
                    text += f"🔢 *العدد الكلي:* {len(subdomains)}\n\n"
                    
                    for sub in list(subdomains)[:15]:
                        text += f"  • {sub}\n"
                    
                    if len(subdomains) > 15:
                        text += f"\n_... و {len(subdomains) - 15} آخرين_"
                    
                    return text
                else:
                    return "❌ خطأ في الحصول على البيانات"
    except Exception as e:
        return f"❌ خطأ: {str(e)[:100]}"


async def open_ports_check(host: str) -> str:
    """فحص المنافذ المفتوحة (بدون Nmap)"""
    text = f"🔓 *فحص المنافذ:* `{host}`\n\n"
    text += "⚠️ يتطلب Nmap للحصول على نتائج كاملة\n\n"
    
    common_ports = {
        21: 'FTP',
        22: 'SSH',
        25: 'SMTP',
        53: 'DNS',
        80: 'HTTP',
        443: 'HTTPS',
        3306: 'MySQL',
        5432: 'PostgreSQL',
        8080: 'HTTP-Alt',
        8443: 'HTTPS-Alt',
    }
    
    text += "*المنافذ الشائعة:*\n"
    for port, service in common_ports.items():
        text += f"  {port:5d} - {service}\n"
    
    return text
