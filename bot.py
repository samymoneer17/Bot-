#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 OSINT Hunter Bot - بوت جمع المعلومات الشامل المحسن
بوت تليجرام متكامل لجمع المعلومات والبحث المتقدم
"""

import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from modules.phone_osint import phone_search, whatsapp_osint, phone_verify, ignorant_check, phone_reputation
from modules.email_osint import email_check, breach_check, email_domain_info, holehe_only_used
from modules.download_tools import download_any, cleanup_download
from modules.username_osint import username_search, username_similar
from modules.social_osint import facebook_osint, instagram_osint, twitter_history
from modules.crypto_osint import (
    bitcoin_wallet, ton_wallet, ton_transactions, 
    ethereum_wallet, usdt_balance, crypto_price, multi_wallet_check
)
from modules.national_id import analyze_egyptian_id
from modules.security_tools import cloudflare_check, shodan_exploits
from modules.google_osint import (
    google_email_osint, youtube_channel_osint, google_drive_osint,
    wifi_geolocate, google_search_dork
)
from modules.web_recon import (
    wayback_urls, dns_lookup, whois_lookup, subdomain_finder,
    http_headers, page_links, tech_detect, robots_txt, ip_lookup
)
from modules.vuln_scanner import (
    sql_injection_scan, xss_scan, lfi_scan, open_redirect_scan,
    command_injection_scan, security_headers_scan, cors_scan,
    full_scan, dir_bruteforce, port_scan, waf_detect
)
from modules.sqlmap_osint import (
    sqlmap_scan, sqlmap_deep_scan, sqlmap_param_scan,
    sqlmap_exploit_db, sqlmap_exploit_tables, sqlmap_exploit_columns,
    sqlmap_dump_data, sqlmap_os_shell
)
# from modules.exif_osint import extract_exif
from modules.doh_osint import doh_lookup
from modules.ip_geo_osint import ip_geo_lookup
from modules.http_sec_osint import http_security_check
from modules.nmap_osint import (
    nmap_scan, nmap_aggressive_scan, nmap_service_scan,
    nmap_vuln_scan, nmap_brute_scan, nmap_discovery_scan
)
from modules.argus_tools import (
    dns_records, ssl_expiry, server_info, reverse_ip, cdn_detection,
    tech_stack, cms_detect, subdomain_enum, open_ports_check
)
from modules.kraken_tools import admin_finder, dir_finder, sensitive_files, banner_grabbing
from modules.lucille_tools import (
    email_extract, phone_extract, sitemap_analysis, security_txt,
    hash_md5, hash_decode, reverse_dns_lookup
)
from modules.deep_web_osint import shodan_scan, darkweb_check, censys_scan
from modules.app_osint import AdvancedAPKAnalyzer, apktool_analyze

from modules.admin_panel import (
    admin_panel, admin_stats, admin_users, admin_channels_menu,
    admin_ban_menu, admin_broadcast_menu, admin_back,
    ban_user, unban_user, add_channel, remove_channel, broadcast,
    get_stats_command, is_banned, check_subscription, 
    get_subscription_keyboard, add_user, increment_command, is_admin
)

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

TELEGRAM_TOKEN = '7852035741:AAFdF4iuBe38GMuqR2mdph0-Z3sMAqhI-YM'

MAIN_MENU_TEXT = """
🔍 *مرحباً بك في OSINT Hunter Bot V5.0*

🧭 *بوت متقدم لجمع المعلومات والاستخبارات المفتوحة*
ابحث عن أي رقم هاتف، بريد إلكتروني، اسم مستخدم، محافظ العملات الرقمية والمزيد!

━━━━━━━━━━━━━━━━━━━━━━
📱 *أدوات الهاتف:*
• `/phone` - البحث عن رقم هاتف
• `/whatsapp` - معلومات واتساب
• `/verify` - التحقق من صحة الرقم
• `/ignorant` - فحص الرقم في المنصات
• `/reputation` - فحص سمعة الرقم

━━━━━━━━━━━━━━━━━━━━━━
📧 *أدوات البريد الإلكتروني:*
• `/email` - فحص الإيميل في 100+ منصة
• `/holehe` - Holehe Only Used (المنصات المستخدمة فقط)
• `/breach` - فحص التسريبات
• `/domain` - معلومات دومين الإيميل

━━━━━━━━━━━━━━━━━━━━━━
🕵️ *الويب العميق وShodan (جديد):*
• `/shodan` - فحص IP/دومين عبر Shodan
• `/darkweb` - فحص تسريبات الويب العميق
• `/censys` - فحص الأجهزة المتصلة (Censys)

━━━━━━━━━━━━━━━━━━━━━━
💰 *أدوات العملات الرقمية:*
• `/btc` - معلومات محفظة Bitcoin
• `/ton` - معلومات محفظة TON
• `/tontx` - معاملات TON
• `/eth` - معلومات محفظة Ethereum
• `/usdt` - رصيد USDT
• `/wallet` - فحص شامل للمحفظة
• `/prices` - أسعار العملات الرقمية

━━━━━━━━━━━━━━━━━━━━━━
👤 *أدوات السوشيال ميديا:*
• `/username` - البحث في 50+ منصة
• `/similar` - اقتراح أسماء مشابهة
• `/facebook` - معلومات فيسبوك
• `/instagram` - معلومات انستجرام
• `/xhistory` - تاريخ أسماء X/Twitter

━━━━━━━━━━━━━━━━━━━━━━
🔵 *أدوات Google:*
• `/ghunt` - تحليل حساب Google
• `/youtube` - تحليل قناة يوتيوب
• `/gdrive` - تحليل Google Drive
• `/wifi` - تحديد موقع WiFi
• `/dork` - Google Dorking

━━━━━━━━━━━━━━━━━━━━━━
🆔 *أدوات الهوية:*
• `/nid` - تحليل الرقم القومي المصري

━━━━━━━━━━━━━━━━━━━━━━
📱 *أدوات تحليل التطبيقات المتقدمة:*
• `/apkinfo` - معلومات أساسية عن APK
• `/apkmanifest` - عرض ملف AndroidManifest.xml
• `/apkpermissions` - استخراج الصلاحيات
• `/apksecrets` - البحث عن أسرار مخفية
• `/apkurls` - استخراج الروابط الداخلية
• `/apkdecompile` - تفكيك كامل للتطبيق
• `/apkdecrypt` - فك تشفير APK
• `/apkcert` - شهادة توقيع التطبيق
• `/apkfull` - تحليل شامل كامل
━━━━━━━━━━━━━━━━━━━━━━
🛡️ *أدوات الأمان:*
• `/cloudflare` - فحص CloudFlare
• `/exploits` - البحث عن ثغرات CVE

━━━━━━━━━━━━━━━━━━━━━━
🔥 *فحص الثغرات:*
• `/scan` - فحص شامل للموقع
• `/sqli` - فحص SQL Injection
• `/xss` - فحص XSS
• `/lfi` - فحص LFI
• `/redirect` - فحص Open Redirect
• `/cmdi` - فحص Command Injection
• `/secheaders` - فحص Security Headers
• `/cors` - فحص CORS
• `/dirscan` - البحث عن مجلدات مخفية
• `/portscan` - فحص المنافذ
• `/waf` - اكتشاف WAF

━━━━━━━━━━━━━━━━━━━━━━
🎯 *أدوات متقدمة (Nmap & SQLMap):*
• `/nmap` - مسح Nmap أساسي للمنافذ
• `/nmapagg` - مسح Nmap عدواني شامل
• `/sqlmap` - فحص SQL Injection بـ SQLMap
• `/sqlmapdeep` - فحص عميق شامل

━━━━━━━━━━━━━━━━━━━━━━
🌐 *أدوات استطلاع الويب:*
• `/wayback` - أرشيف Wayback Machine
• `/dns` - فحص DNS
• `/whois` - معلومات WHOIS
• `/subdomains` - البحث عن Subdomains
• `/headers` - فحص HTTP Headers
• `/links` - استخراج الروابط
• `/tech` - اكتشاف التقنيات
• `/robots` - ملف Robots.txt

━━━━━━━━━━━━━━━━━━━━━━
📸 *أدوات التحليل والشبكات:*
• `/exif` - تحليل البيانات الوصفية للصور
• `/imgsearch` - البحث العكسي عن الصور
• `/unshort` - كشف الروابط المختصرة
• `/doh` - فحص DNS مشفر (DoH)
• `/ipgeo` - تحديد موقع IP المتقدم
• `/httpsec` - فحص أمان روابط الموقع

━━━━━━━━━━━━━━━━━━━━━━
🔽 *أدوات التنزيل:*
• `/download` - تنزيل موقع/مشروع كامل مضغوط

━━━━━━━━━━━━━━━━━━━━━━
💡 *للمساعدة:* `/help`
"""

def get_main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📱 أدوات الهاتف", callback_data="menu_phone"),
            InlineKeyboardButton("📧 أدوات الإيميل", callback_data="menu_email"),
        ],
        [
            InlineKeyboardButton("💰 العملات الرقمية", callback_data="menu_crypto"),
            InlineKeyboardButton("👤 السوشيال ميديا", callback_data="menu_social"),
        ],
        [
            InlineKeyboardButton("🔵 أدوات Google", callback_data="menu_google"),
            InlineKeyboardButton("🕵️ الويب العميق", callback_data="menu_deepweb"),
        ],
        [
            InlineKeyboardButton("🛡️ أدوات الأمان", callback_data="menu_security"),
            InlineKeyboardButton("🆔 الرقم القومي", callback_data="menu_nid"),
        ],
        [
            InlineKeyboardButton("🌐 استطلاع الويب", callback_data="menu_webrecon"),
            InlineKeyboardButton("🔥 فحص الثغرات", callback_data="menu_vulnscan"),
        ],
        [
            InlineKeyboardButton("🎯 أدوات Nmap", callback_data="menu_nmap"),
            InlineKeyboardButton("💉 أدوات SQLMap", callback_data="menu_sqlmap"),
        ],
        [
            InlineKeyboardButton("📱 أدوات التطبيقات", callback_data="menu_app"),
            InlineKeyboardButton("🔽 أدوات التنزيل", callback_data="menu_download"),
        ],
        [
            InlineKeyboardButton("🔮 أدوات Lucille 🐙", callback_data="menu_lucille"),
            InlineKeyboardButton("🐙 أدوات Kraken", callback_data="menu_kraken"),
        ],
        [
            InlineKeyboardButton("🔙 العودة", callback_data="menu_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

async def check_user_access(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is banned or needs to subscribe to channels"""
    user = update.effective_user
    user_id = user.id
    
    if is_banned(user_id):
        await update.message.reply_text("❌ أنت محظور من استخدام البوت!")
        return False
    
    is_subscribed, not_subscribed = await check_subscription(context.bot, user_id)
    if not is_subscribed:
        await update.message.reply_text(
            "⚠️ *يجب عليك الاشتراك في القنوات التالية لاستخدام البوت:*",
            parse_mode='Markdown',
            reply_markup=get_subscription_keyboard(not_subscribed)
        )
        return False
    
    add_user(user_id, user.username)
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if is_banned(user_id):
        await update.message.reply_text("❌ أنت محظور من استخدام البوت!")
        return
    
    is_subscribed, not_subscribed = await check_subscription(context.bot, user_id)
    if not is_subscribed:
        await update.message.reply_text(
            "⚠️ *يجب عليك الاشتراك في القنوات التالية لاستخدام البوت:*",
            parse_mode='Markdown',
            reply_markup=get_subscription_keyboard(not_subscribed)
        )
        return
    
    add_user(user_id, user.username)
    increment_command("start")
    
    await update.message.reply_text(
        MAIN_MENU_TEXT,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🔍 *دليل استخدام OSINT Hunter Bot V2.0*

*📱 أمثلة البحث عن هاتف:*
`/phone 01012345678`
`/whatsapp 201012345678`
`/verify +201012345678`
`/ignorant 201012345678`

*📧 أمثلة فحص الإيميل:*
`/email example@gmail.com`
`/holehe test@gmail.com`
`/breach example@gmail.com`
`/domain example@company.com`

*🔽 أمثلة التنزيل:*
`/download https://example.com`
`/download https://github.com/user/repo`

*💰 أمثلة العملات الرقمية:*
`/btc 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`
`/ton EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG`
`/eth 0x742d35Cc6634C0532925a3b844Bc9e7595f5b8`
`/usdt TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE`
`/wallet [أي عنوان محفظة]`
`/prices`

*👤 أمثلة السوشيال ميديا:*
`/username john_doe`
`/facebook zaborahmed`
`/instagram cristiano`
`/xhistory elonmusk`

*🔵 أمثلة أدوات Google:*
`/ghunt example@gmail.com`
`/youtube @username`
`/dork john_doe`

*🆔 الرقم القومي:*
`/nid 28007172400077`

*🛡️ أدوات الأمان:*
`/cloudflare https://example.com`
`/exploits nginx`
"""
    help_text += "\n*📸 أدوات التحليل (جديد):*\n`/exif` - تحليل البيانات الوصفية للصور\n`/doh [domain]` - فحص DNS مشفر\n`/ipgeo [ip]` - تحديد موقع IP المتقدم\n`/httpsec [url]` - فحص أمان الموقع"
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

# تتبع حالة المستخدم
USER_STATES = {}

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data == "menu_main":
        USER_STATES.pop(user_id, None)
        await query.edit_message_text(
            MAIN_MENU_TEXT,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    
    elif data == "menu_phone":
        USER_STATES.pop(user_id, None)
        text = """
📱 *أدوات البحث عن الهاتف*

• `/phone [رقم]` - البحث العام عن رقم
• `/whatsapp [رقم]` - معلومات واتساب
• `/verify [رقم]` - التحقق من صحة الرقم والمزود
• `/ignorant [رقم]` - فحص الرقم في المنصات
• `/reputation [رقم]` - فحص سمعة الرقم

*مثال:*
`/phone 01012345678`
`/whatsapp 201012345678`
`/ignorant +201012345678`
"""
        await query.edit_message_text(text, parse_mode='Markdown')
        
    elif data == "menu_email":
        text = """
📧 *أدوات فحص البريد الإلكتروني*

• `/email [إيميل]` - فحص في 100+ منصة (Holehe)
• `/holehe [إيميل]` - المنصات المستخدمة فقط + التفاصيل
• `/breach [إيميل]` - فحص التسريبات والاختراقات
• `/domain [إيميل]` - معلومات دومين الإيميل

*مثال:*
`/email example@gmail.com`
`/holehe test@gmail.com`
`/breach test@yahoo.com`
`/domain user@company.com`
"""
        await query.edit_message_text(text, parse_mode='Markdown')
    
    elif data == "menu_lucille":
        text = """
🔮 *أدوات Lucille المتقدمة*

• `/emailextract` - استخراج الإيميلات من نص
• `/phoneextract` - استخراج الأرقام من نص
• `/unshort` - كشف الرابط الحقيقي المختصر
• `/sitemap` - تحليل خريطة الموقع
• `/securitytxt` - فحص ملف security.txt
• `/md5` - تشفير نص لـ MD5
• `/md5decode` - محاولة فك تشفير MD5
• `/reversedns` - فحص Reverse DNS
"""
        keyboard = [
            [InlineKeyboardButton("🔗 كشف الروابط (Unshort)", callback_data="run_unshort")],
            [InlineKeyboardButton("🔙 العودة للقائمة", callback_data="menu_main")]
        ]
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "menu_tools":
        text = """
📸 *أدوات التحليل والشبكات المتقدمة*

• `/exif` - استخراج بيانات EXIF من الصور (أرسل صورة مباشرة)
• `/imgsearch` - البحث العكسي عن الصور (Google, Yandex, Bing)
• `/doh [domain]` - فحص DNS over HTTPS
• `/ipgeo [ip]` - تحديد الموقع الجغرافي الدقيق للـ IP
• `/httpsec [url]` - فحص أمان روابط المواقع والتشفير

*أمثلة:*
`/doh google.com`
`/ipgeo 8.8.8.8`
`/httpsec https://example.com`
"""
        keyboard = [
            [
                InlineKeyboardButton("📸 تحليل EXIF", callback_data="run_exif"),
                InlineKeyboardButton("🔍 بحث عكسي", callback_data="run_imgsearch")
            ],
            [
                InlineKeyboardButton("🌐 فحص DoH", callback_data="run_doh"),
                InlineKeyboardButton("🛰️ موقع IP", callback_data="run_ipgeo")
            ],
            [
                InlineKeyboardButton("🔒 أمان HTTP", callback_data="run_httpsec"),
                InlineKeyboardButton("🔙 العودة", callback_data="menu_main")
            ]
        ]
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("run_"):
        tool = data.split("_")[1]
        prompts = {
            "exif": "📸 أرسل الصورة التي تريد تحليلها مباشرة وسأقوم باستخراج بيانات EXIF لك.",
            "imgsearch": "🔍 أرسل الصورة التي تريد البحث عنها عكسياً في محركات البحث.",
            "doh": "🌐 يرجى إرسال النطاق المراد فحصه.\nمثال: `google.com`",
            "ipgeo": "🛰️ يرجى إرسال عنوان IP المراد تحديد موقعه.\nمثال: `8.8.8.8`",
            "httpsec": "🔒 يرجى إرسال رابط الموقع المراد فحص أمانه.\nمثال: `https://example.com`",
            "unshort": "🔗 يرجى إرسال الرابط المختصر لكشف وجهته الحقيقية.\nمثال: `bit.ly/xxxx`"
        }
        USER_STATES[user_id] = tool
        await query.edit_message_text(prompts.get(tool, "يرجى استخدام الأمر المباشر."), parse_mode='Markdown')

    elif data == "menu_crypto":
        text = """
💰 *أدوات العملات الرقمية*

• `/btc [عنوان]` - معلومات محفظة Bitcoin
• `/ton [عنوان]` - معلومات محفظة TON
• `/tontx [عنوان]` - معاملات محفظة TON
• `/eth [عنوان]` - معلومات محفظة Ethereum
• `/usdt [عنوان]` - رصيد USDT (TRON/ETH)
• `/wallet [عنوان]` - فحص شامل تلقائي
• `/prices` - أسعار العملات الحالية

*الشبكات المدعومة:*
Bitcoin, Ethereum, TON, TRON, BSC

*مثال:*
`/ton EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG`
`/btc 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`
`/prices`
"""
        await query.edit_message_text(text, parse_mode='Markdown')
        
    elif data == "menu_social":
        text = """
👤 *أدوات السوشيال ميديا والأصول*

• `/username [اسم]` - البحث في 50+ منصة
• `/similar [اسم]` - اقتراح أسماء مشابهة
• `/facebook [username]` - معلومات فيسبوك
• `/instagram [username]` - معلومات انستجرام
• `/xhistory [username]` - تاريخ أسماء X/Twitter
• 🖼️ *تحليل الصور:* أرسل صورة مباشرة للبوت لاستخراج بيانات EXIF (نوع الكاميرا، الموقع، التاريخ).

*مثال:*
`/username john_doe`
"""
        await query.edit_message_text(text, parse_mode='Markdown')
        
    elif data == "menu_google":
        text = """
🔵 *أدوات Google*

• `/ghunt [email]` - تحليل حساب Google من الإيميل
• `/youtube [قناة/رابط]` - تحليل قناة يوتيوب
• `/gdrive [رابط]` - تحليل رابط Google Drive
• `/wifi [BSSID]` - تحديد موقع من BSSID
• `/dork [بحث]` - Google Dorking المتقدم

*مثال:*
`/ghunt example@gmail.com`
`/youtube @username`
`/dork john_doe`
"""
        await query.edit_message_text(text, parse_mode='Markdown')
        
    elif data == "menu_security":
        text = """
🛡️ *أدوات الأمان*

• `/cloudflare [url]` - فحص إذا كان الموقع يستخدم CloudFlare
• `/exploits [product]` - البحث عن ثغرات CVE

*مثال:*
`/cloudflare https://example.com`
`/exploits nginx`
`/exploits CVE-2024-12345`
"""
        await query.edit_message_text(text, parse_mode='Markdown')
        
    elif data == "menu_nid":
        text = """
🆔 *تحليل الرقم القومي المصري*

• `/nid [الرقم]` - تحليل الرقم القومي

*المعلومات المستخرجة:*
• تاريخ الميلاد
• المحافظة
• الجنس
• رقم التسلسل

*مثال:*
`/nid 28007172400077`
"""
        await query.edit_message_text(text, parse_mode='Markdown')

    elif data == "menu_app":
        text = """
📱 *أدوات تحليل التطبيقات المتقدمة (APKTool)*

**طريقة 1️⃣ - من ملف مباشر (حتى 20MB):**
أرسل ملف APK مباشرة للبوت

**طريقة 2️⃣ - من رابط مباشر (بدون حد 20MB):**
• `/apkurl https://example.com/app.apk` - تحميل من رابط مباشر

**الأوامر المتاحة:**
• `/apkinfo` - معلومات أساسية
• `/apkmanifest` - ملف AndroidManifest.xml
• `/apkpermissions` - استخراج الصلاحيات
• `/apksecrets` - البحث عن Secrets
• `/apkurls` - استخراج الروابط
• `/apkdecompile` - تفكيك التطبيق
• `/apkfull` - تحليل شامل
"""
        keyboard = [[InlineKeyboardButton("🔙 العودة للقائمة", callback_data="menu_main")]]
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "menu_prices":
        result = await crypto_price()
        await query.edit_message_text(result, parse_mode='Markdown')
    
    elif data == "menu_webrecon":
        text = """
🌐 *أدوات استطلاع الويب*

• `/wayback [domain]` - أرشيف Wayback Machine
• `/dns [domain]` - فحص DNS
• `/whois [domain]` - معلومات WHOIS
• `/subdomains [domain]` - البحث عن Subdomains
• `/headers [url]` - فحص HTTP Headers
• `/links [url]` - استخراج الروابط
• `/tech [url]` - اكتشاف التقنيات
• `/robots [url]` - ملف Robots.txt

*مثال:*
`/wayback example.com`
`/dns google.com`
`/subdomains example.com`
"""
        await query.edit_message_text(text, parse_mode='Markdown')
    
    elif data == "menu_vulnscan":
        text = """
🔥 *أدوات فحص واستغلال الثغرات*

*فحص شامل:*
• `/scan [url]` - فحص شامل للموقع

*فحص ثغرات محددة:*
• `/sqli [url]` - فحص SQL Injection
• `/xss [url]` - فحص XSS
• `/lfi [url]` - فحص LFI
• `/redirect [url]` - فحص Open Redirect
• `/cmdi [url]` - فحص Command Injection

*فحص الإعدادات:*
• `/secheaders [url]` - فحص Security Headers
• `/cors [url]` - فحص CORS

*فحص إضافي:*
• `/dirscan [url]` - البحث عن مجلدات مخفية
• `/portscan [host]` - فحص المنافذ المفتوحة
• `/waf [url]` - اكتشاف WAF/IDS

*مثال:*
`/scan https://example.com`
`/sqli https://example.com/page.php?id=1`
`/portscan example.com`
"""
        await query.edit_message_text(text, parse_mode='Markdown')
    
    elif data == "menu_nmap":
        text = """
🎯 *أدوات Nmap الاحترافية (NSE)*

• `/nmap [target]` - مسح سريع (100 منفذ)
• `/nmapagg [target]` - مسح عدواني شامل (-A)
• `/nmapsvc [target]` - فحص الخدمات والإصدارات
• `/nmapvuln [target]` - فحص الثغرات الشامل (Vuln)
• `/nmapbrute [target]` - فحص التخمين (Brute Force)
• `/nmapdisc [target]` - اكتشاف معلومات المضيف
• `/nmapfull [target]` - فحص كافة المنافذ (65535)

*مثال:*
`/nmapvuln example.com`
"""
        await query.edit_message_text(text, parse_mode='Markdown')

    elif data == "menu_sqlmap":
        text = """
💉 *أدوات SQLMap المتقدمة*

• `/sqlmap [url]` - فحص SQL Injection أساسي
• `/sqlmapdeep [url]` - فحص عميق وشامل
• `/sqlmapdbs [url]` - استخراج قواعد البيانات
• `/sqlmaptables [url] [db]` - استخراج الجداول
• `/sqlmapcolumns [url] [db] [table]` - استخراج الأعمدة
• `/sqlmapdump [url] [db] [table]` - سحب البيانات
• `/sqlmapshell [url]` - محاولة الحصول على OS Shell

*مثال:*
`/sqlmap https://example.com/id=1`
"""
        await query.edit_message_text(text, parse_mode='Markdown')

    elif data == "menu_deepweb":
        text = """
🕵️ *أدوات الويب العميق واستخبارات البنية التحتية*

• `/shodan [ip]` - فحص Shodan للأجهزة والخدمات
• `/darkweb [query]` - فحص تسريبات الويب المظلم
• `/censys [ip/domain]` - فحص Censys للبنية التحتية

*مثال:*
`/shodan 8.8.8.8`
`/darkweb example@gmail.com`
"""
        keyboard = [[InlineKeyboardButton("🔙 العودة", callback_data="menu_main")]]
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "menu_kraken":
        text = """
🐙 *أدوات Kraken للاستطلاع المتقدم*

• `/adminfinder [url]` - البحث عن لوحة التحكم (Admin)
• `/dirfinder [url]` - البحث عن مجلدات الموقع
• `/sensitivefiles [url]` - البحث عن ملفات حساسة (.env, config, etc)
• `/banner [url]` - استخراج معلومات السيرفر (Banner Grabbing)

*مثال:*
`/adminfinder https://example.com`
"""
        keyboard = [
            [InlineKeyboardButton("🔙 العودة للقائمة", callback_data="menu_main")]
        ]
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "menu_argus":
        text = """
🦅 *أدوات Argus المتقدمة*

• `/dnsrecords [domain]` - سجلات DNS التفصيلية
• `/sslexpiry [domain]` - فحص شهادة SSL
• `/serverinfo [domain]` - معلومات السيرفر
• `/reverseip [ip]` - البحث العكسي IP
• `/cdn [domain]` - اكتشاف CDN
• `/techstack [domain]` - تقنيات الموقع
• `/cmsdetect [domain]` - اكتشاف CMS
• `/subenum [domain]` - عد Subdomains
• `/openports [host]` - فحص المنافذ
"""
        await query.edit_message_text(text, parse_mode='Markdown')
    
    elif data == "menu_kraken":
        text = """
🐙 *أدوات Kraken المتقدمة*

• `/adminfinder [domain]` - البحث عن لوحات التحكم
• `/dirfinder [domain]` - البحث عن المجلدات والملفات
• `/sensitivefiles [domain]` - البحث عن ملفات حساسة
• `/banner [host]` - جلب بانر الخدمات (Banner Grabbing)

*مثال:*
`/adminfinder google.com`
"""
        await query.edit_message_text(text, parse_mode='Markdown')
    
    elif data == "menu_lucille":
        text = """
🔮 *أدوات Lucille*

• `/emailextract [domain]` - استخراج إيميلات
• `/phoneextract [domain]` - استخراج أرقام
• `/sitemap [domain]` - تحليل Sitemap
• `/securitytxt [domain]` - فحص security.txt
• `/md5 [text]` - تشفير MD5/SHA1/SHA256
• `/md5decode [hash]` - فك تشفير MD5
• `/reversedns [ip]` - DNS عكسي
"""
        await query.edit_message_text(text, parse_mode='Markdown')
    
    elif data == "menu_download":
        text = """
🔽 *أدوات التنزيل*

• `/download [رابط]` - تنزيل موقع أو مشروع

*المميزات:*
✅ تنزيل مواقع كاملة (HTML, CSS, JS, صور)
✅ تنزيل مشاريع GitHub تلقائياً
✅ ضغط الملفات وإرسالها مباشرة
✅ دعم المواقع العامة ومشاريع GitHub

*أمثلة:*
`/download https://example.com`
`/download https://github.com/user/repo`

⚠️ *ملاحظات:*
• الحد الأقصى للحجم: 50 MB
• قد يستغرق التنزيل عدة دقائق
• تأكد من أن الموقع/المشروع عام
"""
        await query.edit_message_text(text, parse_mode='Markdown')
    
    elif data == "admin_stats":
        await admin_stats(update, context)
    
    elif data == "admin_users":
        await admin_users(update, context)
    
    elif data == "admin_channels":
        await admin_channels_menu(update, context)
    
    elif data == "admin_ban_menu":
        await admin_ban_menu(update, context)
    
    elif data == "admin_broadcast":
        await admin_broadcast_menu(update, context)
    
    elif data == "admin_back":
        await admin_back(update, context)
    
    elif data == "admin_settings":
        if not is_admin(query.from_user.id):
            return
        text = """
⚙️ *الإعدادات*

*الأدمن الحاليين:*
• `7627857345`
• `962731079`

*ملاحظة:* لتعديل الأدمن، يرجى تعديل ملف admin_panel.py
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]]
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "check_subscription":
        user_id = query.from_user.id
        is_subscribed, not_subscribed = await check_subscription(context.bot, user_id)
        if is_subscribed:
            await query.answer("✅ تم التحقق! أنت مشترك في جميع القنوات.", show_alert=True)
            await query.edit_message_text(
                MAIN_MENU_TEXT,
                parse_mode='Markdown',
                reply_markup=get_main_keyboard()
            )
        else:
            await query.answer("❌ لم تشترك في جميع القنوات بعد!", show_alert=True)

