#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐙 Kraken Advanced Directory & Security Tools
أدوات كراكن المتقدمة للبحث والأمان
"""

import aiohttp
import asyncio


async def admin_finder(domain: str) -> str:
    """البحث عن لوحات التحكم والمسارات الإدارية"""
    try:
        common_paths = [
            '/admin', '/administrator', '/admin.php', '/admin.html', '/adm',
            '/wp-admin', '/joomla-admin', '/drupal-admin', '/magento-admin',
            '/cpanel', '/plesk', '/webmin', '/directadmin', '/vesta',
            '/manage', '/console', '/login', '/signin', '/secret-admin',
            '/user/login', '/auth/login', '/api/admin', '/portal/admin',
            '/backend', '/dashboard', '/control-panel', '/sysadmin',
            '/cms-admin', '/staff', '/members/login', '/wp-login.php',
            '/admin1', '/admin2', '/moderator', '/root', '/webadmin'
        ]
        
        text = f"🔑 *البحث عن لوحات التحكم:* `{domain}`\n\n"
        found = []
        
        # استخدام Semaphore لتقليل الضغط على السيرفر وتسريع الفحص
        sem = asyncio.Semaphore(10)
        
        async def check_path(session, path):
            async with sem:
                try:
                    url = f"https://{domain}{path}"
                    async with session.head(url, timeout=aiohttp.ClientTimeout(total=5), allow_redirects=False) as resp:
                        if resp.status in [200, 301, 302, 403]:
                            return (path, resp.status)
                except:
                    pass
            return None

        async with aiohttp.ClientSession(headers={'User-Agent': 'Mozilla/5.0'}) as session:
            tasks = [check_path(session, path) for path in common_paths]
            results = await asyncio.gather(*tasks)
            found = [r for r in results if r]
        
        if found:
            text += "✅ *وجدت مسارات:*\n"
            for path, status in found:
                emoji = "🚫" if status == 403 else "✅"
                text += f"{emoji} `{path}` - Status: {status}\n"
        else:
            text += "❌ لم يتم العثور على مسارات إدارية"
        
        return text
    except Exception as e:
        return f"❌ خطأ: {str(e)[:100]}"


async def dir_finder(domain: str) -> str:
    """البحث عن المجلدات والملفات المهمة"""
    try:
        interesting_paths = [
            '/uploads', '/downloads', '/media', '/images', '/img',
            '/files', '/documents', '/docs', '/backup', '/backups',
            '/config', '/configuration', '/settings', '/setup',
            '/api', '/v1', '/v2', '/api/v1', '/api/v2', '/dev',
            '/.git', '/.env', '/web.config', '/config.php', '/phpinfo.php',
            '/robots.txt', '/sitemap.xml', '/security.txt', '/.well-known',
            '/logs', '/error_log', '/storage', '/private', '/tmp',
            '/.vscode', '/.idea', '/node_modules', '/vendor', '/dist'
        ]
        
        text = f"📁 *البحث عن المجلدات:* `{domain}`\n\n"
        sem = asyncio.Semaphore(10)
        
        async def check_path(session, path):
            async with sem:
                try:
                    url = f"https://{domain}{path}"
                    async with session.head(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                        if resp.status != 404:
                            return (path, resp.status)
                except:
                    pass
            return None

        async with aiohttp.ClientSession(headers={'User-Agent': 'Mozilla/5.0'}) as session:
            tasks = [check_path(session, path) for path in interesting_paths]
            results = await asyncio.gather(*tasks)
            found = [r for r in results if r]
        
        if found:
            text += "✅ *مجلدات مكتشفة:*\n"
            for path, status in found[:20]:
                text += f"  📂 `{path}` - {status}\n"
        else:
            text += "❌ لم يتم اكتشاف مجلدات مهمة"
        
        return text
    except Exception as e:
        return f"❌ خطأ: {str(e)[:100]}"


async def sensitive_files(domain: str) -> str:
    """البحث عن الملفات الحساسة المكشوفة"""
    try:
        sensitive = [
            '/.env', '/config.php', '/database.yml', '/settings.py',
            '/.aws/credentials', '/credentials.json', '/key.json',
            '/private.key', '/id_rsa', '/.ssh/config', '/auth.json',
            '/web.config', '/web.xml', '/.htaccess', '/.htpasswd',
            '/package.json', '/composer.json', '/requirements.txt',
            '/docker-compose.yml', '/Dockerfile', '/Makefile',
            '/.git/config', '/.git/HEAD', '/.svn/entries',
            '/admin/config.php', '/wp-config.php', '/config/db.php',
            '/sql.sql', '/database.sql', '/db_backup.sql', '/backup.zip'
        ]
        
        text = f"⚠️ *فحص الملفات الحساسة:* `{domain}`\n\n"
        sem = asyncio.Semaphore(10)
        
        async def check_file(session, file):
            async with sem:
                try:
                    url = f"https://{domain}{file}"
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                        if resp.status == 200:
                            # محاولة كشف WAF البسيط
                            content = await resp.text()
                            if "WAF" in content or "Cloudflare" in content:
                                return None
                            return file
                except:
                    pass
            return None

        async with aiohttp.ClientSession(headers={'User-Agent': 'Mozilla/5.0'}) as session:
            tasks = [check_file(session, file) for file in sensitive]
            results = await asyncio.gather(*tasks)
            found = [r for r in results if r]
        
        if found:
            text += "🚨 *ملفات مكشوفة:*\n"
            for f in found:
                text += f"  ⚠️ {f}\n"
        else:
            text += "✅ لم يتم العثور على ملفات حساسة مكشوفة"
        
        return text
    except Exception as e:
        return f"❌ خطأ: {str(e)[:100]}"


async def banner_grabbing(host: str) -> str:
    """جلب بانر السيرفر والخدمات"""
    try:
        import socket
        
        text = f"🎫 *جلب البانر:* `{host}`\n\n"
        
        ports_to_check = [
            (21, 'FTP'),
            (22, 'SSH'),
            (25, 'SMTP'),
            (80, 'HTTP'),
            (443, 'HTTPS'),
            (3306, 'MySQL'),
            (5432, 'PostgreSQL'),
        ]
        
        for port, service in ports_to_check:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, port))
                
                if result == 0:
                    try:
                        sock.send(b'HEAD / HTTP/1.0\r\n\r\n')
                        banner = sock.recv(1024).decode('utf-8', errors='ignore')
                        if banner:
                            text += f"✅ *{service} ({port}):*\n"
                            text += f"```\n{banner[:200]}\n```\n\n"
                    except:
                        text += f"✅ *{service} ({port}):* مفتوح\n"
                
                sock.close()
            except:
                pass
        
        return text
    except Exception as e:
        return f"❌ خطأ: {str(e)[:100]}"
