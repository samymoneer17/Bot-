#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔽 Download Tools Module
أدوات تنزيل المواقع والمشاريع مع فك تشفير الكود المضغوط
"""

import os
import re
import asyncio
import shutil
import tempfile
import zipfile
import aiohttp
from urllib.parse import urlparse, urljoin
from datetime import datetime
from bs4 import BeautifulSoup
import jsbeautifier
import cssbeautifier


SUPPORTED_EXTENSIONS = {
    '.html', '.htm', '.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', 
    '.json', '.xml', '.txt', '.php', '.asp', '.aspx', '.py', '.rb', '.go', '.java',
    '.sql', '.c', '.cpp', '.cs', '.swift', '.ts', '.jsx', '.tsx', '.vue', '.scss', '.sass',
    '.less', '.md', '.yaml', '.yml', '.toml', '.ini', '.config', '.env', '.htaccess',
    '.log', '.bak', '.tmp', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.rar', '.tar', '.gz', '.7z', '.mp3', '.mp4', '.avi', '.mov', '.flv', '.wmv',
    '.woff', '.woff2', '.ttf', '.eot', '.otf', '.webp', '.webm',
    # ملفات مخفية وإضافية
    '.env.production', '.env.development', '.env.local', '.env.test',
    '.gitignore', '.gitmodules', '.gitattributes', 'Dockerfile',
    'docker-compose.yml', 'nginx.conf', '.htpasswd', '.ftpconfig',
    '.travis.yml', 'web.config', 'package.json', 'composer.json',
    'requirements.txt', 'Procfile', '.editorconfig', '.babelrc',
    'tsconfig.json', 'vue.config.js', 'webpack.config.js'
}


def is_obfuscated(content: str) -> bool:
    """كشف إذا كان الكود مشفر (obfuscated)"""
    import re
    
    obfuscation_patterns = [
        (r'_0x[a-f0-9]{4,}', 3),  # متغيرات مثل _0x4a90d3
        (r'a\d+_0x[a-f0-9]+', 2),  # متغيرات مثل a66_0x45e0d8
        (r'\[\'[a-zA-Z]+\'\]', 10),  # وصول للخصائص مثل ['toString']
        (r'\\x[0-9a-f]{2}', 5),  # سلاسل مشفرة hex
        (r'\\u[0-9a-f]{4}', 5),  # سلاسل Unicode
        (r'String\.fromCharCode', 2),  # تشفير السلاسل
        (r'atob\s*\(', 2),  # Base64 decode
        (r'eval\s*\(', 2),  # eval usage
        (r'Function\s*\(', 2),  # Function constructor
        (r'[a-zA-Z]\s*=\s*[a-zA-Z]\s*-\s*[a-zA-Z]', 5),  # عمليات حسابية مشوشة
        (r'parseInt\s*\([^)]+,\s*\d+\)', 3),  # parseInt مع radix
        (r'\[\s*[\'"][^\'"]+[\'"]\s*\]\s*\(', 5),  # استدعاء دالة بالأقواس
        (r'while\s*\(\!\!\[\]\)', 1),  # while(![]) pattern
        (r'try\s*\{\s*\}\s*catch', 3),  # empty try-catch
    ]
    
    score = 0
    sample = content[:10000]  # فحص أول 10000 حرف
    
    for pattern, threshold in obfuscation_patterns:
        matches = re.findall(pattern, sample)
        if len(matches) >= threshold:
            score += 1
    
    return score >= 2


def decode_unicode_escapes(content: str) -> str:
    """فك تشفير Unicode escapes"""
    import re
    
    def replace_unicode(match):
        try:
            return chr(int(match.group(1), 16))
        except:
            return match.group(0)
    
    return re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, content)


def decode_hex_escapes(content: str) -> str:
    """فك تشفير Hex escapes"""
    import re
    
    def replace_hex(match):
        try:
            return chr(int(match.group(1), 16))
        except:
            return match.group(0)
    
    return re.sub(r'\\x([0-9a-fA-F]{2})', replace_hex, content)


def decode_base64_strings(content: str) -> str:
    """فك تشفير Base64 المضمنة"""
    import re
    import base64
    
    def replace_base64(match):
        try:
            b64_str = match.group(1)
            # تحقق من أنها base64 صالحة
            if len(b64_str) > 8 and len(b64_str) % 4 == 0:
                decoded = base64.b64decode(b64_str).decode('utf-8', errors='ignore')
                if decoded.isprintable() and len(decoded) > 2:
                    return f'"{decoded}"'
        except:
            pass
        return match.group(0)
    
    # atob('...')
    content = re.sub(r'atob\s*\(\s*[\'"]([A-Za-z0-9+/=]+)[\'"]\s*\)', replace_base64, content)
    
    return content


def decode_char_codes(content: str) -> str:
    """فك تشفير String.fromCharCode"""
    import re
    
    def replace_charcode(match):
        try:
            codes = match.group(1)
            nums = [int(x.strip()) for x in codes.split(',') if x.strip().isdigit()]
            decoded = ''.join(chr(n) for n in nums if 0 <= n <= 65535)
            if decoded and decoded.isprintable():
                return f'"{decoded}"'
        except:
            pass
        return match.group(0)
    
    # String.fromCharCode(72, 101, 108, 108, 111)
    content = re.sub(r'String\.fromCharCode\s*\(([^)]+)\)', replace_charcode, content)
    
    return content


def simplify_bracket_notation(content: str) -> str:
    """تحويل الوصول بالأقواس إلى نقطة"""
    import re
    
    # obj['property'] -> obj.property
    content = re.sub(r"\['(\w+)'\]", r'.\1', content)
    content = re.sub(r'\["(\w+)"\]', r'.\1', content)
    
    return content


def remove_dead_code(content: str) -> str:
    """إزالة الكود الميت والتعليقات الفارغة"""
    import re
    
    # إزالة التعليقات الفارغة
    content = re.sub(r'/\*\s*\*/', '', content)
    
    # إزالة if(false){...}
    content = re.sub(r'if\s*\(\s*false\s*\)\s*\{[^}]*\}', '', content)
    
    # إزالة if(![]){...} (always false)
    content = re.sub(r'if\s*\(\s*!\s*\[\s*\]\s*\)\s*\{[^}]*\}', '', content)
    
    return content


def decode_split_strings(content: str) -> str:
    """دمج السلاسل المقسمة"""
    import re
    
    # "hel" + "lo" -> "hello"
    def merge_strings(match):
        parts = re.findall(r'[\'"]([^\'"]*)[\'"]', match.group(0))
        if parts:
            return f'"{("".join(parts))}"'
        return match.group(0)
    
    # تكرار لدمج السلاسل المتتالية
    for _ in range(3):
        content = re.sub(r'[\'"][^\'"]*[\'"]\s*\+\s*[\'"][^\'"]*[\'"]', merge_strings, content)
    
    return content


def decode_array_obfuscation(content: str) -> str:
    """محاولة فك تشفير المصفوفات المشوشة"""
    import re
    
    # البحث عن المصفوفة الرئيسية
    array_match = re.search(r'var\s+(\w+)\s*=\s*\[([^\]]{100,})\];', content[:5000])
    if array_match:
        var_name = array_match.group(1)
        try:
            # استخراج العناصر
            array_content = array_match.group(2)
            elements = re.findall(r'[\'"]([^\'"]+)[\'"]', array_content)
            
            if len(elements) > 10:
                # استبدال الوصول للمصفوفة
                for i, elem in enumerate(elements[:200]):  # أول 200 عنصر
                    pattern = re.escape(f'{var_name}[{i}]')
                    content = re.sub(pattern, f'"{elem}"', content)
                    
                    # أيضاً للأنماط المختلفة
                    pattern2 = re.escape(f'{var_name}[0x{i:x}]')
                    content = re.sub(pattern2, f'"{elem}"', content)
        except:
            pass
    
    return content


def basic_deobfuscate(content: str) -> str:
    """فك التشفير الشامل - يحاول عدة تقنيات"""
    
    # 1. فك Unicode و Hex
    content = decode_unicode_escapes(content)
    content = decode_hex_escapes(content)
    
    # 2. فك Base64
    content = decode_base64_strings(content)
    
    # 3. فك String.fromCharCode
    content = decode_char_codes(content)
    
    # 4. دمج السلاسل المقسمة
    content = decode_split_strings(content)
    
    # 5. تبسيط الوصول بالأقواس
    content = simplify_bracket_notation(content)
    
    # 6. إزالة الكود الميت
    content = remove_dead_code(content)
    
    # 7. محاولة فك المصفوفات
    content = decode_array_obfuscation(content)
    
    return content


def beautify_javascript(content: str) -> str:
    """فك ضغط وتجميل كود JavaScript المضغوط"""
    try:
        # محاولة فك التشفير الأساسي أولاً
        if is_obfuscated(content):
            content = basic_deobfuscate(content)
        
        opts = jsbeautifier.default_options()
        opts.indent_size = 2
        opts.indent_char = ' '
        opts.max_preserve_newlines = 2
        opts.preserve_newlines = True
        opts.keep_array_indentation = False
        opts.break_chained_methods = True
        opts.indent_scripts = 'normal'
        opts.brace_style = 'collapse'
        opts.space_before_conditional = True
        opts.unescape_strings = True
        opts.wrap_line_length = 0
        opts.end_with_newline = True
        
        return jsbeautifier.beautify(content, opts)
    except Exception as e:
        return content


def beautify_css(content: str) -> str:
    """فك ضغط وتجميل كود CSS المضغوط (بما في ذلك Tailwind)"""
    try:
        opts = cssbeautifier.default_options()
        opts.indent_size = 2
        opts.indent_char = ' '
        opts.selector_separator_newline = True
        opts.end_with_newline = True
        opts.newline_between_rules = True
        
        return cssbeautifier.beautify(content, opts)
    except Exception as e:
        return content


def beautify_html(content: str) -> str:
    """تجميل كود HTML مع تجميل CSS و JS المضمنين"""
    try:
        soup = BeautifulSoup(content, 'html.parser')
        
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                beautified_css = beautify_css(style_tag.string)
                style_tag.string = f"\n{beautified_css}\n"
        
        for script_tag in soup.find_all('script'):
            if script_tag.string and not script_tag.get('src'):
                beautified_js = beautify_javascript(script_tag.string)
                script_tag.string = f"\n{beautified_js}\n"
        
        return soup.prettify()
    except Exception as e:
        return content


def process_file_content(file_path: str) -> tuple:
    """معالجة وتجميل محتوى ملف واحد
    يرجع: (تم_التجميل, مشفر)
    """
    try:
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext not in ['.js', '.css', '.html', '.htm', '.jsx', '.tsx', '.ts', '.mjs', '.cjs']:
            return (False, False)
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if not content.strip():
            return (False, False)
        
        was_obfuscated = False
        
        if ext in ['.js', '.jsx', '.tsx', '.ts', '.mjs', '.cjs']:
            was_obfuscated = is_obfuscated(content)
            beautified = beautify_javascript(content)
        elif ext == '.css':
            beautified = beautify_css(content)
        elif ext in ['.html', '.htm']:
            beautified = beautify_html(content)
        else:
            return (False, False)
        
        if beautified and beautified != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(beautified)
            return (True, was_obfuscated)
        
        return (False, was_obfuscated)
    except Exception as e:
        return (False, False)


def beautify_all_files(directory: str) -> tuple:
    """تجميل جميع ملفات JS و CSS و HTML في مجلد
    يرجع: (عدد_الملفات_المجملة, عدد_الملفات_المشفرة)
    """
    beautified_count = 0
    obfuscated_count = 0
    
    try:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                result = process_file_content(file_path)
                if result[0]:
                    beautified_count += 1
                if result[1]:
                    obfuscated_count += 1
    except Exception as e:
        pass
    
    return (beautified_count, obfuscated_count)


async def download_website(url: str, depth: int = 2) -> tuple:
    """
    تنزيل موقع كامل باستخدام wget --mirror
    يرجع: (نجاح, مسار_الملف_أو_رسالة_خطأ)
    """
    
    url_pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+$'
    if not re.match(url_pattern, url):
        return (False, "❌ صيغة الرابط غير صحيحة")
    
    parsed = urlparse(url)
    domain = parsed.netloc.replace(':', '_')
    
    if not domain:
        return (False, "❌ لم يتم التعرف على الدومين")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = tempfile.mkdtemp(prefix=f"site_{domain}_")
    zip_path = os.path.join(temp_dir, f"{domain}_{timestamp}.zip")
    
    try:
        wget_cmd = [
            'wget',
            '--mirror',
            '--convert-links',
            '--adjust-extension',
            '--page-requisites',
            '--no-parent',
            '--no-check-certificate',
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '--timeout=30',
            '--tries=2',
            '--wait=0.2',
            '--limit-rate=5M',
            '-e', 'robots=off',
            '--no-cookies',
            '--recursive',
            '--level=5',
            '--accept=' + ','.join([ext.lstrip('.') for ext in SUPPORTED_EXTENSIONS if ext.startswith('.')]),
            '--reject=exe,mp4,mp3,avi,mkv,mov',
            '--no-host-directories',
            '--directory-prefix=' + temp_dir,
            url
        ]
        
        process = await asyncio.create_subprocess_exec(
            *wget_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            await asyncio.wait_for(process.communicate(), timeout=300)
        except asyncio.TimeoutError:
            process.kill()
            await process.communicate()
        
        download_dir = None
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isdir(item_path):
                download_dir = item_path
                break
        
        if not download_dir or not os.path.exists(download_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            return (False, "❌ لم يتم تنزيل أي ملفات - تحقق من الرابط")
        
        files_count = 0
        for root, dirs, files in os.walk(download_dir):
            files_count += len(files)
        
        if files_count == 0:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return (False, "❌ لم يتم تنزيل أي ملفات - تحقق من الرابط")
        
        # تجميل وفك ضغط ملفات JS و CSS و HTML
        beautified_count, obfuscated_count = beautify_all_files(download_dir)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(download_dir):
                # تضمين الملفات المخفية وكل شيء
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, download_dir)
                    zipf.write(file_path, arcname)
                # التأكد من تضمين المجلدات الفارغة أيضاً
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    arcname = os.path.relpath(dir_path, download_dir)
                    zipf.write(dir_path, arcname)
        
        zip_size = os.path.getsize(zip_path)
        
        max_size = 50 * 1024 * 1024
        if zip_size > max_size:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return (False, f"❌ حجم الملف كبير جداً ({zip_size / (1024*1024):.1f} MB) - الحد الأقصى 50 MB")
        
        shutil.rmtree(download_dir, ignore_errors=True)
        
        return (True, zip_path, files_count, zip_size, beautified_count, obfuscated_count)
        
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return (False, f"❌ خطأ: {str(e)}")


async def download_github_repo(url: str) -> tuple:
    """
    تنزيل مشروع من GitHub باستخدام aiohttp
    يرجع: (نجاح, مسار_الملف_أو_رسالة_خطأ)
    """
    
    github_pattern = r'^https?://github\.com/([^/]+)/([^/]+)/?.*$'
    match = re.match(github_pattern, url)
    
    if not match:
        return (False, "❌ رابط GitHub غير صالح\nمثال صحيح: https://github.com/username/repo")
    
    username = match.group(1)
    repo = match.group(2).rstrip('/')
    
    if repo.endswith('.git'):
        repo = repo[:-4]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = tempfile.mkdtemp(prefix=f"github_{repo}_")
    zip_url = f"https://github.com/{username}/{repo}/archive/refs/heads/main.zip"
    zip_url_master = f"https://github.com/{username}/{repo}/archive/refs/heads/master.zip"
    zip_path = os.path.join(temp_dir, f"{repo}_{timestamp}.zip")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=60)) as session:
            success = False
            
            for try_url in [zip_url, zip_url_master]:
                try:
                    async with session.get(try_url) as response:
                        if response.status == 200:
                            content = await response.read()
                            with open(zip_path, 'wb') as f:
                                f.write(content)
                            success = True
                            break
                except:
                    continue
            
            if not success or not os.path.exists(zip_path) or os.path.getsize(zip_path) == 0:
                shutil.rmtree(temp_dir, ignore_errors=True)
                return (False, "❌ فشل تنزيل المشروع - تحقق من الرابط أو أن المستودع عام")
        
        # فك ضغط الملفات لتجميلها
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_dir)
        
        # تجميل وفك ضغط ملفات JS و CSS و HTML
        beautified_count, obfuscated_count = beautify_all_files(extract_dir)
        
        # إعادة ضغط الملفات
        new_zip_path = os.path.join(temp_dir, f"{repo}_{timestamp}_beautified.zip")
        with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, extract_dir)
                    zipf.write(file_path, arcname)
        
        # حذف الملفات القديمة
        os.remove(zip_path)
        shutil.rmtree(extract_dir, ignore_errors=True)
        
        zip_size = os.path.getsize(new_zip_path)
        
        max_size = 50 * 1024 * 1024
        if zip_size > max_size:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return (False, f"❌ حجم المشروع كبير جداً ({zip_size / (1024*1024):.1f} MB)")
        
        return (True, new_zip_path, repo, zip_size, beautified_count, obfuscated_count)
        
    except asyncio.TimeoutError:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return (False, "❌ انتهت مهلة التنزيل")
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return (False, f"❌ خطأ: {str(e)}")


async def download_any(url: str) -> tuple:
    """
    تنزيل تلقائي - يكتشف نوع الرابط ويختار الطريقة المناسبة
    """
    
    if 'github.com' in url:
        return await download_github_repo(url)
    else:
        return await download_website(url)


def cleanup_download(file_path: str):
    """تنظيف الملفات المؤقتة"""
    try:
        if file_path and os.path.exists(file_path):
            parent_dir = os.path.dirname(file_path)
            if parent_dir and 'tmp' in parent_dir:
                shutil.rmtree(parent_dir, ignore_errors=True)
    except:
        pass
