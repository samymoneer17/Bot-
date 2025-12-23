#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 Web Reconnaissance Module
أدوات استطلاع الويب بدون API
"""

import os
import aiohttp
import asyncio
import socket
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '')


async def wayback_urls(target: str) -> str:
    """جلب روابط قديمة من Wayback Machine"""
    
    target = target.replace("http://", "").replace("https://", "").strip("/")
    
    text = f"🕰️ *أرشيف Wayback Machine:* `{target}`\n\n"
    
    try:
        url = f"http://web.archive.org/cdx/search/cdx?url={target}/*&output=json&fl=original,timestamp,statuscode&collapse=urlkey&limit=50"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if len(data) > 1:
                        text += f"📊 *عدد النتائج:* {len(data) - 1}\n\n"
                        text += "🔗 *الروابط المؤرشفة:*\n"
                        
                        for i, item in enumerate(data[1:20], 1):
                            original_url = item[0]
                            timestamp = item[1]
                            status = item[2] if len(item) > 2 else "N/A"
                            
                            year = timestamp[:4]
                            month = timestamp[4:6]
                            day = timestamp[6:8]
                            
                            archive_url = f"https://web.archive.org/web/{timestamp}/{original_url}"
                            
                            short_url = original_url[:50] + "..." if len(original_url) > 50 else original_url
                            text += f"\n*{i}.* `{short_url}`\n"
                            text += f"   📅 {day}/{month}/{year} | Status: {status}\n"
                            text += f"   🔗 [عرض الأرشيف]({archive_url})\n"
                        
                        if len(data) > 20:
                            text += f"\n... و{len(data) - 20} رابط آخر\n"
                    else:
                        text += "❌ لم يتم العثور على أي روابط مؤرشفة\n"
                else:
                    text += f"⚠️ خطأ في الاتصال: {response.status}\n"
    
    except asyncio.TimeoutError:
        text += "⏱️ انتهت مهلة الاتصال\n"
    except Exception as e:
        text += f"❌ خطأ: {str(e)}\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"🔗 *رابط الأرشيف الكامل:*\n"
    text += f"https://web.archive.org/web/*/{target}/*"
    
    return text


async def dns_lookup(domain: str) -> str:
    """فحص DNS للدومين"""
    
    domain = domain.replace("http://", "").replace("https://", "").split("/")[0]
    
    text = f"🌐 *فحص DNS:* `{domain}`\n\n"
    
    try:
        ip_addresses = socket.gethostbyname_ex(domain)
        hostname = ip_addresses[0]
        aliases = ip_addresses[1]
        ips = ip_addresses[2]
        
        text += f"🏷️ *Hostname:* `{hostname}`\n\n"
        
        if ips:
            text += f"📍 *عناوين IP ({len(ips)}):*\n"
            for ip in ips:
                text += f"  • `{ip}`\n"
            text += "\n"
        
        if aliases:
            text += f"🔄 *Aliases ({len(aliases)}):*\n"
            for alias in aliases:
                text += f"  • `{alias}`\n"
            text += "\n"
        
    except socket.gaierror as e:
        text += f"❌ لم يتم العثور على الدومين: {str(e)}\n"
    except Exception as e:
        text += f"⚠️ خطأ: {str(e)}\n"
    
    try:
        async with aiohttp.ClientSession() as session:
            dns_api = f"https://dns.google/resolve?name={domain}&type=A"
            async with session.get(dns_api, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    if data.get("Answer"):
                        text += "📋 *سجلات DNS:*\n"
                        for record in data["Answer"][:10]:
                            rtype = record.get("type", "")
                            rdata = record.get("data", "")
                            text += f"  • Type {rtype}: `{rdata}`\n"
                        text += "\n"
            
            mx_api = f"https://dns.google/resolve?name={domain}&type=MX"
            async with session.get(mx_api, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("Answer"):
                        text += "📧 *سجلات البريد (MX):*\n"
                        for record in data["Answer"][:5]:
                            text += f"  • `{record.get('data', 'N/A')}`\n"
                        text += "\n"
            
            txt_api = f"https://dns.google/resolve?name={domain}&type=TXT"
            async with session.get(txt_api, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("Answer"):
                        text += "📝 *سجلات TXT:*\n"
                        for record in data["Answer"][:3]:
                            txt_data = record.get('data', 'N/A')
                            if len(txt_data) > 100:
                                txt_data = txt_data[:100] + "..."
                            text += f"  • `{txt_data}`\n"
                        text += "\n"
                        
    except Exception as e:
        pass
    
    return text


async def whois_lookup(domain: str) -> str:
    """استعلام WHOIS عن الدومين"""
    
    domain = domain.replace("http://", "").replace("https://", "").split("/")[0]
    
    text = f"📋 *معلومات WHOIS:* `{domain}`\n\n"
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://www.whoisxmlapi.com/whoisserver/WhoisService?domainName={domain}&outputFormat=JSON&apiKey=at_demo"
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    pass
    except:
        pass
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.hackertarget.com/whois/?q={domain}"
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.text()
                    
                    if "error" not in data.lower() and len(data) > 50:
                        important_fields = [
                            "Domain Name", "Registrar", "Creation Date", "Updated Date",
                            "Registry Expiry Date", "Registrant", "Admin", "Name Server"
                        ]
                        
                        lines = data.split("\n")
                        for line in lines[:30]:
                            for field in important_fields:
                                if field.lower() in line.lower():
                                    text += f"• {line.strip()}\n"
                                    break
                        
                        if len(text) < 100:
                            text += data[:1000]
                    else:
                        text += "⚠️ لم يتم العثور على معلومات WHOIS\n"
    except Exception as e:
        text += f"❌ خطأ: {str(e)}\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "🔗 *للمزيد من المعلومات:*\n"
    text += f"• https://who.is/whois/{domain}\n"
    text += f"• https://www.whois.com/whois/{domain}\n"
    
    return text


async def subdomain_finder(domain: str) -> str:
    """البحث عن Subdomains"""
    
    domain = domain.replace("http://", "").replace("https://", "").split("/")[0]
    
    text = f"🔍 *البحث عن Subdomains:* `{domain}`\n\n"
    
    found_subdomains = set()
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://crt.sh/?q=%.{domain}&output=json"
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for entry in data:
                        name = entry.get("name_value", "")
                        for sub in name.split("\n"):
                            sub = sub.strip().lower()
                            if sub and "*" not in sub and sub.endswith(domain):
                                found_subdomains.add(sub)
    except:
        pass
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.text()
                    if "error" not in data.lower():
                        for line in data.split("\n"):
                            if "," in line:
                                sub = line.split(",")[0].strip().lower()
                                if sub and sub.endswith(domain):
                                    found_subdomains.add(sub)
    except:
        pass
    
    common_subs = ["www", "mail", "ftp", "smtp", "pop", "imap", "webmail", 
                   "admin", "api", "dev", "test", "staging", "app", "blog",
                   "shop", "store", "m", "mobile", "cdn", "static", "assets"]
    
    async def check_subdomain(sub):
        try:
            full_domain = f"{sub}.{domain}"
            socket.gethostbyname(full_domain)
            found_subdomains.add(full_domain)
        except:
            pass
    
    await asyncio.gather(*[check_subdomain(sub) for sub in common_subs])
    
    if found_subdomains:
        text += f"✅ *تم العثور على {len(found_subdomains)} subdomain:*\n\n"
        
        for i, sub in enumerate(sorted(found_subdomains)[:50], 1):
            text += f"*{i}.* `{sub}`\n"
        
        if len(found_subdomains) > 50:
            text += f"\n... و{len(found_subdomains) - 50} subdomain آخر\n"
    else:
        text += "❌ لم يتم العثور على subdomains\n"
    
    return text


async def http_headers(url: str) -> str:
    """جلب HTTP Headers"""
    
    if not url.startswith("http"):
        url = "https://" + url
    
    text = f"📋 *HTTP Headers:* `{url}`\n\n"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15), allow_redirects=True) as response:
                text += f"📊 *Status:* {response.status} {response.reason}\n"
                text += f"🔗 *Final URL:* `{str(response.url)}`\n\n"
                
                text += "📋 *Headers:*\n"
                
                important_headers = [
                    "server", "x-powered-by", "content-type", "x-frame-options",
                    "strict-transport-security", "content-security-policy",
                    "x-xss-protection", "x-content-type-options", "cache-control",
                    "set-cookie", "cf-ray", "x-cache"
                ]
                
                for header, value in response.headers.items():
                    if header.lower() in important_headers:
                        if len(value) > 100:
                            value = value[:100] + "..."
                        text += f"• *{header}:* `{value}`\n"
                
                text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
                text += "*كل الـ Headers:*\n"
                for header, value in list(response.headers.items())[:15]:
                    if len(value) > 50:
                        value = value[:50] + "..."
                    text += f"• {header}: {value}\n"
                
                if len(response.headers) > 15:
                    text += f"\n... و{len(response.headers) - 15} header آخر\n"
                    
    except aiohttp.ClientError as e:
        text += f"❌ خطأ في الاتصال: {str(e)}\n"
    except Exception as e:
        text += f"⚠️ خطأ: {str(e)}\n"
    
    return text


async def page_links(url: str) -> str:
    """استخراج الروابط من صفحة ويب"""
    
    if not url.startswith("http"):
        url = "https://" + url
    
    text = f"🔗 *استخراج الروابط:* `{url}`\n\n"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    parsed_url = urlparse(url)
                    base_domain = parsed_url.netloc
                    
                    internal_links = set()
                    external_links = set()
                    emails = set()
                    phones = set()
                    
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        
                        if href.startswith('mailto:'):
                            emails.add(href.replace('mailto:', '').split('?')[0])
                        elif href.startswith('tel:'):
                            phones.add(href.replace('tel:', ''))
                        elif href.startswith('http'):
                            if base_domain in href:
                                internal_links.add(href)
                            else:
                                external_links.add(href)
                        elif href.startswith('/'):
                            internal_links.add(f"{parsed_url.scheme}://{base_domain}{href}")
                    
                    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                    found_emails = re.findall(email_pattern, html)
                    emails.update(found_emails[:10])
                    
                    if internal_links:
                        text += f"🏠 *روابط داخلية ({len(internal_links)}):*\n"
                        for link in list(internal_links)[:15]:
                            short = link[:60] + "..." if len(link) > 60 else link
                            text += f"  • `{short}`\n"
                        text += "\n"
                    
                    if external_links:
                        text += f"🌐 *روابط خارجية ({len(external_links)}):*\n"
                        for link in list(external_links)[:10]:
                            short = link[:60] + "..." if len(link) > 60 else link
                            text += f"  • `{short}`\n"
                        text += "\n"
                    
                    if emails:
                        text += f"📧 *إيميلات ({len(emails)}):*\n"
                        for email in emails:
                            text += f"  • `{email}`\n"
                        text += "\n"
                    
                    if phones:
                        text += f"📞 *أرقام هواتف ({len(phones)}):*\n"
                        for phone in phones:
                            text += f"  • `{phone}`\n"
                    
                    if not (internal_links or external_links or emails):
                        text += "❌ لم يتم العثور على روابط\n"
                else:
                    text += f"⚠️ خطأ: Status {response.status}\n"
                    
    except Exception as e:
        text += f"❌ خطأ: {str(e)}\n"
    
    return text


async def tech_detect(url: str) -> str:
    """اكتشاف التقنيات المستخدمة في الموقع"""
    
    if not url.startswith("http"):
        url = "https://" + url
    
    text = f"🔧 *اكتشاف التقنيات:* `{url}`\n\n"
    
    technologies = {
        'CMS': [],
        'Frameworks': [],
        'JavaScript': [],
        'Analytics': [],
        'CDN': [],
        'Server': [],
        'Security': []
    }
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as response:
                html = await response.text()
                resp_headers = dict(response.headers)
                
                server = resp_headers.get('Server', resp_headers.get('server', ''))
                if server:
                    technologies['Server'].append(server)
                
                x_powered = resp_headers.get('X-Powered-By', resp_headers.get('x-powered-by', ''))
                if x_powered:
                    technologies['Frameworks'].append(x_powered)
                
                if 'cf-ray' in str(resp_headers).lower():
                    technologies['CDN'].append('Cloudflare')
                
                cms_patterns = {
                    'WordPress': ['wp-content', 'wp-includes', 'wordpress'],
                    'Joomla': ['joomla', '/media/system/js/'],
                    'Drupal': ['drupal', 'sites/default/files'],
                    'Magento': ['magento', 'mage/'],
                    'Shopify': ['shopify', 'cdn.shopify.com'],
                    'Wix': ['wix.com', 'wixstatic'],
                    'Squarespace': ['squarespace'],
                }
                
                for cms, patterns in cms_patterns.items():
                    for pattern in patterns:
                        if pattern.lower() in html.lower():
                            if cms not in technologies['CMS']:
                                technologies['CMS'].append(cms)
                            break
                
                js_patterns = {
                    'jQuery': ['jquery'],
                    'React': ['react', 'reactdom', '_reactRootContainer'],
                    'Vue.js': ['vue.js', 'vue.min.js', '__vue__'],
                    'Angular': ['ng-app', 'ng-controller', 'angular'],
                    'Bootstrap': ['bootstrap'],
                    'Tailwind': ['tailwind'],
                }
                
                for js, patterns in js_patterns.items():
                    for pattern in patterns:
                        if pattern.lower() in html.lower():
                            if js not in technologies['JavaScript']:
                                technologies['JavaScript'].append(js)
                            break
                
                analytics_patterns = {
                    'Google Analytics': ['google-analytics', 'ga.js', 'gtag'],
                    'Google Tag Manager': ['googletagmanager'],
                    'Facebook Pixel': ['facebook.net/tr', 'fbq('],
                    'Hotjar': ['hotjar'],
                }
                
                for analytic, patterns in analytics_patterns.items():
                    for pattern in patterns:
                        if pattern.lower() in html.lower():
                            if analytic not in technologies['Analytics']:
                                technologies['Analytics'].append(analytic)
                            break
                
                security_headers = ['strict-transport-security', 'x-frame-options', 
                                  'content-security-policy', 'x-xss-protection']
                for header in security_headers:
                    if header in str(resp_headers).lower():
                        technologies['Security'].append(header.upper())
        
        for category, techs in technologies.items():
            if techs:
                text += f"*{category}:*\n"
                for tech in techs:
                    text += f"  • {tech}\n"
                text += "\n"
        
        if not any(technologies.values()):
            text += "⚠️ لم يتم اكتشاف تقنيات محددة\n"
            
    except Exception as e:
        text += f"❌ خطأ: {str(e)}\n"
    
    return text


async def robots_txt(url: str) -> str:
    """جلب ملف robots.txt"""
    
    if not url.startswith("http"):
        url = "https://" + url
    
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    
    text = f"🤖 *ملف Robots.txt:* `{parsed.netloc}`\n\n"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(robots_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    if len(content) > 2000:
                        content = content[:2000] + "\n... [truncated]"
                    
                    text += f"```\n{content}\n```\n"
                else:
                    text += f"❌ لم يتم العثور على ملف robots.txt (Status: {response.status})\n"
                    
    except Exception as e:
        text += f"❌ خطأ: {str(e)}\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
    sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
    text += f"🗺️ *Sitemap:* `{sitemap_url}`"
    
    return text


async def ip_lookup(ip: str) -> str:
    """فحص معلومات عنوان IP"""
    import socket
    import asyncio
    
    ip = ip.strip()
    
    text = f"🌐 *فحص IP:* `{ip}`\n\n"
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query,proxy,hosting,mobile"
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('status') == 'success':
                        text += f"📍 *عنوان IP:* `{data.get('query')}`\n"
                        text += f"🌍 *الدولة:* {data.get('country')} ({data.get('countryCode')})\n"
                        text += f"📍 *المنطقة:* {data.get('regionName')}\n"
                        text += f"🏙️ *المدينة:* {data.get('city')}\n"
                        if data.get('zip'):
                            text += f"📮 *الرمز البريدي:* {data.get('zip')}\n"
                        text += f"📌 *الإحداثيات:* {data.get('lat')}, {data.get('lon')}\n"
                        text += f"🕐 *المنطقة الزمنية:* {data.get('timezone')}\n"
                        
                        text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
                        text += "🏢 *معلومات الشبكة:*\n"
                        text += f"• *مزود الخدمة (ISP):* {data.get('isp')}\n"
                        text += f"• *المنظمة:* {data.get('org')}\n"
                        text += f"• *ASN:* {data.get('as')}\n"
                        
                        text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
                        text += "🔒 *فحص VPN/Proxy/CDN:*\n"
                        
                        is_proxy = data.get('proxy', False)
                        is_hosting = data.get('hosting', False)
                        is_mobile = data.get('mobile', False)
                        
                        if is_proxy:
                            text += "• 🔴 *Proxy/VPN:* نعم - يستخدم بروكسي أو VPN\n"
                        else:
                            text += "• 🟢 *Proxy/VPN:* لا - لا يستخدم بروكسي أو VPN\n"
                        
                        if is_hosting:
                            text += "• 🔴 *مركز بيانات/CDN:* نعم - عنوان من مركز بيانات\n"
                        else:
                            text += "• 🟢 *مركز بيانات/CDN:* لا - عنوان سكني\n"
                        
                        if is_mobile:
                            text += "• 📱 *شبكة موبايل:* نعم\n"
                        else:
                            text += "• 📱 *شبكة موبايل:* لا\n"
                        
                        threat_level = 0
                        if is_proxy:
                            threat_level += 1
                        if is_hosting:
                            threat_level += 1
                            
                        if threat_level == 0:
                            text += "\n✅ *التقييم:* عنوان IP يبدو طبيعي\n"
                        elif threat_level == 1:
                            text += "\n⚠️ *التقييم:* عنوان IP مشبوه - قد يكون VPN أو Proxy\n"
                        else:
                            text += "\n🔴 *التقييم:* عنوان IP مشبوه جداً - مركز بيانات مع بروكسي\n"
                        
                    else:
                        text += f"❌ {data.get('message', 'IP غير صالح')}\n"
                else:
                    text += f"❌ خطأ في الاتصال: {response.status}\n"
    except Exception as e:
        text += f"❌ خطأ: {str(e)}\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "🔄 *Reverse DNS:*\n"
    try:
        hostname = socket.gethostbyaddr(ip)
        text += f"• *اسم المضيف:* `{hostname[0]}`\n"
        if hostname[1]:
            text += f"• *الأسماء البديلة:* {', '.join(hostname[1])}\n"
    except socket.herror:
        text += "• لم يتم العثور على سجل PTR\n"
    except Exception as e:
        text += f"• خطأ: {str(e)}\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "🔓 *فحص المنافذ المفتوحة:*\n"
    
    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 3306, 3389, 5432, 8080, 8443]
    open_ports = []
    
    async def check_port(port):
        try:
            conn = asyncio.open_connection(ip, port)
            reader, writer = await asyncio.wait_for(conn, timeout=1.5)
            writer.close()
            await writer.wait_closed()
            return port
        except:
            return None
    
    try:
        tasks = [check_port(port) for port in common_ports]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        open_ports = [int(p) for p in results if p is not None and isinstance(p, int)]
        
        if open_ports:
            port_names = {
                21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
                80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
                993: "IMAPS", 995: "POP3S", 3306: "MySQL", 3389: "RDP",
                5432: "PostgreSQL", 8080: "HTTP-Alt", 8443: "HTTPS-Alt"
            }
            for port in sorted(open_ports):
                port_name = port_names.get(port, "Unknown")
                text += f"• 🟢 *{port}* ({port_name})\n"
        else:
            text += "• لم يتم العثور على منافذ مفتوحة\n"
    except Exception as e:
        text += f"• خطأ في فحص المنافذ: {str(e)}\n"
    
    return text