async def phone_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال رقم الهاتف\nمثال: `/phone 01012345678`", parse_mode='Markdown')
        return
    
    phone = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري البحث عن الرقم: `{phone}`...", parse_mode='Markdown')
    
    result = await phone_search(phone)
    await msg.edit_text(result, parse_mode='Markdown')

async def whatsapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال رقم الهاتف مع كود الدولة\nمثال: `/whatsapp 201012345678`", parse_mode='Markdown')
        return
    
    phone = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري البحث في واتساب: `{phone}`...", parse_mode='Markdown')
    
    result = await whatsapp_osint(phone)
    await msg.edit_text(result, parse_mode='Markdown')

async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال رقم الهاتف\nمثال: `/verify 201012345678`", parse_mode='Markdown')
        return
    
    phone = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري التحقق من الرقم: `{phone}`...", parse_mode='Markdown')
    
    result = await phone_verify(phone)
    await msg.edit_text(result, parse_mode='Markdown')

async def ignorant_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال رقم الهاتف\nمثال: `/ignorant 201012345678`", parse_mode='Markdown')
        return
    
    phone = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري فحص الرقم في المنصات: `{phone}`...", parse_mode='Markdown')
    
    result = await ignorant_check(phone)
    await msg.edit_text(result, parse_mode='Markdown')

async def reputation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال رقم الهاتف\nمثال: `/reputation 201012345678`", parse_mode='Markdown')
        return
    
    phone = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري فحص سمعة الرقم: `{phone}`...", parse_mode='Markdown')
    
    result = await phone_reputation(phone)
    await msg.edit_text(result, parse_mode='Markdown')

async def email_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال البريد الإلكتروني\nمثال: `/email example@gmail.com`", parse_mode='Markdown')
        return
    
    email = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري فحص الإيميل: `{email}`...\n⏳ قد يستغرق هذا بعض الوقت...", parse_mode='Markdown')
    
    result = await email_check(email)
    await msg.edit_text(result, parse_mode='Markdown')

async def breach_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال البريد الإلكتروني\nمثال: `/breach example@gmail.com`", parse_mode='Markdown')
        return
    
    email = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري فحص التسريبات: `{email}`...", parse_mode='Markdown')
    
    result = await breach_check(email)
    await msg.edit_text(result, parse_mode='Markdown')

async def domain_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال البريد الإلكتروني\nمثال: `/domain example@gmail.com`", parse_mode='Markdown')
        return
    
    email = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري فحص الدومين...", parse_mode='Markdown')
    
    result = await email_domain_info(email)
    await msg.edit_text(result, parse_mode='Markdown')

async def holehe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال البريد الإلكتروني\nمثال: `/holehe test@gmail.com`", parse_mode='Markdown')
        return
    
    email = context.args[0]
    msg = await update.message.reply_text(f"🔍 *Holehe Only Used*\n📧 الإيميل: `{email}`\n\n⏳ جاري الفحص في 100+ منصة...\nقد يستغرق هذا دقيقة أو أكثر...", parse_mode='Markdown')
    
    result = await holehe_only_used(email)
    await msg.edit_text(result, parse_mode='Markdown')

async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("""❌ يرجى إدخال الرابط

*أمثلة:*
`/download https://example.com`
`/download https://github.com/user/repo`

*المميزات:*
• تنزيل مواقع كاملة
• تنزيل مشاريع GitHub
• ضغط وإرسال مباشر""", parse_mode='Markdown')
        return
    
    url = context.args[0]
    
    if 'github.com' in url:
        msg = await update.message.reply_text(f"🔽 *تنزيل مشروع GitHub*\n📂 الرابط: `{url}`\n\n⏳ جاري التنزيل...", parse_mode='Markdown')
    else:
        msg = await update.message.reply_text(f"🔽 *تنزيل موقع*\n🌐 الرابط: `{url}`\n\n⏳ جاري التنزيل... قد يستغرق عدة دقائق", parse_mode='Markdown')
    
    try:
        result = await download_any(url)
        
        if result[0]:
            file_path = result[1]
            
            if 'github.com' in url:
                repo_name = result[2]
                file_size = result[3]
                beautified_count = result[4] if len(result) > 4 else 0
                obfuscated_count = result[5] if len(result) > 5 else 0
                caption = f"✅ *تم تنزيل المشروع بنجاح*\n📂 المشروع: `{repo_name}`\n📦 الحجم: {file_size / 1024:.1f} KB"
                if beautified_count > 0:
                    caption += f"\n🔓 تم تجميل: {beautified_count} ملف (JS/CSS/HTML)"
                if obfuscated_count > 0:
                    caption += f"\n⚠️ ملفات مشفرة (Obfuscated): {obfuscated_count}"
                    caption += f"\n💡 _الملفات المشفرة تستخدم حماية متقدمة وقد لا يمكن قراءتها بالكامل_"
            else:
                files_count = result[2]
                file_size = result[3]
                beautified_count = result[4] if len(result) > 4 else 0
                obfuscated_count = result[5] if len(result) > 5 else 0
                caption = f"✅ *تم تنزيل الموقع بنجاح*\n📄 عدد الملفات: {files_count}\n📦 الحجم: {file_size / 1024:.1f} KB"
                if beautified_count > 0:
                    caption += f"\n🔓 تم تجميل: {beautified_count} ملف (JS/CSS/HTML)"
                if obfuscated_count > 0:
                    caption += f"\n⚠️ ملفات مشفرة (Obfuscated): {obfuscated_count}"
                    caption += f"\n💡 _الملفات المشفرة تستخدم حماية متقدمة وقد لا يمكن قراءتها بالكامل_"
            
            try:
                with open(file_path, 'rb') as f:
                    await update.message.reply_document(
                        document=f,
                        caption=caption,
                        parse_mode='Markdown'
                    )
                
                await msg.delete()
            finally:
                cleanup_download(file_path)
        else:
            await msg.edit_text(result[1], parse_mode='Markdown')
            
    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ: {str(e)}", parse_mode='Markdown')

async def username_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال اسم المستخدم\nمثال: `/username john_doe`", parse_mode='Markdown')
        return
    
    username = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري البحث عن: `{username}` في 50+ منصة...\n⏳ قد يستغرق هذا بعض الوقت...", parse_mode='Markdown')
    
    result = await username_search(username)
    await msg.edit_text(result, parse_mode='Markdown')

async def similar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال اسم المستخدم\nمثال: `/similar john`", parse_mode='Markdown')
        return
    
    username = context.args[0]
    result = await username_similar(username)
    await update.message.reply_text(result, parse_mode='Markdown')

async def nid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الرقم القومي\nمثال: `/nid 28007172400077`", parse_mode='Markdown')
        return
    
    nid = context.args[0]
    result = analyze_egyptian_id(nid)
    await update.message.reply_text(result, parse_mode='Markdown')

async def facebook_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال اسم المستخدم\nمثال: `/facebook zaborahmed`", parse_mode='Markdown')
        return
    
    username = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري البحث في فيسبوك: {username}...")
    
    result = await facebook_osint(username)
    await msg.edit_text(result)

async def instagram_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال اسم المستخدم\nمثال: `/instagram cristiano`", parse_mode='Markdown')
        return
    
    username = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري البحث في انستجرام: {username}...")
    
    result = await instagram_osint(username)
    await msg.edit_text(result)

async def xhistory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال اسم المستخدم\nمثال: `/xhistory elonmusk`", parse_mode='Markdown')
        return
    
    username = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري البحث عن تاريخ: `{username}`...", parse_mode='Markdown')
    
    result = await twitter_history(username)
    await msg.edit_text(result, parse_mode='Markdown')

async def btc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال عنوان المحفظة\nمثال: `/btc 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`", parse_mode='Markdown')
        return
    
    address = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري البحث عن محفظة Bitcoin...", parse_mode='Markdown')
    
    result = await bitcoin_wallet(address)
    await msg.edit_text(result, parse_mode='Markdown')

async def ton_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال عنوان المحفظة\nمثال: `/ton EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG`", parse_mode='Markdown')
        return
    
    address = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري البحث عن محفظة TON...", parse_mode='Markdown')
    
    result = await ton_wallet(address)
    await msg.edit_text(result, parse_mode='Markdown')

async def tontx_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال عنوان المحفظة\nمثال: `/tontx EQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG`", parse_mode='Markdown')
        return
    
    address = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري جلب معاملات TON...", parse_mode='Markdown')
    
    result = await ton_transactions(address)
    await msg.edit_text(result, parse_mode='Markdown')

async def eth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال عنوان المحفظة\nمثال: `/eth 0x742d35Cc6634C0532925a3b844Bc9e7595f5b8`", parse_mode='Markdown')
        return
    
    address = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري البحث عن محفظة Ethereum...", parse_mode='Markdown')
    
    result = await ethereum_wallet(address)
    await msg.edit_text(result, parse_mode='Markdown')

