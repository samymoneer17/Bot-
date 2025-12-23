#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Nmap Port Scanning Module
أداة فحص المنافذ المتقدمة باستخدام Nmap
"""

import subprocess
import asyncio
import re


async def nmap_scan(target: str, scan_type: str = "basic") -> str:
    """
    فحص المنافذ باستخدام Nmap المتقدم
    
    Args:
        target: عنوان IP أو المضيف
        scan_type: نوع المسح المتقدم
    """
    
    if not target or len(target) == 0:
        return "❌ يرجى تحديد هدف صالح"
    
    if any(char in target for char in [';', '|', '&', '$', '`', '\n']):
        return "❌ عنوان غير صالح"
    
    # خيارات Nmap المتقدمة والحقيقية
    scan_options = {
        'basic': '-sV --top-ports 100',
        'full': '-sV -p- -T4',
        'aggressive': '-A -T4 -p-',
        'service': '-sV --script=nmap-service-probes',
        'vuln': '--script vuln,vulners,http-vuln* -T4', # فحص الثغرات الشامل والموسع
        'auth': '--script auth,ssh-brute,ftp-brute,mysql-brute', # فحص بروتوكولات التحقق والتخمين الأساسي
        'default': '-sC -sV', # السكربتات الافتراضية الأكثر أماناً
        'safe': '--script safe', # سكربتات آمنة لا تسبب ضرر للمستهدف
        'malware': '--script malware', # البحث عن آثار برمجيات خبيثة
        'discovery': '--script discovery,dns-brute,http-enum', # اكتشاف معلومات موسعة عن الشبكة والخدمات
        'brute': '--script brute,http-brute,telnet-brute', # محاولات التخمين التلقائي على الخدمات
    }
    
    options = scan_options.get(scan_type, scan_options['basic'])
    
    try:
        # بناء الأمر
        if scan_type in ['vuln', 'aggressive', 'brute']:
            # إضافة خيارات إضافية للمسح العميق
            options += " --script-args=unsafe=1"
        
        cmd = f'nmap {options} {target}'
        
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # زيادة التايم أوت للمسح العميق والسكربتات
        timeout = 300 if scan_type in ['vuln', 'aggressive', 'full', 'brute', 'discovery'] else 90
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )
        
        result = stdout.decode('utf-8', errors='ignore')
        
        if 'Nmap done' not in result:
            return f"❌ فشل المسح أو انتهت المهلة\n{stderr.decode('utf-8', errors='ignore')[:100]}"
        
        # تنسيق النتيجة بشكل احترافي وجذاب
        text = f"🎯 *نتائج Nmap الاحترافية:* `{target}`\n"
        text += f"📊 *نوع الفحص:* `{scan_type.upper()}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # استخراج المنافذ والحالة والخدمة والإصدار
        lines = result.split('\n')
        ports_data = []
        capture_ports = False
        
        for line in lines:
            if 'PORT' in line and 'STATE' in line:
                capture_ports = True
                continue
            if capture_ports and line.strip():
                if 'Nmap done' in line or (line and not line[0].isdigit() and ' |' not in line):
                    capture_ports = False
                    continue
                # إضافة الأسطر التي تبدأ برقم (منفذ) أو تبدأ بـ | (نتيجة سكربت للمنفذ)
                if line[0].isdigit() or line.strip().startswith('|'):
                    ports_data.append(line.strip())
        
        if ports_data:
            text += "🔓 *المنافذ والخدمات المكتشفة:*\n"
            for p in ports_data[:30]: # عرض حتى 30 سطر لضمان عدم تجاوز طول الرسالة
                if p[0].isdigit():
                    text += f"\n✅ `{p}`"
                else:
                    text += f"\n   `{p}`"
        
        # استخراج نتائج السكربتات العامة (Host Scripts)
        host_scripts = re.findall(r'Host script results:(.*?)(?=\n\n|\nNmap done)', result, re.DOTALL)
        if host_scripts:
            text += "\n\n📜 *نتائج سكربتات المضيف (NSE):*\n"
            clean_scripts = host_scripts[0].strip().replace('|', '├').replace('_', '└')
            text += f"`{clean_scripts[:500]}`" # قص النتائج الطويلة جداً
        
        # معلومات نظام التشغيل بدقة
        os_match = re.search(r'OS details: (.*)', result)
        if os_match:
            text += f"\n\n🖥 *تخمين النظام:* `{os_match.group(1)}`"
            
        # ملخص الحالة النهائية
        summary_match = re.search(r'Nmap done: (.*)', result)
        if summary_match:
            text += f"\n\n⏱ *الملخص:* {summary_match.group(1)}"
        
        return text
        
    except asyncio.TimeoutError:
        return f"❌ انتهت المهلة ({timeout}ث) للمسح من نوع {scan_type}. الهدف قد يكون بطيئاً أو محمياً بجدار ناري."
    except Exception as e:
        return f"❌ خطأ تقني في تنفيذ الأمر: {str(e)}"

async def nmap_vuln_scan(target: str) -> str:
    """فحص الثغرات باستخدام NSE"""
    return await nmap_scan(target, 'vuln')

async def nmap_brute_scan(target: str) -> str:
    """فحص التخمين باستخدام NSE"""
    return await nmap_scan(target, 'brute')

async def nmap_discovery_scan(target: str) -> str:
    """اكتشاف معلومات المضيف"""
    return await nmap_scan(target, 'discovery')


async def nmap_aggressive_scan(target: str) -> str:
    """مسح عدواني شامل"""
    return await nmap_scan(target, 'aggressive')


async def nmap_service_scan(target: str) -> str:
    """مسح الخدمات والإصدارات"""
    return await nmap_scan(target, 'service')
