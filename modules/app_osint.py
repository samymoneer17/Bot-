#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 App OSINT Module - أدوات تحليل التطبيقات المتقدمة
مع دعم شامل لتحليل التوقيعات V1 + V2 + V3
"""

import subprocess
import tempfile
import os
import re
import zipfile
import hashlib
import asyncio
import logging
import struct

logger = logging.getLogger(__name__)

class AdvancedAPKAnalyzer:
    def __init__(self):
        self.tools = {
            'apktool': 'apktool',
            'keytool': 'keytool',
            'apksigner': 'apksigner'
        }
    
    def _read_file(self, path):
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
        return ""

    def _extract_permissions(self, manifest):
        return re.findall(r'android\.permission\.\w+', manifest)

    def _find_secrets(self, directory):
        cmd = f"grep -r -i 'password\\|api_key\\|secret\\|token\\|key' {directory} 2>/dev/null | head -50"
        return subprocess.getoutput(cmd)

    def _find_urls(self, directory):
        cmd = f"grep -r -E -o 'https?://[^ <>\"]{{1,}}' {directory} 2>/dev/null | sort -u"
        return subprocess.getoutput(cmd)

    def _find_emails(self, directory):
        cmd = f"grep -r -E -o '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}' {directory} 2>/dev/null | sort -u"
        return subprocess.getoutput(cmd)

    def _find_ips(self, directory):
        cmd = f"grep -r -E -o '([0-9]{{1,3}}\\.){{3}}[0-9]{{1,3}}' {directory} 2>/dev/null | sort -u"
        return subprocess.getoutput(cmd)

    def _extract_v1_signature(self, apk_zip):
        """
        استخراج التوقيع V1 (التوقيع التقليدي)
        يستخدم ملفات RSA/DSA في مجلد META-INF
        """
        try:
            cert_files = [f for f in apk_zip.namelist() if 'META-INF' in f and (f.endswith('.RSA') or f.endswith('.DSA') or f.endswith('.EC'))]
            if cert_files:
                cert_file = cert_files[0]
                cert_data = apk_zip.read(cert_file)
                # استخراج معلومات أساسية
                cert_type = cert_file.split('.')[-1]
                cert_size = len(cert_data)
                cert_hash = hashlib.sha256(cert_data).hexdigest()
                
                return {
                    'present': True,
                    'type': cert_type,
                    'file': cert_file,
                    'size': cert_size,
                    'hash_sha256': cert_hash[:16] + '...',
                    'preview': cert_data[:32].hex()
                }
        except Exception as e:
            logger.error(f"Error extracting V1 signature: {e}")
        
        return {'present': False}

    def _extract_v2_v3_signature(self, apk_path):
        """
        استخراج التوقيعات V2/V3 من APK Signing Block
        يقع بعد مباشرة كل محتويات ZIP file
        """
        try:
            with open(apk_path, 'rb') as f:
                # اقرأ آخر 24 بايت للعثور على APK Signing Block
                f.seek(-24, 2)
                footer = f.read(24)
                
                # تحقق من signature
                if footer[-16:] != b'APK Sig Block 42':
                    return {'v2': {'present': False}, 'v3': {'present': False}}
                
                # اقرأ حجم الكتلة
                block_size = struct.unpack('<Q', footer[-24:-8])[0]
                
                # اقرأ الكتلة كاملة
                f.seek(-block_size - 24, 2)
                block_data = f.read(block_size + 24)
                
                v2_info = self._parse_v2_block(block_data)
                v3_info = self._parse_v3_block(block_data)
                
                return {
                    'v2': v2_info,
                    'v3': v3_info,
                    'block_size': block_size
                }
        except Exception as e:
            logger.error(f"Error extracting V2/V3 signature: {e}")
            return {'v2': {'present': False}, 'v3': {'present': False}}

    def _parse_v2_block(self, block_data):
        """تحليل ملف التوقيع V2"""
        try:
            # البحث عن تحديد ID V2 (0x7109871a)
            if b'\x1a\x87\x09\x71' in block_data:
                return {
                    'present': True,
                    'version': 'Android 7.0+',
                    'algorithm': 'RSA/ECDSA',
                    'scheme': 'APK Signing Scheme v2',
                    'size': len(block_data)
                }
        except:
            pass
        return {'present': False}

    def _parse_v3_block(self, block_data):
        """تحليل ملف التوقيع V3"""
        try:
            # البحث عن تحديد ID V3 (0xf05368c0)
            if b'\xc0\x68\x53\xf0' in block_data:
                return {
                    'present': True,
                    'version': 'Android 9.0+',
                    'algorithm': 'RSA/ECDSA',
                    'scheme': 'APK Signing Scheme v3',
                    'size': len(block_data)
                }
        except:
            pass
        return {'present': False}

    def _extract_all_signatures(self, apk_path):
        """
        استخراج شامل لجميع التوقيعات V1 + V2 + V3
        """
        signatures = {
            'v1': {'present': False},
            'v2': {'present': False},
            'v3': {'present': False},
            'summary': ''
        }
        
        try:
            with zipfile.ZipFile(apk_path, 'r') as apk:
                # استخراج V1
                v1_info = self._extract_v1_signature(apk)
                signatures['v1'] = v1_info
            
            # استخراج V2 و V3
            v2v3_info = self._extract_v2_v3_signature(apk_path)
            signatures['v2'] = v2v3_info.get('v2', {'present': False})
            signatures['v3'] = v2v3_info.get('v3', {'present': False})
            
            # بناء الملخص
            present = []
            if signatures['v1'].get('present'):
                present.append('V1 (JAR Signing)')
            if signatures['v2'].get('present'):
                present.append('V2 (APK Signing Scheme v2)')
            if signatures['v3'].get('present'):
                present.append('V3 (APK Signing Scheme v3)')
            
            if present:
                signatures['summary'] = ' + '.join(present)
            else:
                signatures['summary'] = '❌ لا توجد توقيعات'
                
        except Exception as e:
            logger.error(f"Error in _extract_all_signatures: {e}")
            signatures['error'] = str(e)
        
        return signatures

    def _list_libraries(self, apk_zip):
        return [f for f in apk_zip.namelist() if f.endswith('.so')]

    def _calculate_hashes(self, apk_path):
        hashes = {}
        with open(apk_path, "rb") as f:
            data = f.read()
            hashes['md5'] = hashlib.md5(data).hexdigest()
            hashes['sha1'] = hashlib.sha1(data).hexdigest()
            hashes['sha256'] = hashlib.sha256(data).hexdigest()
        return hashes

    async def full_analysis(self, apk_path, temp_dir=None):
        results = {}
        cleanup_needed = False
        try:
            # تحقق من وجود الملف أولاً
            if not os.path.exists(apk_path):
                return {'error': f"File not found: {apk_path}"}
            
            # 1. Basic Info (using apktool instead of aapt)
            results['basic'] = f"📱 حجم الملف: {os.path.getsize(apk_path) / (1024*1024):.2f}MB\n✅ APK صالح للتحليل"
            
            # 2. Decompile
            if not temp_dir:
                temp_dir = tempfile.mkdtemp()
                cleanup_needed = True
            else:
                os.makedirs(temp_dir, exist_ok=True)
            
            decompile_dir = os.path.join(temp_dir, "decompile")
            process = await asyncio.create_subprocess_shell(
                f"apktool d {apk_path} -o {decompile_dir} -f",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await asyncio.wait_for(process.communicate(), timeout=120)
            
            # 3. Extract everything from decompiled directory
            manifest_path = os.path.join(decompile_dir, "AndroidManifest.xml")
            results['manifest'] = self._read_file(manifest_path)
            results['permissions'] = self._extract_permissions(results['manifest'])
            results['secrets'] = self._find_secrets(decompile_dir)
            results['urls'] = self._find_urls(decompile_dir)
            results['emails'] = self._find_emails(decompile_dir)
            results['ips'] = self._find_ips(decompile_dir)
            
            # 4. Extract from APK directly (including signatures)
            with zipfile.ZipFile(apk_path, 'r') as apk:
                results['libraries'] = self._list_libraries(apk)
                results['hashes'] = self._calculate_hashes(apk_path)
            
            # 5. استخراج التوقيعات V1 + V2 + V3
            signatures = self._extract_all_signatures(apk_path)
            results['signatures'] = signatures
            results['certificate'] = self._format_signature_output(signatures)
            
            # 6. Cleanup if we created a temp dir
            if cleanup_needed and os.path.exists(temp_dir):
                subprocess.run(f"rm -rf {temp_dir}", shell=True)
        except Exception as e:
            logger.error(f"Error in full_analysis: {e}")
            results['error'] = str(e)
            
        return results

    def _format_signature_output(self, signatures):
        """
        تنسيق مخرجات التوقيعات بشكل جميل
        """
        output = "🔐 *تحليل التوقيعات (Signature Analysis)*\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        output += f"📋 *الملخص:* {signatures.get('summary', 'غير متاح')}\n\n"
        
        # V1
        output += "*V1 - التوقيع التقليدي (JAR Signing):*\n"
        if signatures['v1'].get('present'):
            output += f"  ✅ موجود\n"
            output += f"  📝 النوع: {signatures['v1'].get('type', 'N/A')}\n"
            output += f"  📄 الملف: {signatures['v1'].get('file', 'N/A')}\n"
            output += f"  📊 الحجم: {signatures['v1'].get('size', 0)} بايت\n"
            output += f"  🔗 SHA256: {signatures['v1'].get('hash_sha256', 'N/A')}\n"
        else:
            output += f"  ❌ غير موجود\n"
        output += "\n"
        
        # V2
        output += "*V2 - APK Signing Scheme v2:*\n"
        if signatures['v2'].get('present'):
            output += f"  ✅ موجود\n"
            output += f"  📱 الإصدار: {signatures['v2'].get('version', 'Android 7.0+')}\n"
            output += f"  🔐 المخطط: {signatures['v2'].get('scheme', 'N/A')}\n"
            output += f"  🔧 الخوارزمية: {signatures['v2'].get('algorithm', 'N/A')}\n"
        else:
            output += f"  ❌ غير موجود\n"
        output += "\n"
        
        # V3
        output += "*V3 - APK Signing Scheme v3:*\n"
        if signatures['v3'].get('present'):
            output += f"  ✅ موجود\n"
            output += f"  📱 الإصدار: {signatures['v3'].get('version', 'Android 9.0+')}\n"
            output += f"  🔐 المخطط: {signatures['v3'].get('scheme', 'N/A')}\n"
            output += f"  🔧 الخوارزمية: {signatures['v3'].get('algorithm', 'N/A')}\n"
        else:
            output += f"  ❌ غير موجود\n"
        output += "\n"
        
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += "💡 *ملاحظات:*\n"
        output += "• V1: التوقيع التقليدي (متوافق مع جميع إصدارات Android)\n"
        output += "• V2: أسرع وأكثر أماناً (Android 7.0 Nougat +)\n"
        output += "• V3: دعم تغيير المفتاح (Android 9.0 Pie +)\n"
        
        return output

    async def run_command(self, cmd):
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return stdout.decode(errors='ignore') + stderr.decode(errors='ignore')

# Legacy function for backward compatibility
async def apktool_analyze(apk_name_or_link):
    analyzer = AdvancedAPKAnalyzer()
    # In a real scenario, we would download the file first.
    # This is a placeholder for the logic requested.
    return f"📦 *تحليل Apktool لـ:* `{apk_name_or_link}`\n\nيرجى استخدام الأوامر التفصيلية مثل `/apkinfo` بعد رفع الملف."