async def usdt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال عنوان المحفظة\nمثال: `/usdt TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE`", parse_mode='Markdown')
        return
    
    address = context.args[0]
    network = context.args[1] if len(context.args) > 1 else "tron"
    msg = await update.message.reply_text(f"🔍 جاري البحث عن رصيد USDT...", parse_mode='Markdown')
    
    result = await usdt_balance(address, network)
    await msg.edit_text(result, parse_mode='Markdown')

async def wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال عنوان المحفظة\nمثال: `/wallet [عنوان]`\n\nالشبكات المدعومة:\n• Bitcoin\n• Ethereum\n• TON\n• TRON", parse_mode='Markdown')
        return
    
    address = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري فحص المحفظة في الشبكات المختلفة...", parse_mode='Markdown')
    
    result = await multi_wallet_check(address)
    await msg.edit_text(result, parse_mode='Markdown')

async def prices_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🔍 جاري جلب أسعار العملات الرقمية...", parse_mode='Markdown')
    
    result = await crypto_price()
    await msg.edit_text(result, parse_mode='Markdown')

async def cloudflare_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال رابط الموقع\nمثال: `/cloudflare https://example.com`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري فحص الموقع: `{url}`...", parse_mode='Markdown')
    
    result = await cloudflare_check(url)
    await msg.edit_text(result, parse_mode='Markdown')

async def exploits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال اسم المنتج أو CVE\nمثال: `/exploits nginx`", parse_mode='Markdown')
        return
    
    query = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري البحث عن ثغرات: `{query}`...", parse_mode='Markdown')
    
    result = await shodan_exploits(query)
    await msg.edit_text(result, parse_mode='Markdown')

async def ghunt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال البريد الإلكتروني\nمثال: `/ghunt example@gmail.com`", parse_mode='Markdown')
        return
    
    email = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري تحليل حساب Google: `{email}`...", parse_mode='Markdown')
    
    result = await google_email_osint(email)
    await msg.edit_text(result, parse_mode='Markdown')

async def youtube_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال اسم القناة أو الرابط\nمثال: `/youtube @username`", parse_mode='Markdown')
        return
    
    channel = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري تحليل قناة YouTube: `{channel}`...", parse_mode='Markdown')
    
    result = await youtube_channel_osint(channel)
    await msg.edit_text(result, parse_mode='Markdown')

async def gdrive_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال رابط Google Drive\nمثال: `/gdrive https://drive.google.com/file/d/xxx`", parse_mode='Markdown')
        return
    
    drive_url = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري تحليل رابط Drive...", parse_mode='Markdown')
    
    result = await google_drive_osint(drive_url)
    await msg.edit_text(result, parse_mode='Markdown')

async def wifi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال BSSID\nمثال: `/wifi AA:BB:CC:DD:EE:FF`", parse_mode='Markdown')
        return
    
    bssid = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري تحديد موقع WiFi: `{bssid}`...", parse_mode='Markdown')
    
    result = await wifi_geolocate(bssid)
    await msg.edit_text(result, parse_mode='Markdown')

async def dork_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال كلمة البحث\nمثال: `/dork john_doe`", parse_mode='Markdown')
        return
    
    query = ' '.join(context.args)
    msg = await update.message.reply_text(f"🔍 جاري إنشاء روابط Google Dorking: `{query}`...", parse_mode='Markdown')
    
    result = await google_search_dork(query)
    await msg.edit_text(result, parse_mode='Markdown')

async def wayback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الدومين\nمثال: `/wayback example.com`", parse_mode='Markdown')
        return
    
    domain = context.args[0]
    msg = await update.message.reply_text(f"🕰️ جاري البحث في Wayback Machine: `{domain}`...", parse_mode='Markdown')
    
    result = await wayback_urls(domain)
    await msg.edit_text(result, parse_mode='Markdown', disable_web_page_preview=True)

async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال عنوان IP\nمثال: `/ip 8.8.8.8`", parse_mode='Markdown')
        return
    
    ip = context.args[0]
    msg = await update.message.reply_text(f"🌐 جاري فحص IP: `{ip}`...", parse_mode='Markdown')
    
    result = await ip_lookup(ip)
    await msg.edit_text(result, parse_mode='Markdown', disable_web_page_preview=True)

async def dns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الدومين\nمثال: `/dns example.com`", parse_mode='Markdown')
        return
    
    domain = context.args[0]
    msg = await update.message.reply_text(f"🌐 جاري فحص DNS: `{domain}`...", parse_mode='Markdown')
    
    result = await dns_lookup(domain)
    await msg.edit_text(result, parse_mode='Markdown')

async def whois_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الدومين\nمثال: `/whois example.com`", parse_mode='Markdown')
        return
    
    domain = context.args[0]
    msg = await update.message.reply_text(f"📋 جاري البحث في WHOIS: `{domain}`...", parse_mode='Markdown')
    
    result = await whois_lookup(domain)
    await msg.edit_text(result, parse_mode='Markdown', disable_web_page_preview=True)

async def subdomains_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الدومين\nمثال: `/subdomains example.com`", parse_mode='Markdown')
        return
    
    domain = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري البحث عن Subdomains: `{domain}`...\n⏳ قد يستغرق هذا بعض الوقت...", parse_mode='Markdown')
    
    result = await subdomain_finder(domain)
    await msg.edit_text(result, parse_mode='Markdown')

async def headers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الرابط\nمثال: `/headers https://example.com`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    msg = await update.message.reply_text(f"📋 جاري فحص Headers: `{url}`...", parse_mode='Markdown')
    
    result = await http_headers(url)
    await msg.edit_text(result, parse_mode='Markdown')

async def links_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الرابط\nمثال: `/links https://example.com`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    msg = await update.message.reply_text(f"🔗 جاري استخراج الروابط: `{url}`...", parse_mode='Markdown')
    
    result = await page_links(url)
    await msg.edit_text(result, parse_mode='Markdown', disable_web_page_preview=True)

async def tech_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الرابط\nمثال: `/tech https://example.com`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    msg = await update.message.reply_text(f"🔧 جاري اكتشاف التقنيات: `{url}`...", parse_mode='Markdown')
    
    result = await tech_detect(url)
    await msg.edit_text(result, parse_mode='Markdown')

async def robots_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الرابط\nمثال: `/robots https://example.com`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    msg = await update.message.reply_text(f"🤖 جاري جلب Robots.txt: `{url}`...", parse_mode='Markdown')
    
    result = await robots_txt(url)
    await msg.edit_text(result, parse_mode='Markdown', disable_web_page_preview=True)

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الرابط\nمثال: `/scan https://example.com`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    msg = await update.message.reply_text(f"🔥 جاري الفحص الشامل: `{url}`...\n⏳ قد يستغرق بضع دقائق...", parse_mode='Markdown')
    
    result = await full_scan(url)
    await msg.edit_text(result, parse_mode='Markdown')

async def sqli_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الرابط\nمثال: `/sqli https://example.com/page.php?id=1`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    msg = await update.message.reply_text(f"💉 جاري فحص SQL Injection: `{url}`...", parse_mode='Markdown')
    
    result = await sql_injection_scan(url)
    await msg.edit_text(result, parse_mode='Markdown')

async def xss_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الرابط\nمثال: `/xss https://example.com/search?q=test`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    msg = await update.message.reply_text(f"⚡ جاري فحص XSS: `{url}`...", parse_mode='Markdown')
    
    result = await xss_scan(url)
    await msg.edit_text(result, parse_mode='Markdown')

async def lfi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الرابط\nمثال: `/lfi https://example.com/page.php?file=test`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    msg = await update.message.reply_text(f"📁 جاري فحص LFI: `{url}`...", parse_mode='Markdown')
    
    result = await lfi_scan(url)
    await msg.edit_text(result, parse_mode='Markdown')

async def redirect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الرابط\nمثال: `/redirect https://example.com/login?redirect=`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    msg = await update.message.reply_text(f"🔀 جاري فحص Open Redirect: `{url}`...", parse_mode='Markdown')
    
    result = await open_redirect_scan(url)
    await msg.edit_text(result, parse_mode='Markdown')

async def cmdi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الرابط\nمثال: `/cmdi https://example.com/ping?host=`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    msg = await update.message.reply_text(f"💻 جاري فحص Command Injection: `{url}`...", parse_mode='Markdown')
    
    result = await command_injection_scan(url)
    await msg.edit_text(result, parse_mode='Markdown')

async def secheaders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الرابط\nمثال: `/secheaders https://example.com`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    msg = await update.message.reply_text(f"🔒 جاري فحص Security Headers: `{url}`...", parse_mode='Markdown')
    
    result = await security_headers_scan(url)
    await msg.edit_text(result, parse_mode='Markdown')

async def cors_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الرابط\nمثال: `/cors https://example.com`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    msg = await update.message.reply_text(f"🌐 جاري فحص CORS: `{url}`...", parse_mode='Markdown')
    
    result = await cors_scan(url)
    await msg.edit_text(result, parse_mode='Markdown')

async def dirscan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الرابط\nمثال: `/dirscan https://example.com`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    msg = await update.message.reply_text(f"📂 جاري البحث عن مجلدات مخفية: `{url}`...\n⏳ قد يستغرق بعض الوقت...", parse_mode='Markdown')
    
    result = await dir_bruteforce(url)
    await msg.edit_text(result, parse_mode='Markdown')

async def portscan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(context.bot, update.effective_user.id): return
    if is_banned(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الهدف\nمثال: `/portscan example.com`", parse_mode='Markdown')
        return
    
    target = context.args[0]
    increment_command("portscan")
    msg = await update.message.reply_text(f"🔌 جاري فحص المنافذ: `{target}`...\n⏳ قد يستغرق بعض الوقت...", parse_mode='Markdown')
    
    result = await port_scan(target)
    await msg.edit_text(result, parse_mode='Markdown')

async def waf_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(context.bot, update.effective_user.id): return
    if is_banned(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الرابط\nمثال: `/waf https://example.com`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    increment_command("waf")
    msg = await update.message.reply_text(f"🛡️ جاري اكتشاف WAF: `{url}`...", parse_mode='Markdown')
    
    result = await waf_detect(url)
    await msg.edit_text(result, parse_mode='Markdown')

async def nmap_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(context.bot, update.effective_user.id): return
    if is_banned(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال عنوان IP أو المضيف\n💡 استخدام: `/nmap 192.168.1.1`", parse_mode='Markdown')
        return
    
    target = context.args[0]
    increment_command("nmap")
    msg = await update.message.reply_text(f"🔍 جاري مسح Nmap: `{target}`...\n⏳ قد يستغرق بعض الوقت...", parse_mode='Markdown')
    
    result = await nmap_scan(target, 'basic')
    await msg.edit_text(result, parse_mode='Markdown')

async def nmap_aggressive_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(context.bot, update.effective_user.id): return
    if is_banned(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال عنوان IP\n💡 استخدام: `/nmapagg 192.168.1.1`", parse_mode='Markdown')
        return
    
    target = context.args[0]
    increment_command("nmapagg")
    msg = await update.message.reply_text(f"⚡ جاري مسح عدواني: `{target}`...\n⏳ قد يستغرق وقتاً طويلاً...", parse_mode='Markdown')
    
    result = await nmap_aggressive_scan(target)
    await msg.edit_text(result, parse_mode='Markdown')

async def sqlmap_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(context.bot, update.effective_user.id): return
    if is_banned(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال رابط URL\n💡 استخدام: `/sqlmap https://example.com?id=1`", parse_mode='Markdown')
        return
    
    target_url = context.args[0]
    increment_command("sqlmap")
    msg = await update.message.reply_text(f"💾 جاري فحص SQLMap: `{target_url[:40]}...`\n⏳ قد يستغرق بعض الوقت...", parse_mode='Markdown')
    
    result = await sqlmap_scan(target_url)
    await msg.edit_text(result, parse_mode='Markdown')

async def sqlmap_deep_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(context.bot, update.effective_user.id): return
    if is_banned(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال رابط URL\n💡 استخدام: `/sqlmapdeep https://example.com`", parse_mode='Markdown')
        return
    
    target_url = context.args[0]
    increment_command("sqlmapdeep")
    msg = await update.message.reply_text(f"🔍 جاري فحص عميق: `{target_url[:40]}...`\n⏳ هذا قد يستغرق وقتاً طويلاً جداً...", parse_mode='Markdown')
    
    result = await sqlmap_deep_scan(target_url)
    await msg.edit_text(result, parse_mode='Markdown')

async def change_apk_package_name(decompile_dir, new_package=None):
    """غيّر package name في APK المفكّك - CRITICAL للعمل الصحيح"""
    if not new_package:
        import random, string
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        new_package = f"com.modified.{random_suffix}"
    
    manifest_path = os.path.join(decompile_dir, "AndroidManifest.xml")
    if not os.path.exists(manifest_path):
        return False
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    import re
    match = re.search(r'package="([^"]+)"', content)
    if not match:
        return False
    
    old_package = match.group(1)
    if old_package == new_package:
        return True
    
    # 1. غيّر في AndroidManifest.xml
    content = content.replace(f'package="{old_package}"', f'package="{new_package}"')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 2. غيّر في smali files
    smali_dir = os.path.join(decompile_dir, "smali")
    if os.path.exists(smali_dir):
        old_path = old_package.replace('.', '/')
        new_path = new_package.replace('.', '/')
        for root, dirs, files in os.walk(smali_dir):
            for file in files:
                if file.endswith('.smali'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            fcontent = f.read()
                        fcontent = fcontent.replace(f'L{old_path}/', f'L{new_path}/')
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(fcontent)
                    except:
                        pass
    
    return True

async def change_apk_app_name(decompile_dir, new_name):
    """غيّر اسم التطبيق في ALL strings.xml files (values, values-ar, values-en, etc.) - COMPREHENSIVE FIX"""
    import re
    success_count = 0
    
    # ابحث عن جميع ملفات strings.xml في جميع المجلدات
    res_dir = os.path.join(decompile_dir, "res")
    if not os.path.exists(res_dir):
        return False
    
    # ابحث في جميع مجلدات values (values, values-ar, values-en-US, إلخ)
    for root, dirs, files in os.walk(res_dir):
        if "strings.xml" in files:
            file_path = os.path.join(root, "strings.xml")
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # تحقق من وجود app_name
                if '<string name="app_name"' in content:
                    # استبدل app_name في جميع الأماكن
                    new_content = re.sub(
                        r'<string name="app_name"[^>]*>.*?</string>',
                        f'<string name="app_name">{new_name}</string>',
                        content,
                        flags=re.DOTALL
                    )
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    success_count += 1
            except Exception as e:
                logger.warning(f"Could not update {file_path}: {e}")
    
    return success_count > 0

async def remove_corrupted_pngs(decompile_dir):
    """حذف ملفات PNG التالفة التي تسبب خطأ libpng"""
    import os
    import struct
    
    res_dir = os.path.join(decompile_dir, "res")
    if not os.path.exists(res_dir):
        return 0
    
    corrupted_count = 0
    
    # ابحث عن جميع ملفات PNG
    for root, dirs, files in os.walk(res_dir):
        for file in files:
            if file.endswith('.png'):
                file_path = os.path.join(root, file)
                try:
                    # تحقق من signature PNG (أول 8 بايت)
                    with open(file_path, 'rb') as f:
                        header = f.read(8)
                    
                    # PNG magic number: 89 50 4E 47 0D 0A 1A 0A
                    if header != b'\x89PNG\r\n\x1a\n':
                        logger.warning(f"Removing corrupted PNG: {file_path}")
                        os.remove(file_path)
                        corrupted_count += 1
                except Exception as e:
                    logger.warning(f"Could not verify PNG {file_path}: {e}")
                    try:
                        os.remove(file_path)
                        corrupted_count += 1
                    except:
                        pass
    
    return corrupted_count

async def cleanup_broken_references(decompile_dir):
    """حذف المراجع المحطومة من public.xml عند حذف الملفات"""
    import os
    import re
    
    public_xml_path = os.path.join(decompile_dir, "res/values/public.xml")
    if not os.path.exists(public_xml_path):
        return
    
    try:
        with open(public_xml_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # حذف المراجع المحطومة (ic_notification و drawables غير الموجودة)
        content = re.sub(r'.*<public[^>]*name="ic_notification"[^>]*>.*?\n?', '', content)
        # تنظيف الأسطر الفارغة المتعددة
        content = re.sub(r'\n\s*\n+', '\n', content)
        
        with open(public_xml_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info("Cleaned up broken references from public.xml")
    except Exception as e:
        logger.warning(f"Could not cleanup public.xml: {e}")

async def bypass_ssl_pinning(decompile_dir):
    """كسر SSL Certificate Pinning في APK - إضافة Network Security Config"""
    import os
    
    # 1. حذف ملفات PNG التالفة قبل البناء
    await remove_corrupted_pngs(decompile_dir)
    
    # 2. تنظيف المراجع المحطومة من public.xml
    await cleanup_broken_references(decompile_dir)
    
    # 3. إنشاء مجلد xml إذا لم يكن موجوداً
    xml_dir = os.path.join(decompile_dir, "res", "xml")
    os.makedirs(xml_dir, exist_ok=True)
    
    # 4. إنشاء ملف network_security_config.xml
    network_security_config = """<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </base-config>
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">*</domain>
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </domain-config>
</network-security-config>"""
    
    config_path = os.path.join(xml_dir, "network_security_config.xml")
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(network_security_config)
    
    # 5. تحديث AndroidManifest.xml لربط الملف
    manifest_path = os.path.join(decompile_dir, "AndroidManifest.xml")
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest_content = f.read()
    
    # تحقق من وجود application tag
    import re
    if '<application' in manifest_content:
        # أضف networkSecurityConfig إلى application tag
        if 'android:networkSecurityConfig' not in manifest_content:
            # ابحث عن <application ... > واستبدلها
            manifest_content = re.sub(
                r'(<application\s+[^>]*?)(\s*>)',
                r'\1 android:networkSecurityConfig="@xml/network_security_config"\2',
                manifest_content
            )
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(manifest_content)
        
        return True
    
    return False

async def doh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(context.bot, update.effective_user.id): return
    if is_banned(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال النطاق\nمثال: `/doh example.com`", parse_mode='Markdown')
        return
    
    domain = context.args[0]
    increment_command("doh")
    msg = await update.message.reply_text(f"🌐 جاري فحص DNS over HTTPS: `{domain}`...", parse_mode='Markdown')
    result = await doh_lookup(domain)
    await msg.edit_text(result, parse_mode='Markdown')

async def ip_geo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(context.bot, update.effective_user.id): return
    if is_banned(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال IP\nمثال: `/ipgeo 8.8.8.8`", parse_mode='Markdown')
        return
    
    ip = context.args[0]
    increment_command("ipgeo")
    msg = await update.message.reply_text(f"🛰️ جاري تحديد موقع IP: `{ip}`...", parse_mode='Markdown')
    result = await ip_geo_lookup(ip)
    await msg.edit_text(result, parse_mode='Markdown')

async def httpsec_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(context.bot, update.effective_user.id): return
    if is_banned(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الرابط\nمثال: `/httpsec example.com`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    increment_command("httpsec")
    msg = await update.message.reply_text(f"🔒 جاري فحص أمان HTTP: `{url}`...", parse_mode='Markdown')
    result = await http_security_check(url)
    await msg.edit_text(result, parse_mode='Markdown')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(context.bot, update.effective_user.id): return
    if is_banned(update.effective_user.id): return
    
    try:
        msg = await update.message.reply_text("📸 جاري استخراج بيانات EXIF من الصورة...")
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        
        # We try to import inside to catch potential binary errors gracefully
        from modules.exif_osint import extract_exif
        result = await extract_exif(bytes(image_bytes))
        await msg.edit_text(result, parse_mode='Markdown')
    except ImportError:
        await msg.edit_text("❌ عذراً، أداة تحليل الصور غير متوفرة حالياً بسبب نقص في مكتبات النظام الأساسية. جاري العمل على حلها.")
    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ أثناء معالجة الصورة: {str(e)}")


async def dnsrecords_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال النطاق\nمثال: `/dnsrecords example.com`", parse_mode='Markdown')
        return
    domain = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري فحص DNS: `{domain}`...", parse_mode='Markdown')
    result = await dns_records(domain)
    await msg.edit_text(result, parse_mode='Markdown')

async def sslexpiry_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال النطاق", parse_mode='Markdown')
        return
    domain = context.args[0]
    msg = await update.message.reply_text(f"🔐 جاري فحص SSL...", parse_mode='Markdown')
    result = await ssl_expiry(domain)
    await msg.edit_text(result, parse_mode='Markdown')

async def serverinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال النطاق", parse_mode='Markdown')
        return
    domain = context.args[0]
    msg = await update.message.reply_text(f"🖥️ جاري جلب معلومات السيرفر...", parse_mode='Markdown')
    result = await server_info(domain)
    await msg.edit_text(result, parse_mode='Markdown')

async def reverseip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال IP", parse_mode='Markdown')
        return
    ip = context.args[0]
    result = await reverse_ip(ip)
    await update.message.reply_text(result, parse_mode='Markdown')

async def cdn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال النطاق", parse_mode='Markdown')
        return
    domain = context.args[0]
    result = await cdn_detection(domain)
    await update.message.reply_text(result, parse_mode='Markdown')

async def techstack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال النطاق", parse_mode='Markdown')
        return
    domain = context.args[0]
    msg = await update.message.reply_text(f"🛠️ جاري كشف التقنيات...", parse_mode='Markdown')
    result = await tech_stack(domain)
    await msg.edit_text(result, parse_mode='Markdown')

async def cmsdetect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال النطاق", parse_mode='Markdown')
        return
    domain = context.args[0]
    msg = await update.message.reply_text(f"🔍 جاري الكشف عن CMS...", parse_mode='Markdown')
    result = await cms_detect(domain)
    await msg.edit_text(result, parse_mode='Markdown')

async def subenum_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال النطاق", parse_mode='Markdown')
        return
    domain = context.args[0]
    msg = await update.message.reply_text(f"📊 جاري عد Subdomains...", parse_mode='Markdown')
    result = await subdomain_enum(domain)
    await msg.edit_text(result, parse_mode='Markdown')

async def openports_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال Host", parse_mode='Markdown')
        return
    host = context.args[0]
    result = await open_ports_check(host)
    await update.message.reply_text(result, parse_mode='Markdown')

async def adminfinder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال النطاق", parse_mode='Markdown')
        return
    domain = context.args[0]
    msg = await update.message.reply_text(f"🔑 جاري البحث...", parse_mode='Markdown')
    result = await admin_finder(domain)
    await msg.edit_text(result, parse_mode='Markdown')

async def dirfinder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال النطاق", parse_mode='Markdown')
        return
    domain = context.args[0]
    msg = await update.message.reply_text(f"📁 جاري البحث...", parse_mode='Markdown')
    result = await dir_finder(domain)
    await msg.edit_text(result, parse_mode='Markdown')

async def sensitivefiles_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال النطاق", parse_mode='Markdown')
        return
    domain = context.args[0]
    msg = await update.message.reply_text(f"⚠️ جاري الفحص...", parse_mode='Markdown')
    result = await sensitive_files(domain)
    await msg.edit_text(result, parse_mode='Markdown')

async def banner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال Host", parse_mode='Markdown')
        return
    host = context.args[0]
    msg = await update.message.reply_text(f"🎫 جاري جلب البانر: `{host}`...", parse_mode='Markdown')
    result = await banner_grabbing(host)
    await msg.edit_text(result, parse_mode='Markdown')

async def emailextract_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال النطاق", parse_mode='Markdown')
        return
    domain = context.args[0]
    msg = await update.message.reply_text(f"📧 جاري الاستخراج...", parse_mode='Markdown')
    result = await email_extract(domain)
    await msg.edit_text(result, parse_mode='Markdown')

async def phoneextract_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال النطاق", parse_mode='Markdown')
        return
    domain = context.args[0]
    msg = await update.message.reply_text(f"📱 جاري الاستخراج...", parse_mode='Markdown')
    result = await phone_extract(domain)
    await msg.edit_text(result, parse_mode='Markdown')

async def sitemap_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال النطاق", parse_mode='Markdown')
        return
    domain = context.args[0]
    msg = await update.message.reply_text(f"🗺️ جاري التحليل...", parse_mode='Markdown')
    result = await sitemap_analysis(domain)
    await msg.edit_text(result, parse_mode='Markdown')

async def securitytxt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال النطاق", parse_mode='Markdown')
        return
    domain = context.args[0]
    result = await security_txt(domain)
    await update.message.reply_text(result, parse_mode='Markdown')

async def md5_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال النص للتشفير", parse_mode='Markdown')
        return
    text = ' '.join(context.args)
    result = await hash_md5(text)
    await update.message.reply_text(result, parse_mode='Markdown')

async def md5decode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الـ Hash", parse_mode='Markdown')
        return
    hash_val = context.args[0]
    msg = await update.message.reply_text(f"🔓 جاري فك التشفير...", parse_mode='Markdown')
    result = await hash_decode(hash_val)
    await msg.edit_text(result, parse_mode='Markdown')

async def reversedns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال IP", parse_mode='Markdown')
        return
    ip = context.args[0]
    result = await reverse_dns_lookup(ip)
    await update.message.reply_text(result, parse_mode='Markdown')


async def sqlmap_dbs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال رابط URL", parse_mode='Markdown')
        return
    target_url = context.args[0]
    msg = await update.message.reply_text(f"🗄️ جاري استخراج قواعد البيانات: `{target_url[:40]}...`...", parse_mode='Markdown')
    result = await sqlmap_exploit_db(target_url)
    await msg.edit_text(result, parse_mode='Markdown')

async def sqlmap_tables_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❌ يرجى إدخال الرابط واسم القاعدة\nمثال: `/sqlmaptables [url] [db]`", parse_mode='Markdown')
        return
    url, db = context.args[0], context.args[1]
    msg = await update.message.reply_text(f"📋 جاري استخراج الجداول من `{db}`...", parse_mode='Markdown')
    result = await sqlmap_exploit_tables(url, db)
    await msg.edit_text(result, parse_mode='Markdown')

async def sqlmap_columns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text("❌ يرجى إدخال الرابط والقاعدة والجدول\nمثال: `/sqlmapcolumns [url] [db] [table]`", parse_mode='Markdown')
        return
    url, db, table = context.args[0], context.args[1], context.args[2]
    msg = await update.message.reply_text(f"📊 جاري استخراج الأعمدة من `{table}`...", parse_mode='Markdown')
    result = await sqlmap_exploit_columns(url, db, table)
    await msg.edit_text(result, parse_mode='Markdown')

async def sqlmap_dump_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text("❌ يرجى إدخال الرابط والقاعدة والجدول\nمثال: `/sqlmapdump [url] [db] [table]`", parse_mode='Markdown')
        return
    url, db, table = context.args[0], context.args[1], context.args[2]
    msg = await update.message.reply_text(f"📥 جاري سحب البيانات من `{table}`...", parse_mode='Markdown')
    result = await sqlmap_dump_data(url, db, table)
    await msg.edit_text(result, parse_mode='Markdown')

async def sqlmap_shell_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال رابط URL", parse_mode='Markdown')
        return
    url = context.args[0]
    msg = await update.message.reply_text(f"🐚 محاولة الحصول على OS Shell: `{url[:40]}...`...", parse_mode='Markdown')
    result = await sqlmap_os_shell(url)
    await msg.edit_text(result, parse_mode='Markdown')


async def nmap_svc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الهدف", parse_mode='Markdown')
        return
    target = context.args[0]
    msg = await update.message.reply_text(f"🔧 جاري فحص الخدمات: `{target}`...", parse_mode='Markdown')
    result = await nmap_service_scan(target)
    await msg.edit_text(result, parse_mode='Markdown')

async def nmap_vuln_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الهدف", parse_mode='Markdown')
        return
    target = context.args[0]
    msg = await update.message.reply_text(f"🛡️ جاري فحص الثغرات (NSE): `{target}`...", parse_mode='Markdown')
    result = await nmap_vuln_scan(target)
    await msg.edit_text(result, parse_mode='Markdown')

async def nmap_brute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الهدف", parse_mode='Markdown')
        return
    target = context.args[0]
    msg = await update.message.reply_text(f"🔑 جاري فحص التخمين: `{target}`...", parse_mode='Markdown')
    result = await nmap_brute_scan(target)
    await msg.edit_text(result, parse_mode='Markdown')

async def nmap_disc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الهدف", parse_mode='Markdown')
        return
    target = context.args[0]
    msg = await update.message.reply_text(f"📡 جاري اكتشاف المعلومات: `{target}`...", parse_mode='Markdown')
    result = await nmap_discovery_scan(target)
    await msg.edit_text(result, parse_mode='Markdown')

async def nmap_full_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الهدف", parse_mode='Markdown')
        return
    target = context.args[0]
    msg = await update.message.reply_text(f"🌐 جاري فحص جميع المنافذ (65535): `{target}`...", parse_mode='Markdown')
    result = await nmap_scan(target, 'full')
    await msg.edit_text(result, parse_mode='Markdown')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الصور المرسلة لاستخراج EXIF أو البحث العكسي"""
    if not update.effective_user:
        return
    user_id = update.effective_user.id
    user_state = USER_STATES.get(user_id)
    
    photo_file = await update.message.photo[-1].get_file()
    
    # Check for APK icon replacement state
    if user_state and user_state.startswith("waiting_for_icon_"):
        is_auto = "_auto_" in user_state
        session_id = user_state.split("_")[-1]
        apk_info = context.user_data.get('apks', {}).get(session_id)
        if not apk_info:
            await update.message.reply_text("❌ انتهت صلاحية الجلسة.")
            USER_STATES.pop(user_id, None)
            return
        
        msg = await update.message.reply_text("🔍 جاري معالجة واستبدال الأيقونة...")
        temp_dir = apk_info['dir']
        decompile_dir = os.path.join(temp_dir, "full_decompile")
        apk_path = apk_info['path']
        new_icon_path = os.path.join(temp_dir, "new_icon.png")
        
        # Create analyzer instance
        from modules.app_osint import AdvancedAPKAnalyzer
        analyzer = AdvancedAPKAnalyzer()
        
        # Download image
        temp_img_path = os.path.join(temp_dir, "temp_img.tmp")
        await photo_file.download_to_drive(temp_img_path)
        
        # Verify file exists
        if not os.path.exists(temp_img_path) or os.path.getsize(temp_img_path) == 0:
            logger.error("Image file is empty or missing")
            await msg.edit_text("❌ فشل في استقبال الصورة. حاول مرة أخرى.")
            USER_STATES.pop(user_id, None)
            return
        
        # Convert to PNG using ImageMagick (more reliable than other methods)
        convert_cmd = f"convert {temp_img_path} -quality 95 {new_icon_path}"
        result = await analyzer.run_command(convert_cmd)
        
        # Cleanup temp file
        try:
            os.remove(temp_img_path)
        except:
            pass
        
        # Verify PNG was created
        if not os.path.exists(new_icon_path) or os.path.getsize(new_icon_path) == 0:
            logger.error(f"Failed to convert image to PNG: {result}")
            await msg.edit_text("❌ فشل تحويل الصورة. تأكد أنها صورة صحيحة.")
            USER_STATES.pop(user_id, None)
            return
        
        import shutil
        # Find and replace all icon files
        cmd = f"find {decompile_dir}/res -name '*icon*.png' -o -name '*ic_launcher*.png'"
        icon_files_str = await analyzer.run_command(cmd)
        icon_files = [f.strip() for f in icon_files_str.split('\n') if f.strip() and os.path.exists(f.strip())]
        
        if not icon_files:
            # Try fallback to any png in drawable
            cmd = f"find {decompile_dir}/res/drawable* -name '*.png' | head -10"
            icon_files_str = await analyzer.run_command(cmd)
            icon_files = [f.strip() for f in icon_files_str.split('\n') if f.strip() and os.path.exists(f.strip())]

        replaced_count = 0
        for old_icon in icon_files:
            shutil.copy(new_icon_path, old_icon)
            replaced_count += 1
        
        if replaced_count > 0:
            if is_auto:
                await msg.edit_text("✅ تم استبدال الأيقونة بنجاح. جاري تطبيق التعديلات... ⏳")
                
                # غيّر package name (CRITICAL!)
                await change_apk_package_name(decompile_dir)
                
                # غيّر اسم التطبيق أيضاً إذا تم تعيينه (FIX: persist app name changes)
                if 'new_app_name' in apk_info:
                    await change_apk_app_name(decompile_dir, apk_info['new_app_name'])
                
                await msg.edit_text("✅ تم تطبيق جميع التعديلات. جاري إعادة بناء التطبيق... ⏳")
                
                # حذف الصور التالفة المعروفة قبل البناء
                cleanup_cmd = f"find {decompile_dir} -name '*ic_notification*.png' -delete 2>/dev/null; find {decompile_dir} -name '*ic_launcher*.png' -type f -exec file {{}} \\; 2>/dev/null | grep -v 'PNG image' | cut -d: -f1 | xargs rm -f 2>/dev/null"
                await analyzer.run_command(cleanup_cmd)
                
                # حذف المراجع من public.xml
                public_xml_path = os.path.join(decompile_dir, "res/values/public.xml")
                if os.path.exists(public_xml_path):
                    try:
                        import re
                        with open(public_xml_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        # حذف السطر بالكامل الذي يحتوي على ic_notification
                        content = re.sub(r'.*<public\s+type="drawable"\s+name="ic_notification".*\n?', '', content)
                        # تنظيف الأسطر الفارغة المتعددة
                        content = re.sub(r'\n\s*\n+', '\n', content)
                        with open(public_xml_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        logger.info("Updated public.xml - removed ic_notification reference")
                    except Exception as e:
                        logger.warning(f"Could not update public.xml: {e}")
                
                output_apk = os.path.join(temp_dir, f"modified_{apk_info['name']}")
                build_cmd = f"apktool b {decompile_dir} -o {output_apk} --use-aapt1 2>&1"
                build_result = await analyzer.run_command(build_cmd)
                
                if os.path.exists(output_apk):
                    await msg.edit_text("✅ اكتمل البناء بنجاح! جاري إرسال التطبيق المعدل... 📤")
                    with open(output_apk, 'rb') as f:
                        await context.bot.send_document(
                            chat_id=update.effective_chat.id,
                            document=f,
                            filename=os.path.basename(output_apk),
                            caption=f"✅ تم تعديل الاسم والأيقونة لـ `{apk_info['name']}` بنجاح."
                        )
                elif "libpng error" in build_result or "PNG image" in build_result:
                    # إذا فشل بسبب صور تالفة، حاول بناء بدون موارد
                    await msg.edit_text("⚠️ محاولة بناء بدون موارد...")
                    build_cmd2 = f"apktool b {decompile_dir} -o {output_apk} --use-aapt1 --no-res 2>&1"
                    build_result2 = await analyzer.run_command(build_cmd2)
                    
                    if os.path.exists(output_apk):
                        await msg.edit_text("✅ اكتمل البناء بدون موارد! جاري الإرسال... 📤")
                        with open(output_apk, 'rb') as f:
                            await context.bot.send_document(
                                chat_id=update.effective_chat.id,
                                document=f,
                                filename=os.path.basename(output_apk),
                                caption=f"⚠️ تم البناء بدون موارد (بعض الصور قد تكون مفقودة)"
                            )
                    else:
                        await msg.edit_text(f"❌ فشل البناء:\n```\n{build_result2[:1500]}\n```", parse_mode='Markdown')
                else:
                    await msg.edit_text(f"❌ فشل البناء التلقائي:\n```\n{build_result[:1500]}\n```", parse_mode='Markdown')
            else:
                await msg.edit_text(
                    f"✅ تم استبدال {replaced_count} أيقونة بنجاح.\n\n"
                    f"📁 استخدم زر البناء (Build) لإعادة تجميع التطبيق بالأيقونة الجديدة."
                )
        else:
            await msg.edit_text("❌ لم أتمكن من العثور على أيقونات لاستبدالها.")
        
        USER_STATES.pop(user_id, None)
        return

    # إذا كان المستخدم يريد البحث العكسي
    if user_state == "imgsearch":
        msg = await update.message.reply_text("🔍 جاري رفع الصورة وتأمين التوكن...")
        img_bytes = await photo_file.download_as_bytearray()
        from modules.reverse_image_osint import get_reverse_image_links
        result = await get_reverse_image_links(bytes(img_bytes))
        await msg.edit_text(result, parse_mode='Markdown', disable_web_page_preview=True)
        USER_STATES.pop(user_id, None)
        return

    # الوضع الافتراضي أو exif
    msg = await update.message.reply_text("📸 جاري تحليل بيانات الصورة المستخرجة (EXIF)...", parse_mode='Markdown')
    
    # Download photo as bytes
    img_bytes = await photo_file.download_as_bytearray()
    
    try:
        from modules.exif_osint import extract_exif
        result = await extract_exif(bytes(img_bytes))
        await msg.edit_text(result, parse_mode='Markdown', disable_web_page_preview=True)
    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ أثناء تحليل EXIF: {str(e)}")
    
    USER_STATES.pop(user_id, None)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    doc = update.message.document
    
    if not doc:
        return

    user_id = user.id
    # Log file reception for debugging
    logger.info(f"Received document: {doc.file_name} ({doc.mime_type}) from {user_id}")
    
    # Check file size (Telegram Bot API limit for getFile is 20MB)
    if doc.file_size > 20 * 1024 * 1024:
        await update.message.reply_text(f"⚠️ الملف `{doc.file_name}` كبير جداً ({doc.file_size / (1024*1024):.1f}MB).\nبوتات تليجرام العادية تدعم ملفات حتى 20MB فقط للتحليل التلقائي. يرجى إرسال ملف أصغر.")
        return
    
    # Check if user is waiting for an icon image for APK modification
    user_state = USER_STATES.get(user_id)
    image_mimes = {'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'}
    is_image = doc.mime_type in image_mimes or doc.file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))
    
    if user_state and user_state.startswith("waiting_for_icon_") and is_image:
        # User is waiting for an icon image, process it as APK icon replacement
        try:
            file = await context.bot.get_file(doc.file_id)
            is_auto = "_auto_" in user_state
            session_id = user_state.split("_")[-1]
            apk_info = context.user_data.get('apks', {}).get(session_id)
            if not apk_info:
                await update.message.reply_text("❌ انتهت صلاحية الجلسة.")
                USER_STATES.pop(user_id, None)
                return
            
            msg = await update.message.reply_text("🔍 جاري معالجة واستبدال الأيقونة...")
            temp_dir = apk_info['dir']
            decompile_dir = os.path.join(temp_dir, "full_decompile")
            apk_path = apk_info['path']
            new_icon_path = os.path.join(temp_dir, "new_icon.png")
            
            # Create analyzer instance
            from modules.app_osint import AdvancedAPKAnalyzer
            analyzer = AdvancedAPKAnalyzer()
            
            # Download image
            temp_img_path = os.path.join(temp_dir, "temp_img.tmp")
            await file.download_to_drive(temp_img_path)
            
            # Verify file exists
            if not os.path.exists(temp_img_path) or os.path.getsize(temp_img_path) == 0:
                logger.error("Image file is empty or missing")
                await msg.edit_text("❌ فشل في استقبال الصورة. حاول مرة أخرى.")
                USER_STATES.pop(user_id, None)
                return
            
            # Convert to PNG using ImageMagick
            convert_cmd = f"convert {temp_img_path} -quality 95 {new_icon_path}"
            result = await analyzer.run_command(convert_cmd)
            
            # Cleanup temp file
            try:
                os.remove(temp_img_path)
            except:
                pass
            
            # Verify PNG was created
            if not os.path.exists(new_icon_path) or os.path.getsize(new_icon_path) == 0:
                logger.error(f"Failed to convert image to PNG: {result}")
                await msg.edit_text("❌ فشل تحويل الصورة. تأكد أنها صورة صحيحة.")
                USER_STATES.pop(user_id, None)
                return
            
            import shutil
            # Find and replace all icon files
            cmd = f"find {decompile_dir}/res -name '*icon*.png' -o -name '*ic_launcher*.png'"
            icon_files_str = await analyzer.run_command(cmd)
            icon_files = [f.strip() for f in icon_files_str.split('\n') if f.strip() and os.path.exists(f.strip())]
            
            if not icon_files:
                # Try fallback to any png in drawable
                cmd = f"find {decompile_dir}/res/drawable* -name '*.png' | head -10"
                icon_files_str = await analyzer.run_command(cmd)
                icon_files = [f.strip() for f in icon_files_str.split('\n') if f.strip() and os.path.exists(f.strip())]

            replaced_count = 0
            for old_icon in icon_files:
                shutil.copy(new_icon_path, old_icon)
                replaced_count += 1
            
            if replaced_count > 0:
                if is_auto:
                    await msg.edit_text("✅ تم استبدال الأيقونة بنجاح. جاري تطبيق التعديلات... ⏳")
                    
                    # غيّر اسم التطبيق أيضاً إذا تم تعيينه (FIX: persist app name changes)
                    if 'new_app_name' in apk_info:
                        await change_apk_app_name(decompile_dir, apk_info['new_app_name'])
                    
                    # حذف الصور التالفة المعروفة قبل البناء
                    cleanup_cmd = f"find {decompile_dir} -name '*ic_notification*.png' -delete 2>/dev/null; find {decompile_dir} -name '*ic_launcher*.png' -type f -exec file {{}} \\; 2>/dev/null | grep -v 'PNG image' | cut -d: -f1 | xargs rm -f 2>/dev/null"
                    await analyzer.run_command(cleanup_cmd)
                    
                    # حذف المراجع من public.xml
                    public_xml_path = os.path.join(decompile_dir, "res/values/public.xml")
                    if os.path.exists(public_xml_path):
                        try:
                            import re
                            with open(public_xml_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            # حذف السطر بالكامل الذي يحتوي على ic_notification
                            content = re.sub(r'.*<public\s+type="drawable"\s+name="ic_notification".*\n?', '', content)
                            # تنظيف الأسطر الفارغة المتعددة
                            content = re.sub(r'\n\s*\n+', '\n', content)
                            with open(public_xml_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            logger.info("Updated public.xml - removed ic_notification reference")
                        except Exception as e:
                            logger.warning(f"Could not update public.xml: {e}")
                    
                    output_apk = os.path.join(temp_dir, f"modified_{apk_info['name']}")
                    build_cmd = f"apktool b {decompile_dir} -o {output_apk} --use-aapt1 2>&1"
                    build_result = await analyzer.run_command(build_cmd)
                    
                    if os.path.exists(output_apk):
                        await msg.edit_text("✅ اكتمل البناء بنجاح! جاري إرسال التطبيق المعدل... 📤")
                        with open(output_apk, 'rb') as f:
                            await context.bot.send_document(
                                chat_id=update.effective_chat.id,
                                document=f,
                                filename=os.path.basename(output_apk),
                                caption=f"✅ تم تعديل الاسم والأيقونة لـ `{apk_info['name']}` بنجاح."
                            )
                    elif "libpng error" in build_result or "PNG image" in build_result:
                        # إذا فشل بسبب صور تالفة، حاول بناء بدون موارد
                        await msg.edit_text("⚠️ محاولة بناء بدون موارد...")
                        build_cmd2 = f"apktool b {decompile_dir} -o {output_apk} --use-aapt1 --no-res 2>&1"
                        build_result2 = await analyzer.run_command(build_cmd2)
                        
                        if os.path.exists(output_apk):
                            await msg.edit_text("✅ اكتمل البناء بدون موارد! جاري الإرسال... 📤")
                            with open(output_apk, 'rb') as f:
                                await context.bot.send_document(
                                    chat_id=update.effective_chat.id,
                                    document=f,
                                    filename=os.path.basename(output_apk),
                                    caption=f"⚠️ تم البناء بدون موارد (بعض الصور قد تكون مفقودة)"
                                )
                        else:
                            await msg.edit_text(f"❌ فشل البناء:\n```\n{build_result2[:1500]}\n```", parse_mode='Markdown')
                    else:
                        await msg.edit_text(f"❌ فشل البناء التلقائي:\n```\n{build_result[:1500]}\n```", parse_mode='Markdown')
                else:
                    await msg.edit_text(
                        f"✅ تم استبدال {replaced_count} أيقونة بنجاح.\n\n"
                        f"📁 استخدم زر البناء (Build) لإعادة تجميع التطبيق بالأيقونة الجديدة."
                    )
            else:
                await msg.edit_text("❌ لم أتمكن من العثور على أيقونات لاستبدالها.")
            
            USER_STATES.pop(user_id, None)
            return
        except Exception as e:
            logger.error(f"Error handling icon replacement from document: {e}")
            await update.message.reply_text(f"❌ حدث خطأ أثناء معالجة الأيقونة: {str(e)}")
            USER_STATES.pop(user_id, None)
            return

    # Check if it's an image file sent as document (and not waiting for icon)
    if is_image:
        await update.message.reply_text(
            f"📸 تم استقبال صورة: `{doc.file_name}`\n\n"
            f"يرجى استخدام البحث العكسي للصور أو تحليل EXIF عن طريق إرسال الصورة مباشرة (بدون ملف).\n\n"
            f"أو استخدم الأوامر التالية:\n"
            f"• `/imgsearch` - بحث عكسي عن الصورة\n"
            f"• `/exif` - تحليل البيانات الوصفية"
        )
        return
    
    if doc.file_name.lower().endswith('.apk') or doc.mime_type == 'application/vnd.android.package-archive':
        try:
            file = await context.bot.get_file(doc.file_id)
            
            # Create user unique temp dir for concurrency
            import uuid
            session_id = str(uuid.uuid4())[:8]
            temp_dir = f"temp/apk_{user_id}_{session_id}"
            os.makedirs(temp_dir, exist_ok=True)
            apk_path = os.path.join(temp_dir, doc.file_name)
            
            await update.message.reply_text(f"📥 جاري تحميل ومعالجة: `{doc.file_name}`...")
            await file.download_to_drive(apk_path)
            
            # تحقق من أن الملف تم حفظه بشكل صحيح
            if not os.path.exists(apk_path) or os.path.getsize(apk_path) == 0:
                logger.error(f"APK file not properly saved: {apk_path}")
                await update.message.reply_text(f"❌ فشل في حفظ الملف. حاول مرة أخرى.")
                return
            
            # Save path and metadata in user data
            if 'apks' not in context.user_data:
                context.user_data['apks'] = {}
            
            context.user_data['apks'][session_id] = {
                'path': apk_path,
                'name': doc.file_name,
                'dir': temp_dir
            }
            context.user_data['current_apk_session'] = session_id
            
            text = f"✅ تم استلام ملف APK: `{doc.file_name}`\n\nماذا تريد أن أفعل بهذا التطبيق؟ اختر أداة من القائمة:"
            keyboard = [
                [
                    InlineKeyboardButton("📊 معلومات (Info)", callback_data=f"apk_cmd_info_{session_id}"),
                    InlineKeyboardButton("📜 مانیفست (Manifest)", callback_data=f"apk_cmd_manifest_{session_id}"),
                ],
                [
                    InlineKeyboardButton("🔐 أسرار (Secrets)", callback_data=f"apk_cmd_secrets_{session_id}"),
                    InlineKeyboardButton("🔗 روابط (URLs)", callback_data=f"apk_cmd_urls_{session_id}"),
                ],
                [
                    InlineKeyboardButton("🛠️ تفكيك (Decompile)", callback_data=f"apk_cmd_decompile_{session_id}"),
                    InlineKeyboardButton("🛡️ الصلاحيات (Perms)", callback_data=f"apk_cmd_perms_{session_id}"),
                ],
                [
                    InlineKeyboardButton("🔓 فك التشفير (Decrypt)", callback_data=f"apk_cmd_decrypt_{session_id}"),
                    InlineKeyboardButton("📜 الشهادة (Cert)", callback_data=f"apk_cmd_cert_{session_id}"),
                ],
                [
                    InlineKeyboardButton("🎬 الأنشطة (Activities)", callback_data=f"apk_cmd_activities_{session_id}"),
                    InlineKeyboardButton("🖼️ الموارد (Resources)", callback_data=f"apk_cmd_resources_{session_id}"),
                ],
                [
                    InlineKeyboardButton("📚 المكتبات (Libs)", callback_data=f"apk_cmd_libs_{session_id}"),
                    InlineKeyboardButton("🛡️ الحماية (Protection)", callback_data=f"apk_cmd_protection_{session_id}"),
                ],
                [
                    InlineKeyboardButton("🛠️ إعادة بناء (Build)", callback_data=f"apk_cmd_build_{session_id}"),
                    InlineKeyboardButton("📋 تقرير (Report)", callback_data=f"apk_cmd_report_{session_id}"),
                ],
                [
                    InlineKeyboardButton("🔥 تحليل كامل (Full)", callback_data=f"apk_cmd_full_{session_id}"),
                ],
                [
                    InlineKeyboardButton("🎨📛 تعديل الهوية (Edit Icon & Name)", callback_data=f"apk_cmd_editall_{session_id}"),
                    InlineKeyboardButton("🔐 توقيع APK (Sign)", callback_data=f"apk_cmd_sign_{session_id}"),
                ],
                [
                    InlineKeyboardButton("🔓 كسر SSL (Bypass SSL)", callback_data=f"apk_cmd_ssl_{session_id}"),
                    InlineKeyboardButton("💬 نص عند الفتح (Splash)", callback_data=f"apk_cmd_splash_{session_id}"),
                ],
                [
                    InlineKeyboardButton("📥 تحميل من رابط", callback_data=f"apk_cmd_loadurl_{session_id}"),
                    InlineKeyboardButton("❌ إلغاء وحذف", callback_data=f"apk_cmd_cancel_{session_id}"),
                ]
            ]
            await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            logger.error(f"Error getting file: {e}")
            await update.message.reply_text(f"❌ فشل تحميل الملف من تليجرام: {str(e)}")
    else:
        await update.message.reply_text(f"❓ الملف `{doc.file_name}` ليس تطبيق أندرويد (.apk). البوت يدعم تحليل تطبيقات APK فقط حالياً.")

async def show_apk_menu(query, apk_info, session_id):
    """عرض القائمة الرئيسية للـ APK"""
    text = f"✅ تم استلام ملف APK: `{apk_info['name']}`\n\nماذا تريد أن أفعل بهذا التطبيق؟ اختر أداة من القائمة:"
    keyboard = [
        [
            InlineKeyboardButton("📊 معلومات (Info)", callback_data=f"apk_cmd_info_{session_id}"),
            InlineKeyboardButton("📜 مانیفست (Manifest)", callback_data=f"apk_cmd_manifest_{session_id}"),
        ],
        [
            InlineKeyboardButton("🔐 أسرار (Secrets)", callback_data=f"apk_cmd_secrets_{session_id}"),
            InlineKeyboardButton("🔗 روابط (URLs)", callback_data=f"apk_cmd_urls_{session_id}"),
        ],
        [
            InlineKeyboardButton("🛠️ تفكيك (Decompile)", callback_data=f"apk_cmd_decompile_{session_id}"),
            InlineKeyboardButton("🛡️ الصلاحيات (Perms)", callback_data=f"apk_cmd_perms_{session_id}"),
        ],
        [
            InlineKeyboardButton("🔓 فك التشفير (Decrypt)", callback_data=f"apk_cmd_decrypt_{session_id}"),
            InlineKeyboardButton("📜 الشهادة (Cert)", callback_data=f"apk_cmd_cert_{session_id}"),
        ],
        [
            InlineKeyboardButton("🎬 الأنشطة (Activities)", callback_data=f"apk_cmd_activities_{session_id}"),
            InlineKeyboardButton("🖼️ الموارد (Resources)", callback_data=f"apk_cmd_resources_{session_id}"),
        ],
        [
            InlineKeyboardButton("📚 المكتبات (Libs)", callback_data=f"apk_cmd_libs_{session_id}"),
            InlineKeyboardButton("🛡️ الحماية (Protection)", callback_data=f"apk_cmd_protection_{session_id}"),
        ],
        [
            InlineKeyboardButton("🛠️ إعادة بناء (Build)", callback_data=f"apk_cmd_build_{session_id}"),
            InlineKeyboardButton("📋 تقرير (Report)", callback_data=f"apk_cmd_report_{session_id}"),
        ],
        [
            InlineKeyboardButton("🔥 تحليل كامل (Full)", callback_data=f"apk_cmd_full_{session_id}"),
        ],
        [
            InlineKeyboardButton("🎨📛 تعديل الهوية (Edit Icon & Name)", callback_data=f"apk_cmd_editall_{session_id}"),
            InlineKeyboardButton("🔐 توقيع APK (Sign)", callback_data=f"apk_cmd_sign_{session_id}"),
        ],
        [
            InlineKeyboardButton("🔓 كسر SSL (Bypass SSL)", callback_data=f"apk_cmd_ssl_{session_id}"),
            InlineKeyboardButton("💬 نص عند الفتح (Splash)", callback_data=f"apk_cmd_splash_{session_id}"),
        ],
        [
            InlineKeyboardButton("📥 تحميل من رابط", callback_data=f"apk_cmd_loadurl_{session_id}"),
            InlineKeyboardButton("❌ إلغاء وحذف", callback_data=f"apk_cmd_cancel_{session_id}"),
        ]
    ]
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def apk_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    callback_data = query.data.split("_")
    
    # Callback format: apk_cmd_[action]_[session_id]
    if len(callback_data) < 4:
        await query.edit_message_text("❌ بيانات غير صالحة.")
        return
        
    action = callback_data[2]
    session_id = callback_data[3]
    
    # تحقق من أن apks موجود في user_data
    if 'apks' not in context.user_data:
        context.user_data['apks'] = {}
    
    apk_info = context.user_data.get('apks', {}).get(session_id)
    
    if not apk_info:
        await query.edit_message_text("❌ انتهت صلاحية الجلسة. يرجى إرسال الملف مرة أخرى أو استخدم `/apkurl` لتحميله من رابط.")
        return

    apk_path = apk_info['path']
    temp_dir = apk_info['dir']
    
    if not os.path.exists(apk_path):
        if action != "cancel" and action != "back":
            await query.edit_message_text("❌ لم يتم العثور على ملف APK. يرجى إعادة إرساله.")
            return

    analyzer = AdvancedAPKAnalyzer()
    
    if action == "back":
        await show_apk_menu(query, apk_info, session_id)
        return
    
    if action == "cancel":
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        context.user_data['apks'].pop(session_id, None)
        await query.edit_message_text(f"🗑️ تم إلغاء العملية وحذف الملفات المؤقتة لـ `{apk_info['name']}`.")
        return

    msg = await query.edit_message_text(f"⏳ جاري تنفيذ `{action}` على `{apk_info['name']}`... قد يستغرق هذا وقتاً.")
    
    try:
        # Launch analysis in background to not block the bot
        if action == "info":
            # Use apktool instead of aapt since aapt may not be available
            result = await analyzer.run_command(f"apktool d {apk_path} -o {os.path.join(temp_dir, 'info_temp')} -f --no-src 2>&1 | head -n 20")
            if not result.strip():
                result = f"✅ تم فك التشفير بنجاح. استخدم الأوامر الأخرى للمزيد من التفاصيل."
            back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
            await msg.edit_text(f"📊 *معلومات التطبيق:*\n```\n{result}\n```", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(back_keyboard))
            
        elif action == "manifest":
            out_dir = os.path.join(temp_dir, "manifest_extract")
            await analyzer.run_command(f"apktool d {apk_path} -o {out_dir} -f --no-src")
            manifest_path = os.path.join(out_dir, "AndroidManifest.xml")
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    manifest_content = f.read()[:2000]
                back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
                await msg.edit_text(f"📜 *AndroidManifest.xml (بداية الملف):*\n```xml\n{manifest_content}\n```", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(back_keyboard))
            else:
                back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
                await msg.edit_text("❌ فشل استخراج المانيفست.", reply_markup=InlineKeyboardMarkup(back_keyboard))
            
        elif action == "secrets":
            results = await analyzer.full_analysis(apk_path, temp_dir=temp_dir)
            back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
            await msg.edit_text(f"🔐 *الأسرار المكتشفة:*\n```\n{results.get('secrets', 'لا يوجد')[:1000]}\n```", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(back_keyboard))

        elif action == "urls":
            results = await analyzer.full_analysis(apk_path, temp_dir=temp_dir)
            back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
            await msg.edit_text(f"🔗 *الروابط المكتشفة:*\n```\n{results.get('urls', 'لا يوجد')[:1000]}\n```", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(back_keyboard))

        elif action == "perms":
            results = await analyzer.full_analysis(apk_path, temp_dir=temp_dir)
            perms = "\n".join(results.get('permissions', []))
            back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
            await msg.edit_text(f"🛡️ *الصلاحيات المطلوبة:*\n```\n{perms if perms else 'لا توجد'}\n```", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(back_keyboard))

        elif action == "decompile":
            await msg.edit_text(f"🛠️ جاري التفكيك الكامل لـ `{apk_info['name']}`... قد يستغرق هذا وقتاً.")
            out_dir = os.path.join(temp_dir, "full_decompile")
            zip_path = os.path.join(temp_dir, f"{apk_info['name']}_decompiled.zip")
            
            # Decompile
            await analyzer.run_command(f"apktool d {apk_path} -o {out_dir} -f")
            
            if os.path.exists(out_dir):
                await msg.edit_text(f"📦 جاري ضغط الملفات الناتجة لـ `{apk_info['name']}`...")
                import shutil
                # Create zip archive of the decompile directory
                shutil.make_archive(zip_path.replace('.zip', ''), 'zip', out_dir)
                
                if os.path.exists(zip_path):
                    await msg.edit_text(f"📤 جاري إرسال الملف المفقود لـ `{apk_info['name']}`...")
                    with open(zip_path, 'rb') as f:
                        await context.bot.send_document(
                            chat_id=update.effective_chat.id,
                            document=f,
                            filename=os.path.basename(zip_path),
                            caption=f"✅ اكتمل تفكيك `{apk_info['name']}` بنجاح."
                        )
                    await msg.delete()
                else:
                    await msg.edit_text("❌ فشل إنشاء ملف ZIP.")
            else:
                await msg.edit_text("❌ فشل تفكيك التطبيق.")

        elif action == "full":
            results = await analyzer.full_analysis(apk_path, temp_dir=temp_dir)
            res_text = f"🔥 *نتائج التحليل الشامل لـ `{apk_info['name']}`:*\n\n✅ تم استخراج {len(results.get('permissions', []))} صلاحية.\n✅ تم العثور على {len(results.get('libraries', []))} مكتبة.\n✅ تم فحص الأسرار والروابط.\n\nاستخدم الأوامر المتخصصة لرؤية التفاصيل."
            back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
            await msg.edit_text(res_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(back_keyboard))

        elif action == "decrypt":
            # Attempt to find common encryption keys or hardcoded strings
            await msg.edit_text(f"🔓 جاري البحث عن مفاتيح فك التشفير في `{apk_info['name']}`...")
            # We can use AdvancedAPKAnalyzer's find_secrets logic or custom grep
            results = await analyzer.run_command(f"grep -r -E -i 'key|iv|encrypt|decrypt|cipher' {temp_dir} 2>/dev/null | head -n 30")
            if results.strip():
                back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
                await msg.edit_text(f"🔓 *مفاتيح وسلاسل تشفير محتملة:*\n```\n{results[:2000]}\n```", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(back_keyboard))
            else:
                back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
                await msg.edit_text("❌ لم يتم العثور على سلاسل تشفير واضحة.", reply_markup=InlineKeyboardMarkup(back_keyboard))

        elif action == "cert":
            await msg.edit_text(f"📜 جاري استخراج معلومات الشهادة (V1+V2+V3) لـ `{apk_info['name']}`...")
            # استخدام التحليل الشامل للتوقيعات V1 + V2 + V3
            signatures = analyzer._extract_all_signatures(apk_path)
            cert_info = analyzer._format_signature_output(signatures)
            back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
            await msg.edit_text(cert_info, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(back_keyboard))

        elif action == "activities":
            await msg.edit_text(f"🎬 جاري استخراج الأنشطة لـ `{apk_info['name']}`...")
            # Decompile manifest if not already done
            out_dir = os.path.join(temp_dir, "manifest_extract")
            if not os.path.exists(out_dir):
                await analyzer.run_command(f"apktool d {apk_path} -o {out_dir} -f --no-src")
            
            manifest_path = os.path.join(out_dir, "AndroidManifest.xml")
            if os.path.exists(manifest_path):
                cmd = f"grep 'activity' {manifest_path} | grep 'android:name' | cut -d '\"' -f 2"
                result = await analyzer.run_command(cmd)
                back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
                await msg.edit_text(f"🎬 *أنشطة التطبيق (Activities):*\n```\n{result[:3000] if result.strip() else 'لا يوجد'}\n```", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(back_keyboard))
            else:
                back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
                await msg.edit_text("❌ فشل العثور على AndroidManifest.xml", reply_markup=InlineKeyboardMarkup(back_keyboard))

        elif action == "resources":
            await msg.edit_text(f"🖼️ جاري جرد الموارد لـ `{apk_info['name']}`...")
            # Use manifest_extract dir if exists
            res_dir = os.path.join(temp_dir, "manifest_extract/res")
            if not os.path.exists(res_dir):
                out_dir = os.path.join(temp_dir, "manifest_extract")
                await analyzer.run_command(f"apktool d {apk_path} -o {out_dir} -f --no-src")
            
            cmd = f"find {temp_dir}/manifest_extract/res -type f | head -30 | sed 's|{temp_dir}/manifest_extract/res/||'"
            result = await analyzer.run_command(cmd)
            back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
            await msg.edit_text(f"🖼️ *قائمة الموارد (Resources):*\n```\n{result[:3000] if result.strip() else 'لا يوجد'}\n```", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(back_keyboard))

        elif action == "libs":
            await msg.edit_text(f"📚 جاري جرد المكتبات لـ `{apk_info['name']}`...")
            cmd = f"find {temp_dir} -name '*.so' | head -20 | sed 's|{temp_dir}/||'"
            result = await analyzer.run_command(cmd)
            back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
            await msg.edit_text(f"📚 *المكتبات المستخدمة (Libs):*\n```\n{result[:3000] if result.strip() else 'لا توجد مكتبات .so'}\n```", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(back_keyboard))

        elif action == "protection":
            await msg.edit_text(f"🛡️ جاري فحص الحماية لـ `{apk_info['name']}`...")
            cmd = f"grep -r -i 'proguard\\|dexguard\\|obfuscate\\|crypt' {temp_dir} 2>/dev/null | head -15"
            result = await analyzer.run_command(cmd)
            back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
            await msg.edit_text(f"🛡️ *نتائج فحص الحماية:*\n```\n{result[:3000] if result.strip() else '⚠️ لا توجد حماية واضحة'}\n```", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(back_keyboard))

        elif action == "editall":
            # Decompile full if not already done
            decompile_dir = os.path.join(temp_dir, "full_decompile")
            if not os.path.exists(decompile_dir):
                await msg.edit_text(f"🛠️ جاري التفكيك الكامل أولاً للتعديل الشامل لـ `{apk_info['name']}`...")
                await analyzer.run_command(f"apktool d {apk_path} -o {decompile_dir} -f")
            
            if os.path.exists(decompile_dir):
                USER_STATES[user_id] = f"waiting_for_name_auto_{session_id}"
                await msg.edit_text(
                    "📝 **تعديل الهوية المتكامل:**\n\n"
                    "1️⃣ أرسل **الاسم الجديد** للتطبيق الآن:",
                    parse_mode='Markdown'
                )
            else:
                await msg.edit_text("❌ فشل التفكيك للتعديل.")

        elif action == "build":
            await msg.edit_text(f"🛠️ جاري محاولة إعادة بناء `{apk_info['name']}`...")
            decompile_dir = os.path.join(temp_dir, "full_decompile")
            
            # Ensure we have a complete decompile with apktool.yml
            # If manifest_extract exists but not full_decompile, we might be missing apktool.yml
            if not os.path.exists(os.path.join(decompile_dir, "apktool.yml")):
                await msg.edit_text(f"🛠️ جاري التفكيك الكامل أولاً لبناء `{apk_info['name']}`...")
                await analyzer.run_command(f"apktool d {apk_path} -o {decompile_dir} -f")
            
            if os.path.exists(os.path.join(decompile_dir, "apktool.yml")):
                # حذف ملفات PNG التالفة قبل البناء
                await remove_corrupted_pngs(decompile_dir)
                
                output_apk = os.path.join(temp_dir, f"rebuilt_{apk_info['name']}")
                # Using --use-aapt1 to avoid aapt2 compilation errors with invalid resources
                cmd = f"apktool b {decompile_dir} -o {output_apk} --use-aapt1 2>&1"
                result = await analyzer.run_command(cmd)
                
                if os.path.exists(output_apk):
                    await msg.edit_text(f"✅ تم إعادة بناء `{apk_info['name']}` بنجاح. جاري الإرسال...")
                    with open(output_apk, 'rb') as f:
                        await context.bot.send_document(
                            chat_id=update.effective_chat.id,
                            document=f,
                            filename=os.path.basename(output_apk),
                            caption=f"✅ تم إعادة بناء `{apk_info['name']}`"
                        )
                    back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
                    await msg.edit_text("✅ تم الإرسال بنجاح!", reply_markup=InlineKeyboardMarkup(back_keyboard))
                else:
                    back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
                    await msg.edit_text(f"❌ فشل البناء:\n```\n{result[:2000]}\n```", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(back_keyboard))
            else:
                back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
                await msg.edit_text("❌ فشل العثور على ملف `apktool.yml`. لا يمكن إعادة بناء التطبيق بدون تفكيك كامل.", reply_markup=InlineKeyboardMarkup(back_keyboard))

        elif action == "report":
            await msg.edit_text(f"📋 جاري توليد تقرير شامل لـ `{apk_info['name']}`...")
            results = await analyzer.full_analysis(apk_path, temp_dir=temp_dir)
            
            # Extract basic info from results
            basic = results.get('basic', 'No info')[:500]
            perms = "\n".join(results.get('permissions', []))[:500]
            
            report = f"📋 *تقرير تحليل شامل: `{apk_info['name']}`*\n\n"
            report += f"📊 *معلومات أساسية:*\n```\n{basic}\n```\n"
            report += f"🛡️ *الصلاحيات:*\n```\n{perms}\n```\n"
            report += f"✅ تم فحص الأسرار والروابط والمكتبات.\n"
            
            back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
            await msg.edit_text(report, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(back_keyboard))

        elif action == "sign":
            await msg.edit_text(f"🔐 جاري توقيع التطبيق: `{apk_info['name']}`...")
            
            # Try to find a built APK or use the original one
            decompile_dir = os.path.join(temp_dir, "full_decompile")
            apk_to_sign = None
            
            # Check for modified/rebuilt APKs first
            for filename in os.listdir(temp_dir):
                if filename.endswith('.apk') and filename != apk_info['name']:
                    apk_to_sign = os.path.join(temp_dir, filename)
                    break
            
            # If no modified APK found, use original
            if not apk_to_sign:
                apk_to_sign = apk_path
            
            signed_apk = os.path.join(temp_dir, f"signed_{apk_info['name']}")
            
            # Generate UNIQUE keystore for EACH modification (CRITICAL!)
            import time
            import random
            unique_id = f"{int(time.time())}_{random.randint(1000,9999)}"
            keystore_path = os.path.join(temp_dir, f"key_{unique_id}.keystore")
            
            # Create keystore with default credentials (for testing)
            keytool_cmd = f"keytool -genkey -v -keystore {keystore_path} -keyalg RSA -keysize 2048 -validity 10000 -alias testkey -storepass 123456 -keypass 123456 -dname 'CN=Test,OU=Test,O=Test,L=Test,S=Test,C=US'"
            await analyzer.run_command(keytool_cmd)
            
            # Sign the APK with V1+V2+V3 signatures
            if os.path.exists(keystore_path):
                import shutil
                # خطوة 1: zipalign APK للمحاذاة الصحيحة
                aligned_apk = os.path.join(temp_dir, f"aligned_{apk_info['name']}")
                zipalign_cmd = f"zipalign -v 4 {apk_to_sign} {aligned_apk}"
                await analyzer.run_command(zipalign_cmd)
                
                # استخدم aligned APK إذا نجح، وإلا استخدم الأصلي
                apk_to_final_sign = aligned_apk if os.path.exists(aligned_apk) else apk_to_sign
                
                # خطوة 2: استخدم apksigner لعمل V1+V2+V3 signatures
                sign_cmd = f"apksigner sign --ks {keystore_path} --ks-pass pass:123456 --ks-key-alias testkey --key-pass pass:123456 --v1-signer-name RSA {apk_to_final_sign}"
                sign_result = await analyzer.run_command(sign_cmd)
                
                # نسخ التطبيق الموقع
                try:
                    shutil.copy(apk_to_final_sign, signed_apk)
                except Exception as e:
                    logger.error(f"Failed to copy signed APK: {e}")
                
                if os.path.exists(signed_apk):
                    await msg.edit_text(f"✅ تم توقيع التطبيق بنجاح! جاري الإرسال...")
                    with open(signed_apk, 'rb') as f:
                        await context.bot.send_document(
                            chat_id=update.effective_chat.id,
                            document=f,
                            filename=os.path.basename(signed_apk),
                            caption=f"✅ تم توقيع `{apk_info['name']}` بنجاح.\n\n⚠️ **ملاحظة:** هذا توقيع اختبار فقط. للإنتاج، استخدم keystoreخاصتك."
                        )
                    back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
                    await msg.edit_text("✅ تم الإرسال بنجاح!", reply_markup=InlineKeyboardMarkup(back_keyboard))
                else:
                    back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
                    await msg.edit_text(f"❌ فشل في إنشاء APK موقع.", reply_markup=InlineKeyboardMarkup(back_keyboard))
            else:
                back_keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data=f"apk_cmd_back_{session_id}")]]
                await msg.edit_text("❌ فشل في إنشاء keystore للتوقيع.", reply_markup=InlineKeyboardMarkup(back_keyboard))

        elif action == "icon":
            # Decompile full if not already done
            decompile_dir = os.path.join(temp_dir, "full_decompile")
            if not os.path.exists(decompile_dir):
                await msg.edit_text(f"🛠️ جاري التفكيك الكامل أولاً لاستبدال الأيقونة لـ `{apk_info['name']}`...")
                await analyzer.run_command(f"apktool d {apk_path} -o {decompile_dir} -f")
            
            if os.path.exists(decompile_dir):
                USER_STATES[user_id] = f"waiting_for_icon_{session_id}"
                await msg.edit_text(
                    "🖼️ **لتغيير الأيقونة:**\n"
                    "1. ارفع صورة PNG مربعة (512x512 مثلاً)\n"
                    "2. سأقوم باستبدال الأيقونة القديمة في جميع الأحجام\n\n"
                    "⚠️ تأكد أن الصورة بصيغة PNG",
                    parse_mode='Markdown'
                )
            else:
                await msg.edit_text("❌ فشل التفكيك لاستبدال الأيقونة.")

        elif action == "name":
            # Decompile full if not already done
            decompile_dir = os.path.join(temp_dir, "full_decompile")
            if not os.path.exists(decompile_dir):
                await msg.edit_text(f"🛠️ جاري التفكيك الكامل أولاً لتغيير الاسم لـ `{apk_info['name']}`...")
                await analyzer.run_command(f"apktool d {apk_path} -o {decompile_dir} -f")
            
            if os.path.exists(decompile_dir):
                # Try to find current name
                import re
                current_name = "غير معروف"
                strings_path = os.path.join(decompile_dir, "res/values/strings.xml")
                if os.path.exists(strings_path):
                    with open(strings_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    match = re.search(r'<string name="app_name">(.*?)</string>', content)
                    if match:
                        current_name = match.group(1)
                
                USER_STATES[user_id] = f"waiting_for_name_{session_id}"
                await msg.edit_text(
                    f"📛 **الاسم الحالي:** `{current_name}`\n\n"
                    f"✏️ **أرسل الاسم الجديد الآن:**",
                    parse_mode='Markdown'
                )
            else:
                await msg.edit_text("❌ فشل التفكيك لتغيير الاسم.")

        elif action == "ssl":
            await msg.edit_text(f"🔓 جاري كسر SSL Certificate Pinning لـ `{apk_info['name']}`...")
            
            # Decompile full if not already done
            decompile_dir = os.path.join(temp_dir, "full_decompile")
            if not os.path.exists(decompile_dir):
                await msg.edit_text(f"🛠️ جاري التفكيك الكامل أولاً...")
                await analyzer.run_command(f"apktool d {apk_path} -o {decompile_dir} -f")
            
            if os.path.exists(decompile_dir):
                # Apply SSL bypass
                success = await bypass_ssl_pinning(decompile_dir)
                
                if success:
                    await msg.edit_text(f"✅ تم كسر SSL Certificate Pinning!\n\n🛠️ جاري إعادة البناء...")
                    
                    # Rebuild APK
                    output_apk = os.path.join(temp_dir, f"ssl_bypassed_{apk_info['name']}")
                    build_cmd = f"apktool b {decompile_dir} -o {output_apk} --use-aapt1 2>&1"
                    build_result = await analyzer.run_command(build_cmd)
                    
                    if os.path.exists(output_apk):
                        # توقيع التطبيق تلقائياً بعد البناء (V1+V2+V3)
                        await msg.edit_text(f"✅ تم إعادة البناء بنجاح!\n\n🔐 جاري التوقيع التلقائي (V1+V2+V3)...")
                        
                        import time
                        import random
                        unique_id = f"{int(time.time())}_{random.randint(1000,9999)}"
                        keystore_path = os.path.join(temp_dir, f"key_{unique_id}.keystore")
                        
                        # Create keystore
                        keytool_cmd = f"keytool -genkey -v -keystore {keystore_path} -keyalg RSA -keysize 2048 -validity 10000 -alias testkey -storepass 123456 -keypass 123456 -dname 'CN=Test,OU=Test,O=Test,L=Test,S=Test,C=US'"
                        await analyzer.run_command(keytool_cmd)
                        
                        # Sign APK with V1+V2+V3 using apksigner
                        if os.path.exists(keystore_path):
                            # استخدام apksigner لتوقيع V1+V2+V3 (أفضل من jarsigner)
                            sign_cmd = f"apksigner sign --ks {keystore_path} --ks-pass pass:123456 --ks-key-alias testkey --key-pass pass:123456 --min-sdk-version 1 {output_apk} 2>&1"
                            sign_result = await analyzer.run_command(sign_cmd)
                            
                            # إذا فشل apksigner، حاول jarsigner كبديل
                            if "error" in sign_result.lower() or not os.path.exists(output_apk):
                                sign_cmd_fallback = f"jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore {keystore_path} -storepass 123456 -keypass 123456 {output_apk} testkey"
                                await analyzer.run_command(sign_cmd_fallback)
                        
                        # Send signed APK
                        await msg.edit_text(f"✅ تم التوقيع بنجاح (V1+V2+V3)! جاري الإرسال...", parse_mode='Markdown')
                        with open(output_apk, 'rb') as f:
                            await context.bot.send_document(
                                chat_id=update.effective_chat.id,
                                document=f,
                                filename=os.path.basename(output_apk),
                                caption=f"✅ تم كسر SSL Pinning + التوقيع (V1+V2+V3) لـ `{apk_info['name']}`\n\n📝 **التفاصيل:**\n- ✅ تم كسر SSL Certificate Pinning\n- ✅ تم توقيع التطبيق بـ V1 + V2 + V3\n- يثق بـ شهادات المستخدم (البروكسي)\n- متوافق مع جميع إصدارات Android\n- جاهز للتثبيت على الجهاز 📱"
                            )
                        # عرض القائمة الرئيسية مع رسالة تأكيد
                        text = f"✅ تم كسر SSL Pinning والتوقيع (V1+V2+V3)!\n\n🔥 اختر أداة أخرى للمتابعة:"
                        keyboard = [
                            [
                                InlineKeyboardButton("🔥 تحليل كامل", callback_data=f"apk_cmd_full_{session_id}"),
                                InlineKeyboardButton("🛠️ إعادة بناء", callback_data=f"apk_cmd_build_{session_id}"),
                            ],
                            [
                                InlineKeyboardButton("📥 تحميل من رابط", callback_data=f"apk_cmd_loadurl_{session_id}"),
                                InlineKeyboardButton("🔙 العودة", callback_data=f"apk_cmd_back_{session_id}"),
                            ]
                        ]
                        await msg.edit_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
                    elif "Public symbol" in build_result or "not defined" in build_result:
                        # محاولة تنظيف المراجع مجدداً وإعادة المحاولة
                        await msg.edit_text("⚠️ يوجد مراجع محطومة... جاري التنظيف والمحاولة مجدداً...")
                        await cleanup_broken_references(decompile_dir)
                        
                        # إعادة المحاولة
                        build_cmd_retry = f"apktool b {decompile_dir} -o {output_apk} --use-aapt1 2>&1"
                        build_result_retry = await analyzer.run_command(build_cmd_retry)
                        
                        if os.path.exists(output_apk):
                            await msg.edit_text(f"✅ تم إعادة البناء بنجاح (بعد التنظيف)! جاري الإرسال...")
                            with open(output_apk, 'rb') as f:
                                await context.bot.send_document(
                                    chat_id=update.effective_chat.id,
                                    document=f,
                                    filename=os.path.basename(output_apk),
                                    caption=f"✅ تم كسر SSL Pinning لـ `{apk_info['name']}` (بعد تنظيف المراجع)"
                                )
                            text = f"✅ تم البناء بنجاح!\n\n🔥 اختر أداة أخرى للمتابعة:"
                            keyboard = [
                                [
                                    InlineKeyboardButton("🔥 تحليل كامل", callback_data=f"apk_cmd_full_{session_id}"),
                                    InlineKeyboardButton("🔐 توقيع", callback_data=f"apk_cmd_sign_{session_id}"),
                                ],
                                [
                                    InlineKeyboardButton("🔓 كسر SSL", callback_data=f"apk_cmd_ssl_{session_id}"),
                                    InlineKeyboardButton("🔙 العودة", callback_data=f"apk_cmd_back_{session_id}"),
                                ]
                            ]
                            await msg.edit_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
                        else:
                            await msg.edit_text(f"❌ فشل البناء حتى بعد التنظيف:\n```\n{build_result_retry[:1500]}\n```", parse_mode='Markdown')
                    else:
                        await msg.edit_text(f"❌ فشل البناء:\n```\n{build_result[:2000]}\n```", parse_mode='Markdown')
                else:
                    await msg.edit_text("❌ فشل تطبيق SSL Bypass.")
            else:
                await msg.edit_text("❌ فشل التفكيك.")
        
        elif action == "splash":
            user_id = update.effective_user.id
            # عرض خيارات النص
            splash_keyboard = [
                [
                    InlineKeyboardButton("⚠️ تحذير أمان", callback_data=f"splash_warning_{session_id}"),
                    InlineKeyboardButton("📝 ملاحظة", callback_data=f"splash_note_{session_id}"),
                ],
                [
                    InlineKeyboardButton("🔄 نسخة معدلة", callback_data=f"splash_mod_{session_id}"),
                    InlineKeyboardButton("✏️ نص مخصص", callback_data=f"splash_custom_{session_id}"),
                ]
            ]
            await msg.edit_text(
                "💬 **إضافة نص عند فتح التطبيق:**\n\n"
                "اختر نوع النص الذي تريد عرضه:\n\n"
                "سيظهر النص عند فتح التطبيق ويختفي بعد 3 ثواني",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(splash_keyboard)
            )
        
        elif action == "loadurl":
            user_id = update.effective_user.id
            USER_STATES[user_id] = f"waiting_for_url_{session_id}"
            await msg.edit_text(
                "📥 **تحميل APK من رابط:**\n\n"
                "أرسل رابط APK مباشر (http أو https):\n\n"
                "*مثال:*\n"
                "`https://example.com/app.apk`\n\n"
                "⏳ جاري الانتظار...",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Error in APK analysis: {e}")
        await msg.edit_text(f"❌ حدث خطأ: {str(e)}")

async def splash_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار نوع النص عند فتح التطبيق"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data.split("_")
    splash_type = callback_data[1]
    session_id = callback_data[2]
    
    if 'apks' not in context.user_data:
        context.user_data['apks'] = {}
    
    apk_info = context.user_data.get('apks', {}).get(session_id)
    if not apk_info:
        await query.edit_message_text("❌ انتهت صلاحية الجلسة.")
        return
    
    user_id = update.effective_user.id
    temp_dir = apk_info['dir']
    
    if splash_type == "custom":
        USER_STATES[user_id] = f"waiting_for_splash_custom_{session_id}"
        await query.edit_message_text(
            "✏️ **أرسل النص المخصص:**\n\n"
            "سيظهر النص عند فتح التطبيق (حد أقصى 200 حرف)\n\n"
            "*أمثلة:*\n"
            "`عمك سامي`\n"
            "`تعديل: القروب التعليمي`",
            parse_mode='Markdown'
        )
    else:
        splash_texts = {
            "warning": "⚠️ تحذير أمان\nهذا التطبيق معدل، استخدامك له على مسؤوليتك",
            "note": "📝 ملاحظة\nهذه نسخة معدلة لأغراض تعليمية",
            "mod": "🔄 نسخة معدلة\nModified Version - For Educational Use"
        }
        
        splash_text = splash_texts.get(splash_type, "تم التعديل")
        msg = await context.bot.send_message(chat_id=query.message.chat_id, text=f"🛠️ جاري إضافة النص: `{splash_text[:50]}...`", parse_mode='Markdown')
        
        success = await add_splash_toast(temp_dir, splash_text)
        if success:
            await msg.edit_text(
                f"✅ **تم إضافة النص بنجاح:**\n\n"
                f"`{splash_text}`\n\n"
                f"استخدم 🛠️ إعادة بناء (Build) لتطبيق التغييرات",
                parse_mode='Markdown'
            )
        else:
            await msg.edit_text(f"❌ فشل إضافة النص. قد لا يكون التطبيق متوافقاً.")

async def add_splash_toast(base_dir, text):
    """إضافة Toast نص عند فتح التطبيق"""
    try:
        import re
        
        # البحث عن manifest في المجلد أو أي مجلد فرعي
        manifest_path = None
        smali_base = None
        
        # ابحث عن full_decompile أولاً
        full_decompile = os.path.join(base_dir, "full_decompile")
        if os.path.exists(full_decompile):
            manifest_path = os.path.join(full_decompile, "AndroidManifest.xml")
            smali_base = full_decompile
        else:
            # ابحث عن manifest في المجلد الرئيسي
            manifest_path = os.path.join(base_dir, "AndroidManifest.xml")
            smali_base = base_dir
        
        if not os.path.exists(manifest_path):
            logger.warning(f"Manifest not found at {manifest_path}")
            # جرب البحث في جميع المجلدات
            for root, dirs, files in os.walk(base_dir):
                if 'AndroidManifest.xml' in files:
                    manifest_path = os.path.join(root, 'AndroidManifest.xml')
                    smali_base = root
                    logger.info(f"Found manifest at: {manifest_path}")
                    break
            
            if not manifest_path or not os.path.exists(manifest_path):
                logger.warning(f"Could not find manifest in {base_dir}")
                return False
        
        with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
            manifest = f.read()
        
        # البحث عن MainActivity
        launcher_match = re.search(
            r'<activity[^>]+android:name="([^"]+)"[^>]*>.*?<action\s+android:name="android\.intent\.action\.MAIN"',
            manifest,
            re.DOTALL
        )
        
        if launcher_match:
            main_activity = launcher_match.group(1)
        else:
            match = re.search(r'<activity[^>]+android:name="([^"]+)"', manifest)
            if not match:
                logger.warning("No activity found in manifest")
                return False
            main_activity = match.group(1)
        
        logger.info(f"Found main activity: {main_activity}")
        activity_path = main_activity.replace('.', '/') + '.smali'
        
        # البحث عن ملف smali
        smali_file = None
        for i in range(10):
            if i == 0:
                path = os.path.join(smali_base, "smali", activity_path)
            else:
                path = os.path.join(smali_base, f"smali_classes{i}", activity_path)
            
            if os.path.exists(path):
                smali_file = path
                logger.info(f"Found smali file: {path}")
                break
        
        # إذا لم نجد، ابحث في جميع المجلدات
        if not smali_file:
            for root, dirs, files in os.walk(smali_base):
                for file in files:
                    if file.endswith('.smali') and 'MainActivity' in file:
                        smali_file = os.path.join(root, file)
                        logger.info(f"Found MainActivity smali: {smali_file}")
                        break
                if smali_file:
                    break
        
        if not smali_file:
            logger.warning(f"Smali file not found for {activity_path}")
            return False
        
        with open(smali_file, 'r', encoding='utf-8', errors='ignore') as f:
            smali = f.read()
        
        if 'onCreate' not in smali:
            logger.warning("onCreate method not found in smali")
            return False
        
        # إضافة Toast - الطريقة الصحيحة
        lines = smali.split('\n')
        insert_pos = -1
        in_onCreate = False
        locals_line_idx = -1
        
        # ابحث عن onCreate وإيجاد .locals
        for i, line in enumerate(lines):
            if '.method' in line and 'onCreate' in line:
                in_onCreate = True
            
            if in_onCreate and '.locals' in line:
                locals_line_idx = i
                # تحقق من أن .locals كافي (نحتاج على الأقل 2)
                match = re.search(r'\.locals\s+(\d+)', line)
                if match:
                    current_locals = int(match.group(1))
                    if current_locals < 2:
                        # زيد .locals
                        lines[i] = re.sub(r'\.locals\s+\d+', '.locals 2', line)
                        logger.info(f"Updated .locals to 2 at line {i}")
            
            # ابحث عن invoke-super (بداية code execution في onCreate)
            if in_onCreate and 'invoke-super' in line and locals_line_idx != -1:
                insert_pos = i + 1
                logger.info(f"Will insert Toast code after invoke-super at line {insert_pos}")
                break
        
        if insert_pos == -1:
            logger.warning("Could not find invoke-super in onCreate")
            return False
        
        # كود Toast الصحيح - بالترتيب الصحيح
        escaped_text = text.replace('"', '\\"')
        toast_code = [
            "    # Toast injection",
            "    const/4 v0, 0x1",
            f"    const-string v1, \"{escaped_text}\"",
            "    invoke-static {p0, v1, v0}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;",
            "    move-result-object v0",
            "    invoke-virtual {v0}, Landroid/widget/Toast;->show()V",
        ]
        
        # أدرج جميع الأسطر واحداً تلو الآخر
        for j, code_line in enumerate(toast_code):
            lines.insert(insert_pos + j, code_line)
        
        with open(smali_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        logger.info("Successfully added splash toast")
        return True
        
    except Exception as e:
        logger.error(f"Error adding splash toast: {e}", exc_info=True)
        return False

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة النصوص المرسلة تلقائياً"""
    if not update.message or not update.message.text:
        return
        
    text = update.message.text.strip()
    user_id = update.effective_user.id
    user_state = USER_STATES.get(user_id)
    
    # إذا كان المستخدم في حالة انتظار إدخال لأداة معينة
    if user_state:
        # Check for custom splash text
        if user_state.startswith("waiting_for_splash_custom_"):
            session_id = user_state.split("_")[-1]
            apk_info = context.user_data.get('apks', {}).get(session_id)
            
            if not apk_info:
                await update.message.reply_text("❌ انتهت صلاحية الجلسة.")
                USER_STATES.pop(user_id, None)
                return
            
            splash_text = text.strip()
            if len(splash_text) > 200:
                await update.message.reply_text("❌ النص طويل جداً (الحد الأقصى 200 حرف)")
                return
            
            msg = await update.message.reply_text(f"🛠️ جاري إضافة النص: `{splash_text[:50]}...`", parse_mode='Markdown')
            
            success = await add_splash_toast(apk_info['dir'], splash_text)
            if success:
                await msg.edit_text(
                    f"✅ **تم إضافة النص بنجاح:**\n\n"
                    f"`{splash_text}`\n\n"
                    f"استخدم 🛠️ إعادة بناء (Build) لتطبيق التغييرات",
                    parse_mode='Markdown'
                )
            else:
                await msg.edit_text(f"❌ فشل إضافة النص. قد لا يكون التطبيق متوافقاً.")
            
            USER_STATES.pop(user_id, None)
            return
        
        # Check for URL loading state
        if user_state.startswith("waiting_for_url_"):
            session_id = user_state.split("_")[-1]
            url = text.strip()
            
            if not url.startswith(('http://', 'https://')):
                await update.message.reply_text("❌ يرجى إرسال رابط صحيح يبدأ بـ http:// أو https://")
                return
            
            msg = await update.message.reply_text(f"📥 جاري تحميل ملف APK من الرابط...\n\nالرابط: `{url[:50]}...`", parse_mode='Markdown')
            
            try:
                import uuid
                import httpx
                
                new_session_id = str(uuid.uuid4())[:8]
                temp_dir = f"temp/apk_{user_id}_{new_session_id}"
                os.makedirs(temp_dir, exist_ok=True)
                
                # تحميل الملف
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    
                    # الحصول على اسم الملف
                    filename = url.split('/')[-1]
                    if not filename.endswith('.apk'):
                        filename = f"app_{new_session_id}.apk"
                    
                    apk_path = os.path.join(temp_dir, filename)
                    
                    # حفظ الملف
                    with open(apk_path, 'wb') as f:
                        f.write(response.content)
                    
                    file_size = os.path.getsize(apk_path) / (1024*1024)
                    
                    if file_size > 500:
                        raise Exception(f"الملف كبير جداً ({file_size:.1f}MB)")
                    
                    # حفظ البيانات
                    if 'apks' not in context.user_data:
                        context.user_data['apks'] = {}
                    
                    context.user_data['apks'][new_session_id] = {
                        'path': apk_path,
                        'name': filename,
                        'dir': temp_dir
                    }
                    
                    # عرض القائمة الرئيسية للـ APK الجديد
                    apk_info = {'name': filename}
                    await msg.delete()
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"✅ تم تحميل ملف APK: `{filename}`\n📦 الحجم: {file_size:.1f}MB\n\nماذا تريد أن أفعل بهذا التطبيق؟",
                        parse_mode='Markdown'
                    )
                    # Show the menu
                    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                    keyboard = [
                        [
                            InlineKeyboardButton("📊 معلومات (Info)", callback_data=f"apk_cmd_info_{new_session_id}"),
                            InlineKeyboardButton("📜 مانیفست (Manifest)", callback_data=f"apk_cmd_manifest_{new_session_id}"),
                        ],
                        [
                            InlineKeyboardButton("🔐 أسرار (Secrets)", callback_data=f"apk_cmd_secrets_{new_session_id}"),
                            InlineKeyboardButton("🔗 روابط (URLs)", callback_data=f"apk_cmd_urls_{new_session_id}"),
                        ],
                        [
                            InlineKeyboardButton("🛠️ تفكيك (Decompile)", callback_data=f"apk_cmd_decompile_{new_session_id}"),
                            InlineKeyboardButton("🛡️ الصلاحيات (Perms)", callback_data=f"apk_cmd_perms_{new_session_id}"),
                        ],
                        [
                            InlineKeyboardButton("🔓 فك التشفير (Decrypt)", callback_data=f"apk_cmd_decrypt_{new_session_id}"),
                            InlineKeyboardButton("📜 الشهادة (Cert)", callback_data=f"apk_cmd_cert_{new_session_id}"),
                        ],
                        [
                            InlineKeyboardButton("🎬 الأنشطة (Activities)", callback_data=f"apk_cmd_activities_{new_session_id}"),
                            InlineKeyboardButton("🖼️ الموارد (Resources)", callback_data=f"apk_cmd_resources_{new_session_id}"),
                        ],
                        [
                            InlineKeyboardButton("📚 المكتبات (Libs)", callback_data=f"apk_cmd_libs_{new_session_id}"),
                            InlineKeyboardButton("🛡️ الحماية (Protection)", callback_data=f"apk_cmd_protection_{new_session_id}"),
                        ],
                        [
                            InlineKeyboardButton("🛠️ إعادة بناء (Build)", callback_data=f"apk_cmd_build_{new_session_id}"),
                            InlineKeyboardButton("📋 تقرير (Report)", callback_data=f"apk_cmd_report_{new_session_id}"),
                        ],
                        [
                            InlineKeyboardButton("🔥 تحليل كامل (Full)", callback_data=f"apk_cmd_full_{new_session_id}"),
                        ],
                        [
                            InlineKeyboardButton("🎨📛 تعديل الهوية (Edit Icon & Name)", callback_data=f"apk_cmd_editall_{new_session_id}"),
                            InlineKeyboardButton("🔐 توقيع APK (Sign)", callback_data=f"apk_cmd_sign_{new_session_id}"),
                        ],
                        [
                            InlineKeyboardButton("🔓 كسر SSL (Bypass SSL)", callback_data=f"apk_cmd_ssl_{new_session_id}"),
                            InlineKeyboardButton("💬 نص عند الفتح (Splash)", callback_data=f"apk_cmd_splash_{new_session_id}"),
                        ],
                        [
                            InlineKeyboardButton("📥 تحميل من رابط", callback_data=f"apk_cmd_loadurl_{new_session_id}"),
                            InlineKeyboardButton("❌ إلغاء وحذف", callback_data=f"apk_cmd_cancel_{new_session_id}"),
                        ]
                    ]
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="⬇️ اختر من القائمة أدناه:",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    USER_STATES.pop(user_id, None)
                    
            except Exception as e:
                await msg.edit_text(f"❌ فشل التحميل: {str(e)}")
                USER_STATES.pop(user_id, None)
            return
        
        # Check for APK edit states
        if user_state.startswith("waiting_for_name_"):
            is_auto = "_auto_" in user_state
            session_id = user_state.split("_")[-1]
            apk_info = context.user_data.get('apks', {}).get(session_id)
            if not apk_info:
                await update.message.reply_text("❌ انتهت صلاحية الجلسة.")
                USER_STATES.pop(user_id, None)
                return
            
            new_name = text
            decompile_dir = os.path.join(apk_info['dir'], "full_decompile")
            
            import re
            success = False
            # غيّر package name أولاً (CRITICAL!)
            await change_apk_package_name(decompile_dir)
            
            # Update all strings.xml files
            for root, dirs, files in os.walk(os.path.join(decompile_dir, "res")):
                if "strings.xml" in files:
                    file_path = os.path.join(root, "strings.xml")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = re.sub(
                        r'<string name="app_name">.*?</string>',
                        f'<string name="app_name">{new_name}</string>',
                        content
                    )
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    success = True
            
            if success:
                # احفظ الاسم الجديد في apk_info لاستخدامه لاحقاً
                apk_info['new_app_name'] = new_name
                
                if is_auto:
                    USER_STATES[user_id] = f"waiting_for_icon_auto_{session_id}"
                    await update.message.reply_text(
                        f"✅ تم تغيير الاسم إلى: `{new_name}`\n\n"
                        "2️⃣ الآن أرسل **صورة الأيقونة الجديدة** (PNG):",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text(
                        f"✅ تم تغيير الاسم إلى: `{new_name}`\n\n"
                        "📁 استخدم زر البناء لإعادة التجميع.",
                        parse_mode='Markdown'
                    )
                    USER_STATES.pop(user_id, None)
            else:
                await update.message.reply_text("❌ لم يتم العثور على ملفات strings.xml لتعديل الاسم.")
                USER_STATES.pop(user_id, None)
            return

        context.args = [text]
        if user_state == "ipgeo":
            await ip_geo_command(update, context)
        elif user_state == "httpsec":
            await httpsec_command(update, context)
        elif user_state == "doh":
            await doh_command(update, context)
        elif user_state == "exif":
            await update.message.reply_text("📸 يرجى إرسال صورة وليس نصاً لتحليل EXIF.")
        
        # مسح الحالة بعد التنفيذ
        USER_STATES.pop(user_id, None)
        return

    # التعرف التلقائي إذا لم يكن هناك حالة محددة
    import re
    
    # 1. عنوان IP
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ip_pattern, text):
        context.args = [text]
        await ip_geo_command(update, context)
        return

    # 2. رابط أو دومين
    domain_pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(domain_pattern, text) and not text.startswith("http"):
        context.args = [text]
        await doh_command(update, context)
        return
        
    # 3. بريد إلكتروني
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, text):
        context.args = [text]
        await holehe_command(update, context)
        return

    # 4. رقم هاتف (تقريبي)
    phone_pattern = r'^\+?\d{8,15}$'
    if re.match(phone_pattern, text):
        context.args = [text]
        await phone_command(update, context)
        return

    # 5. رابط URL (لفحص الأمان أو كشف الرابط المختصر)
    if text.startswith(("http://", "https://")):
        context.args = [text]
        if user_state == "unshort":
            from modules.url_tools import unshorten_url
            msg = await update.message.reply_text("🔗 جاري كشف الرابط الحقيقي...")
            result = await unshorten_url(text)
            await msg.edit_text(result, parse_mode='Markdown', disable_web_page_preview=True)
            USER_STATES.pop(user_id, None)
            return
        await httpsec_command(update, context)
        return

async def unshort_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(context.bot, update.effective_user.id): return
    if is_banned(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الرابط المختصر\nمثال: `/unshort bit.ly/xxx`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    increment_command("unshort")
    msg = await update.message.reply_text(f"🔗 جاري كشف الرابط: `{url}`...", parse_mode='Markdown')
    from modules.url_tools import unshorten_url
    result = await unshorten_url(url)
    await msg.edit_text(result, parse_mode='Markdown', disable_web_page_preview=True)

async def shodan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(context.bot, update.effective_user.id): return
    if is_banned(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال عنوان IP\nمثال: `/shodan 8.8.8.8`", parse_mode='Markdown')
        return
    target = context.args[0]
    increment_command("shodan")
    msg = await update.message.reply_text(f"🔍 جاري فحص Shodan لـ `{target}`...", parse_mode='Markdown')
    from modules.deep_web_osint import shodan_scan
    result = await shodan_scan(target)
    await msg.edit_text(result, parse_mode='Markdown')

async def darkweb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(context.bot, update.effective_user.id): return
    if is_banned(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الإيميل أو اسم المستخدم للفحص\nمثال: `/darkweb example@gmail.com`", parse_mode='Markdown')
        return
    query = context.args[0]
    increment_command("darkweb")
    msg = await update.message.reply_text(f"🕵️ جاري فحص تسريبات الويب المظلم لـ `{query}`...", parse_mode='Markdown')
    from modules.deep_web_osint import darkweb_check
    result = await darkweb_check(query)
    await msg.edit_text(result, parse_mode='Markdown')

async def darkweb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(context.bot, update.effective_user.id): return
    if is_banned(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال الإيميل أو اسم المستخدم للفحص\nمثال: `/darkweb example@gmail.com`", parse_mode='Markdown')
        return
    query = context.args[0]
    increment_command("darkweb")
    msg = await update.message.reply_text(f"🕵️ جاري فحص تسريبات الويب المظلم لـ `{query}`...", parse_mode='Markdown')
    from modules.deep_web_osint import darkweb_check
    result = await darkweb_check(query)
    await msg.edit_text(result, parse_mode='Markdown')

async def censys_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(context.bot, update.effective_user.id): return
    if is_banned(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال IP أو دومين\nمثال: `/censys 1.1.1.1`", parse_mode='Markdown')
        return
    target = context.args[0]
    increment_command("censys")
    msg = await update.message.reply_text(f"🔎 جاري فحص Censys لـ `{target}`...", parse_mode='Markdown')
    from modules.deep_web_osint import censys_scan
    result = await censys_scan(target)
    await msg.edit_text(result, parse_mode='Markdown')

async def apktool_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال اسم التطبيق أو الرابط\nمثال: `/apktool app.apk`", parse_mode='Markdown')
        return
    query = context.args[0]
    msg = await update.message.reply_text(f"📦 جاري تحليل التطبيق: `{query}`...", parse_mode='Markdown')
    result = await apktool_analyze(query)
    await msg.edit_text(result, parse_mode='Markdown')

async def apk_handler_base(update: Update, context: ContextTypes.DEFAULT_TYPE, cmd_type):
    # This is a generic handler for APK commands
    # For a real implementation, it would look for a downloaded file or session
    await update.message.reply_text(f"🛠️ جاري تنفيذ أمر `{cmd_type}`... (يرجى إرفاق ملف APK أولاً)")

async def apkinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await apk_handler_base(update, context, "apkinfo")

async def apkmanifest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await apk_handler_base(update, context, "apkmanifest")

async def apkpermissions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await apk_handler_base(update, context, "apkpermissions")

async def apksecrets_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await apk_handler_base(update, context, "apksecrets")

async def apkurls_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await apk_handler_base(update, context, "apkurls")

async def apkdecompile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await apk_handler_base(update, context, "apkdecompile")

async def apkdecrypt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await apk_handler_base(update, context, "apkdecrypt")

async def apkcert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await apk_handler_base(update, context, "apkcert")

async def apkfull_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await apk_handler_base(update, context, "apkfull")

async def apkurl_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحميل وتحليل APK من رابط مباشر"""
    if not context.args:
        await update.message.reply_text(
            "📥 أرسل رابط APK مباشر لتحميله وتحليله\n\n"
            "*مثال:*\n"
            "`/apkurl https://example.com/app.apk`\n\n"
            "⚠️ هذه الطريقة تتجاوز حد 20MB من تليجرام!",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    if not url.startswith(('http://', 'https://')):
        await update.message.reply_text("❌ يرجى إرسال رابط صحيح يبدأ بـ http:// أو https://")
        return
    
    user_id = update.effective_user.id
    msg = await update.message.reply_text(f"📥 جاري تحميل ملف APK من الرابط...\n\nالرابط: `{url[:50]}...`", parse_mode='Markdown')
    
    try:
        import uuid
        import httpx
        
        session_id = str(uuid.uuid4())[:8]
        temp_dir = f"temp/apk_{user_id}_{session_id}"
        os.makedirs(temp_dir, exist_ok=True)
        
        # تحميل الملف
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            # الحصول على اسم الملف
            filename = url.split('/')[-1]
            if not filename.endswith('.apk'):
                filename = f"app_{session_id}.apk"
            
            apk_path = os.path.join(temp_dir, filename)
            
            # حفظ الملف
            with open(apk_path, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(apk_path) / (1024*1024)
            
            if file_size > 500:  # حد أعلى معقول
                raise Exception(f"الملف كبير جداً ({file_size:.1f}MB)")
            
            # حفظ البيانات
            if 'apks' not in context.user_data:
                context.user_data['apks'] = {}
            
            context.user_data['apks'][session_id] = {
                'path': apk_path,
                'name': filename,
                'dir': temp_dir
            }
            context.user_data['current_apk_session'] = session_id
            
            # عرض القائمة الكاملة (نفس القائمة من show_apk_menu)
            text = f"✅ تم تحميل ملف APK: `{filename}`\n📦 الحجم: {file_size:.1f}MB\n\nماذا تريد أن أفعل بهذا التطبيق؟ اختر أداة من القائمة:"
            keyboard = [
                [
                    InlineKeyboardButton("📊 معلومات (Info)", callback_data=f"apk_cmd_info_{session_id}"),
                    InlineKeyboardButton("📜 مانیفست (Manifest)", callback_data=f"apk_cmd_manifest_{session_id}"),
                ],
                [
                    InlineKeyboardButton("🔐 أسرار (Secrets)", callback_data=f"apk_cmd_secrets_{session_id}"),
                    InlineKeyboardButton("🔗 روابط (URLs)", callback_data=f"apk_cmd_urls_{session_id}"),
                ],
                [
                    InlineKeyboardButton("🛠️ تفكيك (Decompile)", callback_data=f"apk_cmd_decompile_{session_id}"),
                    InlineKeyboardButton("🛡️ الصلاحيات (Perms)", callback_data=f"apk_cmd_perms_{session_id}"),
                ],
                [
                    InlineKeyboardButton("🔓 فك التشفير (Decrypt)", callback_data=f"apk_cmd_decrypt_{session_id}"),
                    InlineKeyboardButton("📜 الشهادة (Cert)", callback_data=f"apk_cmd_cert_{session_id}"),
                ],
                [
                    InlineKeyboardButton("🎬 الأنشطة (Activities)", callback_data=f"apk_cmd_activities_{session_id}"),
                    InlineKeyboardButton("🖼️ الموارد (Resources)", callback_data=f"apk_cmd_resources_{session_id}"),
                ],
                [
                    InlineKeyboardButton("📚 المكتبات (Libs)", callback_data=f"apk_cmd_libs_{session_id}"),
                    InlineKeyboardButton("🛡️ الحماية (Protection)", callback_data=f"apk_cmd_protection_{session_id}"),
                ],
                [
                    InlineKeyboardButton("🛠️ إعادة بناء (Build)", callback_data=f"apk_cmd_build_{session_id}"),
                    InlineKeyboardButton("📋 تقرير (Report)", callback_data=f"apk_cmd_report_{session_id}"),
                ],
                [
                    InlineKeyboardButton("🔥 تحليل كامل (Full)", callback_data=f"apk_cmd_full_{session_id}"),
                ],
                [
                    InlineKeyboardButton("🎨📛 تعديل الهوية (Edit Icon & Name)", callback_data=f"apk_cmd_editall_{session_id}"),
                    InlineKeyboardButton("🔐 توقيع APK (Sign)", callback_data=f"apk_cmd_sign_{session_id}"),
                ],
                [
                    InlineKeyboardButton("🔓 كسر SSL (Bypass SSL)", callback_data=f"apk_cmd_ssl_{session_id}"),
                    InlineKeyboardButton("💬 نص عند الفتح (Splash)", callback_data=f"apk_cmd_splash_{session_id}"),
                ],
                [
                    InlineKeyboardButton("📥 تحميل من رابط", callback_data=f"apk_cmd_loadurl_{session_id}"),
                    InlineKeyboardButton("❌ إلغاء وحذف", callback_data=f"apk_cmd_cancel_{session_id}"),
                ]
            ]
            await msg.edit_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
            
    except Exception as e:
        await msg.edit_text(f"❌ خطأ في التحميل:\n`{str(e)[:200]}`", parse_mode='Markdown')

def main():
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN غير موجود!")
        print("يرجى إضافة التوكن في متغيرات البيئة")
        return
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    app.add_handler(CommandHandler("phone", phone_command))
    app.add_handler(CommandHandler("whatsapp", whatsapp_command))
    app.add_handler(CommandHandler("verify", verify_command))
    app.add_handler(CommandHandler("ignorant", ignorant_command))
    app.add_handler(CommandHandler("reputation", reputation_command))
    
    app.add_handler(CommandHandler("email", email_command))
    app.add_handler(CommandHandler("holehe", holehe_command))
    app.add_handler(CommandHandler("breach", breach_command))
    app.add_handler(CommandHandler("domain", domain_command))
    
    app.add_handler(CommandHandler("download", download_command))
    
    app.add_handler(CommandHandler("username", username_command))
    app.add_handler(CommandHandler("similar", similar_command))
    app.add_handler(CommandHandler("facebook", facebook_command))
    app.add_handler(CommandHandler("instagram", instagram_command))
    app.add_handler(CommandHandler("xhistory", xhistory_command))
    
    app.add_handler(CommandHandler("btc", btc_command))
    app.add_handler(CommandHandler("ton", ton_command))
    app.add_handler(CommandHandler("tontx", tontx_command))
    app.add_handler(CommandHandler("eth", eth_command))
    app.add_handler(CommandHandler("usdt", usdt_command))
    app.add_handler(CommandHandler("wallet", wallet_command))
    app.add_handler(CommandHandler("prices", prices_command))
    
    app.add_handler(CommandHandler("nid", nid_command))
    
    app.add_handler(CommandHandler("cloudflare", cloudflare_command))
    app.add_handler(CommandHandler("exploits", exploits_command))
    
    app.add_handler(CommandHandler("ghunt", ghunt_command))
    app.add_handler(CommandHandler("youtube", youtube_command))
    app.add_handler(CommandHandler("gdrive", gdrive_command))
    app.add_handler(CommandHandler("wifi", wifi_command))
    app.add_handler(CommandHandler("dork", dork_command))
    
    app.add_handler(CommandHandler("wayback", wayback_command))
    app.add_handler(CommandHandler("ip", ip_command))
    app.add_handler(CommandHandler("dns", dns_command))
    app.add_handler(CommandHandler("whois", whois_command))
    app.add_handler(CommandHandler("subdomains", subdomains_command))
    app.add_handler(CommandHandler("headers", headers_command))
    app.add_handler(CommandHandler("links", links_command))
    app.add_handler(CommandHandler("tech", tech_command))
    app.add_handler(CommandHandler("robots", robots_command))
    
    app.add_handler(CommandHandler("scan", scan_command))
    app.add_handler(CommandHandler("sqli", sqli_command))
    app.add_handler(CommandHandler("xss", xss_command))
    app.add_handler(CommandHandler("lfi", lfi_command))
    app.add_handler(CommandHandler("redirect", redirect_command))
    app.add_handler(CommandHandler("cmdi", cmdi_command))
    app.add_handler(CommandHandler("secheaders", secheaders_command))
    app.add_handler(CommandHandler("cors", cors_command))
    app.add_handler(CommandHandler("dirscan", dirscan_command))
    app.add_handler(CommandHandler("portscan", portscan_command))
    app.add_handler(CommandHandler("waf", waf_command))
    
    app.add_handler(CommandHandler("nmap", nmap_command))
    app.add_handler(CommandHandler("nmapagg", nmap_aggressive_command))
    app.add_handler(CommandHandler("nmapsvc", nmap_svc_command))
    app.add_handler(CommandHandler("nmapvuln", nmap_vuln_command))
    app.add_handler(CommandHandler("nmapbrute", nmap_brute_command))
    app.add_handler(CommandHandler("nmapdisc", nmap_disc_command))
    app.add_handler(CommandHandler("nmapfull", nmap_full_command))
    
    app.add_handler(CommandHandler("sqlmap", sqlmap_command))
    app.add_handler(CommandHandler("sqlmapdeep", sqlmap_deep_command))
    app.add_handler(CommandHandler("sqlmapdbs", sqlmap_dbs_command))
    app.add_handler(CommandHandler("sqlmaptables", sqlmap_tables_command))
    app.add_handler(CommandHandler("sqlmapcolumns", sqlmap_columns_command))
    app.add_handler(CommandHandler("sqlmapdump", sqlmap_dump_command))
    app.add_handler(CommandHandler("sqlmapshell", sqlmap_shell_command))
    
    app.add_handler(CommandHandler("shodan", shodan_command))
    
    app.add_handler(CommandHandler("darkweb", darkweb_command))
    app.add_handler(CommandHandler("censys", censys_command))
    
    app.add_handler(CommandHandler("apktool", apktool_command))
    app.add_handler(CommandHandler("apkinfo", apkinfo_command))
    app.add_handler(CommandHandler("apkmanifest", apkmanifest_command))
    app.add_handler(CommandHandler("apkpermissions", apkpermissions_command))
    app.add_handler(CommandHandler("apksecrets", apksecrets_command))
    app.add_handler(CommandHandler("apkurls", apkurls_command))
    app.add_handler(CommandHandler("apkdecompile", apkdecompile_command))
    app.add_handler(CommandHandler("apkdecrypt", apkdecrypt_command))
    app.add_handler(CommandHandler("apkcert", apkcert_command))
    app.add_handler(CommandHandler("apkfull", apkfull_command))
    app.add_handler(CommandHandler("apkurl", apkurl_command))

    app.add_handler(CommandHandler("exif", handle_photo))
    app.add_handler(CommandHandler("imgsearch", lambda u, c: (asyncio.create_task(USER_STATES.update({u.effective_user.id: "imgsearch"}) or u.message.reply_text("🔍 أرسل الصورة الآن للبحث عنها عكسياً."))) if asyncio.iscoroutinefunction(u.message.reply_text) else (USER_STATES.update({u.effective_user.id: "imgsearch"}) or asyncio.run(u.message.reply_text("🔍 أرسل الصورة الآن للبحث عنها عكسياً.")))))
    app.add_handler(CommandHandler("doh", doh_command))
    app.add_handler(CommandHandler("ipgeo", ip_geo_command))
    app.add_handler(CommandHandler("httpsec", httpsec_command))
    app.add_handler(CommandHandler("unshort", unshort_command))
    
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("addchannel", add_channel))
    app.add_handler(CommandHandler("removechannel", remove_channel))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("stats", get_stats_command))
    
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(apk_callback_handler, pattern="^apk_cmd_"))
    app.add_handler(CallbackQueryHandler(splash_callback_handler, pattern="^splash_"))
    
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    app.add_handler(CommandHandler("dnsrecords", dnsrecords_command))
    app.add_handler(CommandHandler("sslexpiry", sslexpiry_command))
    app.add_handler(CommandHandler("serverinfo", serverinfo_command))
    app.add_handler(CommandHandler("reverseip", reverseip_command))
    app.add_handler(CommandHandler("cdn", cdn_command))
    app.add_handler(CommandHandler("techstack", techstack_command))
    app.add_handler(CommandHandler("cmsdetect", cmsdetect_command))
    app.add_handler(CommandHandler("subenum", subenum_command))
    app.add_handler(CommandHandler("openports", openports_command))
    app.add_handler(CommandHandler("adminfinder", adminfinder_command))
    app.add_handler(CommandHandler("dirfinder", dirfinder_command))
    app.add_handler(CommandHandler("sensitivefiles", sensitivefiles_command))
    app.add_handler(CommandHandler("banner", banner_command))
    app.add_handler(CommandHandler("emailextract", emailextract_command))
    app.add_handler(CommandHandler("phoneextract", phoneextract_command))
    app.add_handler(CommandHandler("sitemap", sitemap_command))
    app.add_handler(CommandHandler("securitytxt", securitytxt_command))
    app.add_handler(CommandHandler("md5", md5_command))
    app.add_handler(CommandHandler("md5decode", md5decode_command))
    app.add_handler(CommandHandler("reversedns", reversedns_command))
    
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🚀 البوت يعمل الآن...")
    print("✅ OSINT Hunter Bot V5.0 جاهز!")
    print("🔥 أدوات جديدة: /holehe, /download")
    print("📧 Holehe Only Used: /holehe test@gmail.com")
    print("🔽 تنزيل المواقع: /download https://example.com")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
